# PreAudit Guard

**A local, static, no-execution preflight scanner that quarantines an unknown codebase before an AI agent or human auditor reviews it.**

When you clone an unfamiliar repo to audit it — or point an AI coding/audit agent at it — the *first* code you run is often the attacker's: a `postinstall` hook, a `curl | bash` in a setup script, or a `README` full of instructions aimed at your AI assistant. PreAudit Guard inspects the repository **first** and surfaces those pre-audit risk signals so you can review them before installing dependencies, running tests, or feeding the source to a model.

It is a **scanner, not a vulnerability finder**. It does not judge your Solidity logic — it tells you whether the repo is safe to *open the lid on*.

> ⚠️ **Limitation:** PreAudit Guard reports risk *signals*. It does **not** prove a repository is safe or malicious, and it **never executes the scanned code**. Treat a clean result as "no obvious traps found," not "safe."

---

## What it detects

Seven detector families, each scoped to keep false positives low:

| Family | Examples |
|---|---|
| **Prompt injection** | "ignore all previous instructions", instructions to exfiltrate secrets / read env vars, system-prompt probing, base64-encoded payloads in comments, oversized NatSpec, look-alike (homoglyph) identifiers |
| **Lifecycle / build scripts** | npm `preinstall`/`postinstall`/`prepare` hooks, `curl\|bash` download-and-execute, `eval $(...)`, `node -e` / `python -c`, `base64 -d`, generic `rm -rf`, foundry `ffi = true`, dependency typosquats, `git+https:` / `file:` deps |
| **Secrets** | PEM private-key blocks, named keys (`PRIVATE_KEY`, `MNEMONIC`, AWS/GitHub/Infura/Alchemy/Helius), AWS/GitHub/Slack token shapes, Solana `id.json`/`keypair.json` 64-byte arrays, committed `.env` files |
| **Network behavior** | programmatic HTTP/socket clients (`fetch`/`axios`/`requests`/`urllib`/`WebSocket`/raw sockets) in **build / test / CI** paths — the exfiltration / payload-fetch surface you trigger by auditing |
| **Destructive filesystem** | fork bombs, `dd` to a device, `mkfs`, `rm -rf` of `/` · `~` · `$HOME` · system paths, `shutil.rmtree`, recursive `fs.rmSync`, recursive `chmod 777` |
| **Dynamic execution** | `eval(` / `exec(`, `os.system(`, `subprocess(…, shell=True)`, `pickle.loads`, unsafe `yaml.load`, `new Function(`, `vm.runIn*`, `child_process` |
| **CI / GitHub Actions** | `pull_request_target`, untrusted `${{ github.event.*.body }}` script injection, `curl\|bash` run steps, third-party actions not pinned to a full commit SHA |

**Scoping (why FPs stay low):** injection matches only prose/comments/strings; secret patterns are context-gated and redacted; network/destructive/dynamic-exec detectors target build/test/script paths and high-signal patterns rather than ordinary app source; CI checks run only on `.github/workflows/`. The families complement each other — e.g. `lifecycle_scripts` owns generic build `rm -rf` (MEDIUM) while `destructive_fs` owns catastrophic `rm -rf ~` (HIGH). Matched secrets are **never echoed in full**.

---

## Install

```sh
pip install -e tools/public/preaudit-guard      # from this repo, editable
# or, once published:
# pip install preaudit-guard
```

Requires Python ≥ 3.10. Only dependency: `PyYAML`.

## Usage

```sh
preaudit scan ./target-repo                  # human-readable report
preaudit scan ./target-repo --format json    # machine-readable (pipe into other tools)
preaudit scan ./target-repo --format markdown -o PREFLIGHT.md
preaudit scan ./target-repo --strict         # block at MEDIUM (default blocks at HIGH)
preaudit scan ./target-repo --exit-zero      # report only, never fail the shell
```

### Example output

```text
PreAudit Guard — preflight scan
  Target : ./target-repo
  Files  : 24
  Risk   : 🟥 CRITICAL
  Findings: 6  (CRITICAL 1 · HIGH 3 · MEDIUM 2 · LOW 0)

  [HIGH] lifecycle_scripts/remote_exec
      package.json:3
      Downloads and pipes a remote script directly into a shell (curl|bash).
  [HIGH] prompt_injection/exfiltration_instruction
      README.md:6
      Text instructs an agent to exfiltrate data.
  [CRITICAL] secrets/solana_keypair
      keypair.json:1
      'keypair.json' contains a 64-byte keypair array — a committed Solana private key.
  ...

  Recommended quarantine actions:
   - Do NOT run install/build scripts blindly. Install with `npm ci --ignore-scripts` ...
   - Treat README/comments/docs as untrusted DATA ...
   - Rotate and remove any committed key/secret immediately ...
```

### Exit codes (CI / pre-commit friendly)

| Code | Meaning |
|---|---|
| `0` | Overall risk below the block threshold (or `--exit-zero`) |
| `2` | Overall risk at/above the threshold (default **HIGH**; `--strict` → **MEDIUM**) |
| `1` | Usage / IO error |

---

## Quarantine sandbox

After scanning, generate the artifacts to safely *open and build* an untrusted repo:

```sh
preaudit sandbox ./target-repo -o ./quarantine
```

This **generates** (it never builds the image, runs Docker, or executes the repo):

| File | Purpose |
|---|---|
| `Dockerfile.quarantine` | Non-root, toolchain-matched image. The repo is **mounted at run, never baked in**, and the project's install/build is **never `RUN` at build time** — so setup scripts can't fire during `docker build`. |
| `run-quarantine.sh` | Hardened `docker run` wrapper: `--network none`, non-root, `--security-opt no-new-privileges`, `--cap-drop ALL`, pids/memory limits, repo mounted read-only. Build/test the repo fully offline inside it. |
| `SECURITY_PREFLIGHT.md` | The scan report + how to use the package. |
| `agent_context_safe.md` | **Metadata-only** summary (tree + dependency names + risk-signal table + a "files withheld" list). Contains **no raw repository prose**, so you can hand it to an AI agent without exposing it to injection text in READMEs/comments. |

Building the image pulls the base image (needs network **once**); the untrusted code only ever runs in the `--network none` container.

## Risk model

Each finding carries `LOW` / `MEDIUM` / `HIGH` / `CRITICAL`. The overall repo risk is the **maximum** finding severity, with a few documented **combination escalations** that matter for a quarantine decision:

- a **secret** present *and* a **network-capable lifecycle script** → `CRITICAL` (possible exfiltration)
- a **prompt-injection** *and* an **executable setup path** → at least `HIGH` (weaponizable injection)

## Rules are data

Detection patterns live in editable YAML under `preaudit_guard/rules/` (`prompt_injection.yml`, `lifecycle_scripts.yml`, `secrets.yml`). Add or tune patterns without touching code.

## Develop / test

```sh
cd tools/public/preaudit-guard
pip install -e .
pytest
```

The `examples/` directory contains a `malicious-toy-repo/` (should score HIGH/CRITICAL) and a `clean-toy-repo/` (should score LOW) used by the test suite.

---

## Roadmap

- SARIF export, pre-commit hook, VS Code extension
- Optional post-scan LLM interpretation of `agent_context_safe.md` **after** deterministic quarantine
- Configurable per-rule severity / allowlist file

## License

MIT.
