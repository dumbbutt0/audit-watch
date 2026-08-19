"""Quarantine artifact generator for `preaudit sandbox`.

After the static scan, this GENERATES (never runs) the files needed to safely open
an untrusted repo:

  * Dockerfile.quarantine  — a non-root, build/test-capable image (repo is mounted
                             at run, never baked in; project setup is never RUN at build)
  * run-quarantine.sh      — a hardened `docker run` wrapper: --network none, non-root,
                             no-new-privileges, --cap-drop ALL, resource limits
  * SECURITY_PREFLIGHT.md   — the scan report + how to use the sandbox
  * agent_context_safe.md   — METADATA-ONLY summary (tree + deps + findings) safe to
                             hand an AI agent; contains NO raw repository prose

Safety invariant: this module performs pure file writes. It never executes the
target, invokes Docker, or touches the network.
"""

from __future__ import annotations

import json
import os
import re
import stat
from pathlib import Path

from .findings import ScanResult, Severity
from .report import render as render_report, DISCLAIMER
from .scanner import run_scan
from .walker import iter_text_files, SKIP_DIRS

DEFAULT_OUT_DIR = "preaudit-quarantine"
IMAGE_TAG = "preaudit-quarantine"

# ── ecosystem detection ───────────────────────────────────────────────────────

def _basenames(file_index: dict[str, str]) -> set[str]:
    return {Path(p).name for p in file_index}


def detect_ecosystems(file_index: dict[str, str]) -> list[str]:
    names = _basenames(file_index)
    exts = {Path(p).suffix.lower() for p in file_index}
    eco: list[str] = []
    if "package.json" in names:
        eco.append("node")
    if "pyproject.toml" in names or "requirements.txt" in names or "setup.py" in names:
        eco.append("python")
    if "Cargo.toml" in names:
        eco.append("rust")
    if "foundry.toml" in names or ".sol" in exts:
        eco.append("foundry")
    return eco


def pick_base_image(ecos: list[str]) -> tuple[str, str]:
    """Return (base_image, note). Single dominant ecosystem -> matching toolchain image."""
    mapping = {
        "node": "node:20-slim",
        "python": "python:3.12-slim",
        "rust": "rust:slim",
        "foundry": "ghcr.io/foundry-rs/foundry:latest",
    }
    if len(ecos) == 1:
        e = ecos[0]
        return mapping[e], f"Detected ecosystem: {e}."
    if not ecos:
        return "debian:stable-slim", "No toolchain manifest detected; using a generic base."
    # multiple — pick the first by a stable priority, note the rest
    priority = ["node", "python", "rust", "foundry"]
    chosen = next(e for e in priority if e in ecos)
    return mapping[chosen], (
        f"Multiple ecosystems detected ({', '.join(ecos)}); using the {chosen} base. "
        f"Add the other toolchains to Dockerfile.quarantine if you need them."
    )


# ── repo metadata (defanged) ──────────────────────────────────────────────────

_CTRL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def _defang(s: str, cap: int = 200) -> str:
    """Neutralize a repo-derived string for safe embedding in a doc handed to an agent.

    Collapses whitespace/newlines, strips control chars, escapes markdown table/code
    characters, and caps length. This prevents a crafted path or dependency name from
    smuggling a directive into agent_context_safe.md.
    """
    s = _CTRL_RE.sub("", s)
    s = re.sub(r"\s+", " ", s).strip()
    s = s.replace("`", "'").replace("|", "\\|")
    if len(s) > cap:
        s = s[:cap] + "…"
    return s


def build_tree(repo: Path, max_entries: int = 400) -> str:
    """A flat, sorted file listing (path + size), honoring the walker's skip dirs."""
    repo = repo.resolve()
    rows: list[tuple[str, int]] = []
    for dirpath, dirnames, filenames in os.walk(repo):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            p = Path(dirpath) / name
            try:
                size = p.stat().st_size
            except OSError:
                size = 0
            rows.append((os.path.relpath(p, repo), size))
    rows.sort(key=lambda r: r[0])
    total = len(rows)
    shown = rows[:max_entries]
    lines = [f"{_defang(rel, 160)}  ({size} B)" for rel, size in shown]
    if total > max_entries:
        lines.append(f"… and {total - max_entries} more files (truncated)")
    lines.append(f"\nTotal files (excluding vendored/build dirs): {total}")
    return "\n".join(lines)


