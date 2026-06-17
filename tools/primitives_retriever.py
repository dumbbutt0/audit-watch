#!/usr/bin/env python3
"""
primitives_retriever.py — Query the attack primitives knowledge base.

Usage:
    python tools/primitives_retriever.py <category>               # by category
    python tools/primitives_retriever.py --compounds PRIM-001     # find compounds
    python tools/primitives_retriever.py --id PRIM-006            # single primitive
    python tools/primitives_retriever.py --all                    # all primitives
    python tools/primitives_retriever.py --list-categories        # category names

Output: JSON array (or object for --id) to stdout.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PRIMITIVES_FILE = Path(__file__).resolve().parent.parent / "kb" / "attack_primitives.json"


def load_primitives() -> list[dict]:
    if not PRIMITIVES_FILE.exists():
        return []
    data = json.loads(PRIMITIVES_FILE.read_text())
    return data.get("primitives", [])


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Query the attack primitives KB",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "category",
        nargs="?",
        default="",
        help="Filter by category (reentrancy, flash-loan, oracle-manipulation, access-control, "
             "logic-error, arithmetic, dos, front-running, upgrade-storage)",
    )
    parser.add_argument(
        "--compounds",
        metavar="PRIM-ID",
        help="Find all primitives that compound with the given primitive ID",
    )
    parser.add_argument(
        "--id",
        metavar="PRIM-ID",
        dest="prim_id",
        help="Return a single primitive by exact ID",
    )
    parser.add_argument(
        "--all",
        dest="all_prims",
        action="store_true",
        help="Return all primitives",
    )
    parser.add_argument(
        "--list-categories",
        action="store_true",
        help="List all available category names",
    )
    parser.add_argument(
        "--query",
        metavar="TEXT",
        help="Simple keyword search across name, trigger, and required_conditions fields",
    )
    args = parser.parse_args()

    primitives = load_primitives()
    if not primitives:
        print("[]")
        return 0

    if args.list_categories:
        cats = sorted({p["category"] for p in primitives})
        print(json.dumps(cats, indent=2))
        return 0

    if args.prim_id:
        match = next((p for p in primitives if p["id"] == args.prim_id), None)
        if match is None:
            print(f"No primitive found with id={args.prim_id}", file=sys.stderr)
            return 1
        print(json.dumps(match, indent=2))
        return 0

    if args.compounds:
        results = [
            p for p in primitives
            if args.compounds in p.get("known_compounds", [])
        ]
        print(json.dumps(results, indent=2))
        return 0

    if args.all_prims:
        print(json.dumps(primitives, indent=2))
        return 0

    if args.query:
        q = args.query.lower()
        results = [
            p for p in primitives
            if q in p.get("name", "").lower()
            or q in p.get("trigger", "").lower()
            or any(q in c.lower() for c in p.get("required_conditions", []))
        ]
        # Also filter by category if provided
        if args.category:
            results = [p for p in results if p.get("category") == args.category]
        print(json.dumps(results, indent=2))
        return 0

    if args.category:
        results = [p for p in primitives if p.get("category") == args.category]
        print(json.dumps(results, indent=2))
        return 0

    # Default: print all
    print(json.dumps(primitives, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
