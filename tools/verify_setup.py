#!/usr/bin/env python3
"""
verify_setup.py

Pre-flight check. Run this after setup to confirm everything is ready.

Usage:
    python tools/verify_setup.py
"""

import json
import subprocess
import sys
from pathlib import Path

import urllib.request
import urllib.error

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
try:
    from audit_context import audit_path, get_active_audit, get_audit_meta, _AUDITS_DIR, _CONFIG_DIR
    _HAS_AUDIT_CTX = True
except ImportError:
    _HAS_AUDIT_CTX = False


def check(label: str, ok: bool, detail: str = ""):
    icon = "✓" if ok else "✗"
    line = f"  {icon} {label}"
    if detail:
        line += f" — {detail}"
    print(line)
    return ok


def main():
    # Print active audit at the top
    if _HAS_AUDIT_CTX:
        active = get_active_audit()
        if active.get("audit_id"):
            meta = get_audit_meta()
            print(f"Active audit: {meta.get('name', active['audit_id'])} ({active['audit_id']})")
        else:
            print("Active audit: (none — run python scripts/migrate_to_audit.py)")
    print("Smart Contract Auditor — pre-flight checks\n")
    all_ok = True

    # 1. Chroma DB
    try:
        import chromadb
        kb_path = Path("kb/chroma")
        if kb_path.exists():
            client = chromadb.PersistentClient(path=str(kb_path))
            try:
                col = client.get_collection("solodit_findings")
                count = col.count()
                all_ok &= check("Chroma DB", count > 0, f"{count} findings indexed")
                if count == 0:
                    print("    → Run: python scripts/solodit_scraper.py")
            except Exception:
                all_ok &= check("Chroma DB", False, "collection not found — run scraper")
                print("    → Run: python scripts/solodit_scraper.py")
        else:
            all_ok &= check("Chroma DB", False, "kb/ directory not found — run scraper")
            print("    → Run: python scripts/solodit_scraper.py")
    except ImportError:
        all_ok &= check("Chroma DB", False, "chromadb not installed")
        print("    → Run: pip install chromadb")

    # 1b. Immunefi MCP reachability (non-fatal — audit proceeds without it)
    IMMUNEFI_MCP = "https://reports.immunefi.com/~gitbook/mcp"
    try:
        req = urllib.request.Request(
            IMMUNEFI_MCP,
            data=b'{"jsonrpc":"2.0","id":0,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"verify_setup","version":"1.0.0"}}}',
            headers={"Content-Type": "application/json", "Accept": "application/json, text/event-stream"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            reachable = r.status < 500
    except Exception:
        reachable = False
    if reachable:
        check("Immunefi MCP", True, "reachable — bounty precedents available")
    else:
        # Non-fatal: print warning but don't count against all_ok
        check("Immunefi MCP", False, "unreachable — offline mode, no bounty precedents")
        print("    → Agents will still run using Solodit DB only")

    # 2. Sentence transformers
    try:
        from sentence_transformers import SentenceTransformer
        all_ok &= check("Embedding model", True, "sentence-transformers available")
    except ImportError:
        all_ok &= check("Embedding model", False, "not installed")
        print("    → Run: pip install sentence-transformers")

    # 3. slither
    result = subprocess.run(["slither", "--version"], capture_output=True, text=True)
    if result.returncode == 0:
        version = result.stdout.strip() or result.stderr.strip()
        all_ok &= check("slither", True, version[:40])
    else:
        all_ok &= check("slither", False, "not found")
        print("    → Run: pip install slither-analyzer")

    # 4. solc (optional for Rust/Soroban audits)
    try:
        result = subprocess.run(["solc", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.split("\n")[1].strip() if "\n" in result.stdout else result.stdout.strip()
            all_ok &= check("solc", True, version[:40])
        else:
            all_ok &= check("solc", False, "not found")
            print("    → Run: pip install solc-select && solc-select install auto && solc-select use latest")
    except FileNotFoundError:
        all_ok &= check("solc", False, "not installed (optional for Rust/Soroban audits)")
        print("    → Run: pip install solc-select && solc-select install auto && solc-select use latest")

    # 5. Schema file
    schema_path = Path("schema/findings_schema.json")
    if schema_path.exists():
        try:
            with open(schema_path) as f:
                schema = json.load(f)
            all_ok &= check("Findings schema", True, "schema/findings_schema.json valid")
        except json.JSONDecodeError:
            all_ok &= check("Findings schema", False, "JSON parse error")
    else:
        all_ok &= check("Findings schema", False, "schema/findings_schema.json missing")

    # 6. Agent spec files
    agent_specs = [
        "agents/reentrancy.md",
        "agents/access_control.md",
        "agents/arithmetic.md",
        "agents/oracle.md",
        "agents/flash_loan.md",
        "agents/logic.md",
        "agents/protocol_context.md",
        "agents/report_synthesis.md",
        "agents/dos.md",
        "agents/snapshot.md",
    ]
    missing = [s for s in agent_specs if not Path(s).exists()]
    if missing:
        all_ok &= check("Agent specs", False, f"missing: {', '.join(missing)}")
    else:
        all_ok &= check("Agent specs", True, f"all {len(agent_specs)} specs present")

    # 6b. Triage scripts
    triage_scripts = [
        "scripts/triage_findings.py",
        "scripts/build_poc_queue.py",
        "scripts/final_submission_pack.py",
    ]
    missing_scripts = [s for s in triage_scripts if not Path(s).exists()]
    if missing_scripts:
        all_ok &= check("Triage scripts", False, f"missing: {', '.join(missing_scripts)}")
    else:
        all_ok &= check("Triage scripts", True, f"all {len(triage_scripts)} triage scripts present")

    # 6c. Triager prompt
    triager_prompt = Path("prompts/triager.md")
    all_ok &= check("Triager prompt", triager_prompt.exists(), "prompts/triager.md")
    if not triager_prompt.exists():
        print("    → Missing prompts/triager.md — triage will not run")

    # 6d. Triage schema
    triage_schema_path = Path("schemas/triage.schema.json")
    if triage_schema_path.exists():
        try:
            json.loads(triage_schema_path.read_text())
            all_ok &= check("Triage schema", True, "schemas/triage.schema.json valid")
        except json.JSONDecodeError:
            all_ok &= check("Triage schema", False, "schemas/triage.schema.json — JSON parse error")
    else:
        all_ok &= check("Triage schema", False, "schemas/triage.schema.json missing")

    # 6e. data/triage directory
    if _HAS_AUDIT_CTX and get_active_audit().get("audit_id"):
        triage_dir = audit_path("data/triage")
        all_ok &= check("Triage output dir", True, f"{triage_dir} ready")
    else:
        Path("data/triage").mkdir(parents=True, exist_ok=True)
        all_ok &= check("Triage output dir", True, "data/triage/ ready")

    # 6f. Specialist review agent specs
    specialist_agents = [
        "agents/exploitability_modeler.md",
        "agents/runtime_poc_agent.md",
        "agents/judge_simulator.md",
        "agents/duplicate_risk_agent.md",
        "agents/severity_calibrator.md",
    ]
    missing_sa = [s for s in specialist_agents if not Path(s).exists()]
    if missing_sa:
        all_ok &= check("Specialist agent specs", False, f"missing: {', '.join(missing_sa)}")
    else:
        all_ok &= check("Specialist agent specs", True, f"all {len(specialist_agents)} present")

    # 6g. Specialist prompts
    specialist_prompts = [
        "prompts/exploitability_modeler.md",
        "prompts/runtime_poc_executor.md",
        "prompts/judge_simulator.md",
        "prompts/duplicate_risk.md",
        "prompts/severity_calibrator.md",
    ]
    missing_sp = [s for s in specialist_prompts if not Path(s).exists()]
    if missing_sp:
        all_ok &= check("Specialist prompts", False, f"missing: {', '.join(missing_sp)}")
    else:
        all_ok &= check("Specialist prompts", True, f"all {len(specialist_prompts)} present")

    # 6h. Specialist schemas
    specialist_schemas = [
        "schemas/exploitability.schema.json",
        "schemas/runtime_poc.schema.json",
        "schemas/judge_simulation.schema.json",
        "schemas/duplicate_risk.schema.json",
        "schemas/severity_calibration.schema.json",
        "schemas/severity_learning_record.schema.json",
    ]
    bad_spec_schemas = []
    for sp in specialist_schemas:
        p = Path(sp)
        if not p.exists():
            bad_spec_schemas.append(f"{sp} (missing)")
        else:
            try:
                json.loads(p.read_text())
            except json.JSONDecodeError:
                bad_spec_schemas.append(f"{sp} (invalid JSON)")
    if bad_spec_schemas:
        all_ok &= check("Specialist schemas", False, "; ".join(bad_spec_schemas))
    else:
        all_ok &= check("Specialist schemas", True, f"all {len(specialist_schemas)} valid")

    # 6i. Specialist scripts
    specialist_scripts = [
        "scripts/model_exploitability.py",
        "scripts/run_integrated_poc.py",
        "scripts/judge_simulate.py",
        "scripts/estimate_duplicate_risk.py",
        "scripts/calibrate_severity.py",
        "scripts/ingest_judging_results.py",
        "scripts/run_specialist_review.py",
    ]
    missing_ss = [s for s in specialist_scripts if not Path(s).exists()]
    if missing_ss:
        all_ok &= check("Specialist scripts", False, f"missing: {', '.join(missing_ss)}")
    else:
        all_ok &= check("Specialist scripts", True, f"all {len(specialist_scripts)} present")

    # 6j. Specialist data directories
    spec_data_dirs = [
        "data/exploitability",
        "data/runtime_poc",
        "data/judge_simulation",
        "data/duplicates",
        "data/learning",
        "data/severity",
    ]
    if _HAS_AUDIT_CTX and get_active_audit().get("audit_id"):
        for d in spec_data_dirs:
            audit_path(d)
    else:
        for d in spec_data_dirs:
            Path(d).mkdir(parents=True, exist_ok=True)
    all_ok &= check("Specialist data dirs", True,
                    f"{len(spec_data_dirs)} dirs ready")

    # 6k. severity_rules.yaml
    rules_path = Path("data/learning/severity_rules.yaml")
    if rules_path.exists():
        try:
            import yaml
            yaml.safe_load(rules_path.read_text())
            all_ok &= check("Severity rules YAML", True, "data/learning/severity_rules.yaml valid")
        except ImportError:
            # pyyaml not installed — check file exists at least
            all_ok &= check("Severity rules YAML", True,
                            "data/learning/severity_rules.yaml present (pyyaml not installed for parse check)")
        except Exception as e:
            all_ok &= check("Severity rules YAML", False, f"YAML parse error: {e}")
    else:
        all_ok &= check("Severity rules YAML", False, "data/learning/severity_rules.yaml missing")

    # 6l. run_specialist_review.py executable
    review_script = Path("scripts/run_specialist_review.py")
    all_ok &= check("run_specialist_review.py", review_script.exists(),
                    "scripts/run_specialist_review.py")

    # 6n. PoC generator scripts
    poc_scripts = [
        "scripts/profile_target_repo.py",
        "scripts/generate_poc_plan.py",
        "scripts/generate_poc_test.py",
        "scripts/run_poc_tests.py",
        "scripts/summarize_poc_results.py",
    ]
    missing_poc = [s for s in poc_scripts if not Path(s).exists()]
    if missing_poc:
        all_ok &= check("PoC scripts", False, f"missing: {', '.join(missing_poc)}")
    else:
        all_ok &= check("PoC scripts", True, f"all {len(poc_scripts)} PoC scripts present")

    # 6o. PoC prompts
    poc_prompts = [
        "prompts/poc_planner.md",
        "prompts/poc_writer.md",
        "prompts/poc_reviewer.md",
    ]
    missing_prompts = [p for p in poc_prompts if not Path(p).exists()]
    if missing_prompts:
        all_ok &= check("PoC prompts", False, f"missing: {', '.join(missing_prompts)}")
    else:
        all_ok &= check("PoC prompts", True, f"all {len(poc_prompts)} PoC prompts present")

    # 6p. PoC schemas
    poc_schemas = [
        "schemas/poc_queue.schema.json",
        "schemas/poc_plan.schema.json",
        "schemas/poc_result.schema.json",
    ]
    bad_schemas = []
    for sp in poc_schemas:
        p = Path(sp)
        if not p.exists():
            bad_schemas.append(f"{sp} (missing)")
        else:
            try:
                json.loads(p.read_text())
            except json.JSONDecodeError:
                bad_schemas.append(f"{sp} (invalid JSON)")
    if bad_schemas:
        all_ok &= check("PoC schemas", False, "; ".join(bad_schemas))
    else:
        all_ok &= check("PoC schemas", True, f"all {len(poc_schemas)} PoC schemas valid")

    # 6q. PoC output directories
    if _HAS_AUDIT_CTX and get_active_audit().get("audit_id"):
        audit_path("data/poc_queue")
        audit_path("pocs/k2")
        audit_path("reports")
        all_ok &= check("PoC output dirs", True, "audit data/poc_queue/, pocs/k2/, reports/ ready")
    else:
        Path("data/poc_queue").mkdir(parents=True, exist_ok=True)
        Path("pocs/k2").mkdir(parents=True, exist_ok=True)
        Path("reports").mkdir(parents=True, exist_ok=True)
        all_ok &= check("PoC output dirs", True, "data/poc_queue/, pocs/k2/, reports/ ready")

    # 6r. cargo available (needed to run PoC tests)
    cargo_result = subprocess.run(["cargo", "--version"], capture_output=True, text=True)
    if cargo_result.returncode == 0:
        all_ok &= check("cargo", True, cargo_result.stdout.strip()[:40])
    else:
        all_ok &= check("cargo", False, "not found — PoC tests won't run")
        print("    → Install Rust: https://rustup.rs")

    # 6s. Deep invariant analysis agent specs
    deep_agent_specs = [
        "agents/invariant_extractor.md",
        "agents/interaction_mapper.md",
        "agents/deep_trace_agent.md",
    ]
    missing_da = [s for s in deep_agent_specs if not Path(s).exists()]
    if missing_da:
        all_ok &= check("Deep analysis agent specs", False, f"missing: {', '.join(missing_da)}")
    else:
        all_ok &= check("Deep analysis agent specs", True, f"all {len(deep_agent_specs)} present")

    # 6t. Deep analysis prompts
    deep_prompts = [
        "prompts/invariant_extractor.md",
        "prompts/interaction_mapper.md",
        "prompts/deep_trace.md",
    ]
    missing_dp = [p for p in deep_prompts if not Path(p).exists()]
    if missing_dp:
        all_ok &= check("Deep analysis prompts", False, f"missing: {', '.join(missing_dp)}")
    else:
        all_ok &= check("Deep analysis prompts", True, f"all {len(deep_prompts)} present")

    # 6u. Deep analysis schemas
    deep_schemas = [
        "schemas/invariants.schema.json",
        "schemas/call_graph.schema.json",
        "schemas/thread.schema.json",
    ]
    bad_da_schemas = []
    for sp in deep_schemas:
        p = Path(sp)
        if not p.exists():
            bad_da_schemas.append(f"{sp} (missing)")
        else:
            try:
                json.loads(p.read_text())
            except json.JSONDecodeError:
                bad_da_schemas.append(f"{sp} (invalid JSON)")
    if bad_da_schemas:
        all_ok &= check("Deep analysis schemas", False, "; ".join(bad_da_schemas))
    else:
        all_ok &= check("Deep analysis schemas", True, f"all {len(deep_schemas)} valid")

    # 6v. Deep analysis scripts
    deep_scripts = [
        "scripts/extract_invariants.py",
        "scripts/map_interactions.py",
        "scripts/deep_trace.py",
        "scripts/escalate_threads.py",
        "scripts/run_deep_analysis.py",
    ]
    missing_ds = [s for s in deep_scripts if not Path(s).exists()]
    if missing_ds:
        all_ok &= check("Deep analysis scripts", False, f"missing: {', '.join(missing_ds)}")
    else:
        all_ok &= check("Deep analysis scripts", True, f"all {len(deep_scripts)} present")

    # 6w. Deep analysis data directories
    deep_data_dirs = ["data/invariants", "data/interactions", "data/threads"]
    if _HAS_AUDIT_CTX and get_active_audit().get("audit_id"):
        for d in deep_data_dirs:
            audit_path(d)
    else:
        for d in deep_data_dirs:
            Path(d).mkdir(parents=True, exist_ok=True)
    all_ok &= check("Deep analysis data dirs", True,
                    f"{len(deep_data_dirs)} dirs ready (invariants, interactions, threads)")

    # 7. Output directory
    if _HAS_AUDIT_CTX and get_active_audit().get("audit_id"):
        out_dir = audit_path("output")
        all_ok &= check("Output directory", True, f"{out_dir} ready")
    else:
        Path("output").mkdir(exist_ok=True)
        all_ok &= check("Output directory", True, "output/ ready")

    # 8. Multi-audit infrastructure
    if _HAS_AUDIT_CTX:
        config_dir = _CONFIG_DIR
        audits_dir = _AUDITS_DIR
        active = get_active_audit()
        registry_path = audits_dir / "registry.json"
        active_file = config_dir / "active_audit.json"

        all_ok &= check("audit_context.py", True, "scripts/audit_context.py present")
        all_ok &= check("config/ directory", config_dir.exists(), str(config_dir))
        all_ok &= check("audits/ directory", audits_dir.exists(), str(audits_dir))
        if registry_path.exists():
            try:
                json.loads(registry_path.read_text())
                all_ok &= check("audits/registry.json", True, "valid JSON")
            except json.JSONDecodeError:
                all_ok &= check("audits/registry.json", False, "invalid JSON")
        else:
            all_ok &= check("audits/registry.json", False, "missing")
        if active.get("audit_id"):
            workspace = audits_dir / active["audit_id"]
            meta = get_audit_meta()
            all_ok &= check("Active audit workspace", workspace.exists(),
                            f"{active['audit_id']} at {workspace}")
            all_ok &= check("Active audit meta.json",
                            (workspace / "meta.json").exists() if workspace.exists() else False,
                            meta.get("name", "?"))
        else:
            # Non-fatal: migration not yet run
            check("Active audit", False, "not set — run python scripts/migrate_to_audit.py")
            print("    → This is non-fatal for initial setup; run migration before auditing")
    else:
        all_ok &= check("audit_context.py", False, "scripts/audit_context.py missing")

    print()
    if all_ok:
        print("All checks passed. Ready to audit.")
        print("\nTo start an audit:")
        print("  → Tell Claude Code: 'Audit this contract: contracts/YourContract.sol'")
    else:
        print("Some checks failed. Fix the issues above before running an audit.")

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())


# Additional check appended — .env file and continuous mode hint
def check_env_file():
    env = Path(".env")
    if env.exists():
        keys = [l.split("=")[0] for l in env.read_text().splitlines() if "=" in l]
        print(f"  ✓ .env file found with keys: {', '.join(keys)}")
    else:
        print("  ℹ  No .env file — keys must be exported each session")
        print("    → Create one: echo 'SOLODIT_API_KEY=sk_...' > .env")