def summarize_dependencies(file_index: dict[str, str]) -> str:
    """Best-effort dependency names/versions from common manifests (no execution)."""
    out: list[str] = []

    for path, text in file_index.items():
        bn = Path(path).name
        if bn == "package.json":
            try:
                data = json.loads(text)
            except Exception:
                continue
            for field in ("dependencies", "devDependencies"):
                deps = data.get(field, {})
                if isinstance(deps, dict) and deps:
                    items = ", ".join(_defang(f"{k}@{v}", 60) for k, v in list(deps.items())[:60])
                    out.append(f"- **node / {field}** ({_defang(path,80)}): {items}")
        elif bn.startswith("requirements") and bn.endswith(".txt"):
            pkgs = [ln.strip() for ln in text.splitlines() if ln.strip() and not ln.strip().startswith("#")]
            if pkgs:
                out.append(f"- **python / pip** ({_defang(path,80)}): "
                           + ", ".join(_defang(p, 60) for p in pkgs[:60]))
        elif bn == "pyproject.toml":
            quoted = re.findall(r'"([A-Za-z0-9_.\-]+(?:[<>=!~]=?[^"]+)?)"', text)
            if quoted:
                out.append(f"- **python / pyproject** ({_defang(path,80)}): "
                           + ", ".join(_defang(q, 60) for q in quoted[:40]))
        elif bn == "Cargo.toml":
            deps = _toml_dependency_names(text)
            if deps:
                out.append(f"- **rust / cargo** ({_defang(path,80)}): "
                           + ", ".join(_defang(d, 60) for d in deps[:60]))
        elif bn == "remappings.txt":
            lhs = [ln.split("=", 1)[0].strip() for ln in text.splitlines() if "=" in ln]
            if lhs:
                out.append(f"- **solidity / remappings** ({_defang(path,80)}): "
                           + ", ".join(_defang(x, 40) for x in lhs[:40]))

    return "\n".join(out) if out else "_No dependency manifests detected._"


def _toml_dependency_names(text: str) -> list[str]:
    """Names declared under any [*dependencies] table in a TOML file (line-based, no tomllib)."""
    names: list[str] = []
    in_deps = False
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("[") and s.endswith("]"):
            in_deps = s.rstrip("]").lstrip("[").endswith("dependencies")
            continue
        if in_deps:
            m = re.match(r'([A-Za-z0-9_.\-]+)\s*=', s)
            if m:
                names.append(m.group(1))
    return names


# ── renderers ─────────────────────────────────────────────────────────────────

def render_dockerfile(base: str, note: str) -> str:
    return f"""# Generated by PreAudit Guard — quarantine image for an UNTRUSTED repository.
# {note}
#
# This image deliberately does NOT run the project's install/build scripts at build
# time. The repo is mounted read-only at /src at RUN time and copied into a writable
# /work; you run any build/test yourself INSIDE the --network none container (see
# run-quarantine.sh). Building this image pulls the base image and needs network ONCE;
# the untrusted code is only ever executed offline.

FROM {base}

# non-root auditor user + writable workspace
RUN (useradd -m -u 1000 auditor || adduser -D -u 1000 auditor) \\
 && mkdir -p /work && chown -R 1000:1000 /work

# entrypoint: copy the read-only mounted repo into the writable workspace, then shell
RUN printf '%s\\n' \\
    '#!/usr/bin/env bash' \\
    'set -e' \\
    'if [ -d /src ]; then cp -r /src/. /work/ 2>/dev/null || true; fi' \\
    'cd /work' \\
    'exec "$@"' > /usr/local/bin/quarantine-entry \\
 && chmod +x /usr/local/bin/quarantine-entry

USER 1000:1000
WORKDIR /work
ENTRYPOINT ["/usr/local/bin/quarantine-entry"]
CMD ["bash"]
"""


def render_run_wrapper(repo_abspath: str, image_tag: str = IMAGE_TAG) -> str:
    repo = _defang(repo_abspath, 4096)
    return f"""#!/usr/bin/env bash
# Generated by PreAudit Guard. Build + enter a hardened, NETWORK-DENIED container to
# inspect/build/test an untrusted repository.
#
#   * `docker build` pulls the base image and needs network ONCE.
#   * The untrusted repo only ever EXECUTES inside the `--network none` container below,
#     as a non-root user with no new privileges and all capabilities dropped.
#   * The repo is mounted READ-ONLY at /src and copied into an in-memory /work, so the
#     container cannot modify your host copy.
#
# Inside the container, install with scripts DISABLED, e.g.:
#   npm ci --ignore-scripts   |   pip install --no-build-isolation -r requirements.txt
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="{repo}"
TAG="{image_tag}"

docker build -f "$HERE/Dockerfile.quarantine" -t "$TAG" "$HERE"

exec docker run --rm -it \\
  --network none \\
  --user 1000:1000 \\
  --security-opt no-new-privileges \\
  --cap-drop ALL \\
  --pids-limit 512 \\
  --memory 4g \\
  --tmpfs /work:rw,size=2g,mode=1777 \\
  -v "$REPO":/src:ro \\
  "$TAG"
"""


