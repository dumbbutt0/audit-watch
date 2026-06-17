#!/usr/bin/env python3
"""
update_session.py — CLI wrapper for write_session() in audit_context.py.

Called by run_pipeline.sh after each step to keep session.json current.

Usage:
    python scripts/update_session.py --step "1.5"
    python scripts/update_session.py --step "4" --count 12
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import write_session

parser = argparse.ArgumentParser(description="Update active audit session.json")
parser.add_argument("--step",  required=True, help="Pipeline step label (e.g. '0.5', '1.5', '3.8')")
parser.add_argument("--count", type=int, default=None, help="findings_count to record")
args = parser.parse_args()

updates: dict = {"active_step": args.step}
if args.count is not None:
    updates["findings_count"] = args.count

write_session(updates)

msg = f"[session] active_step={args.step}"
if args.count is not None:
    msg += f"  findings_count={args.count}"
print(msg)