def render_preflight(result: ScanResult) -> str:
    body = render_report(result, "markdown")
    return f"""# Security Preflight — quarantine package

This directory was generated by **PreAudit Guard** for an untrusted repository. Review this
report, then use the generated container to open/build the repo safely.

## How to use this quarantine package
1. Read the risk report below and `agent_context_safe.md`.
2. Build + enter the network-denied sandbox: `./run-quarantine.sh`
3. Inside the container, install with scripts disabled (e.g. `npm ci --ignore-scripts`) and
   run the project's build/tests. Networking is off and you are a non-root user.
4. Only hand an AI agent `agent_context_safe.md` — never the raw repository — until you have
   reviewed the flagged files yourself.

---

{body}
"""


def render_agent_context(result: ScanResult, tree: str, deps: str) -> str:
    counts = result.counts()
    withheld = sorted({
        f.file for f in result.findings if f.detector == "prompt_injection"
    })
    withheld_block = (
        "\n".join(f"- `{_defang(w, 160)}` — contains prompt-injection signals; body withheld."
                  for w in withheld)
        if withheld else "_None._"
    )

    rows = []
    for f in result.findings:
        loc = _defang(f"{f.file}:{f.line}" if f.line else f.file, 120)
        rows.append(f"| {f.severity.label} | {f.detector}/{f.category} | `{loc}` | {_defang(f.message, 160)} |")
    findings_table = (
        "| Severity | Detector | Location | Signal |\n|---|---|---|---|\n" + "\n".join(rows)
        if rows else "_No risk signals detected._"
    )

    return f"""# Agent Context (SAFE)

> Generated by PreAudit Guard for `{_defang(result.root, 160)}`.
> **This file is safe to hand to an AI agent.** It contains ONLY structural metadata,
> dependency names, and tool-authored risk signals. It deliberately includes **no raw
> repository prose** (READMEs, comments, doc strings) — so attacker-controlled text in the
> repo cannot reach the agent through this summary. All embedded values are sanitized.

## Risk verdict
- **Overall risk:** {result.overall.label}
- **Findings:** {len(result.findings)} (CRITICAL {counts['CRITICAL']} · HIGH {counts['HIGH']} · MEDIUM {counts['MEDIUM']} · LOW {counts['LOW']})
- **Files scanned:** {result.files_scanned}

## Files withheld (do not request their raw contents without review)
{withheld_block}

## Dependencies (names/versions only)
{deps}

## Risk signals
{findings_table}

## Repository structure
```
{tree}
```

---
_{DISCLAIMER}_
"""


# ── orchestration ─────────────────────────────────────────────────────────────

def generate_sandbox(repo: str | Path, out_dir: str | Path | None = None) -> tuple[ScanResult, list[Path]]:
    """Run the scan and write the quarantine artifacts. Pure file writes — no execution."""
    repo_path = Path(repo).resolve()
    out = Path(out_dir) if out_dir else Path.cwd() / DEFAULT_OUT_DIR
    out.mkdir(parents=True, exist_ok=True)

    result = run_scan(repo_path)
    file_index = dict(iter_text_files(repo_path))

    ecos = detect_ecosystems(file_index)
    base, note = pick_base_image(ecos)
    tree = build_tree(repo_path)
    deps = summarize_dependencies(file_index)

    artifacts = {
        "SECURITY_PREFLIGHT.md": render_preflight(result),
        "Dockerfile.quarantine": render_dockerfile(base, note),
        "run-quarantine.sh": render_run_wrapper(str(repo_path)),
        "agent_context_safe.md": render_agent_context(result, tree, deps),
    }

    written: list[Path] = []
    for name, content in artifacts.items():
        p = out / name
        p.write_text(content, encoding="utf-8")
        if name.endswith(".sh"):
            p.chmod(p.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        written.append(p)

    return result, written
