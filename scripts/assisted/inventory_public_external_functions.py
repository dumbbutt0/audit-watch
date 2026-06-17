#!/usr/bin/env python3
"""
inventory_public_external_functions.py — P103 in-scope function inventory (RESEARCH-ONLY, UN-WIRED).

P102 showed the lens *selection* nearly dropped LiquidityManager.moveLiquidity (the M-01 locus). This helper
lists EVERY function in the in-scope Solidity so autonomous enumeration can run over the full public/external
surface, not only lens-surfaced functions. It only INVENTORIES — it never validates, ranks, promotes, sets
severity, or submits. Recall input only; precision stays downstream.

Per function: contract · function · visibility · mutability · file · source_span · is_constructor. The
public/external functions are the enumeration set; internal/private are recorded but skipped; constructors are a
SEPARATE category (not mixed into normal function-invariant ranking).

is_gate:false research_only:true review_only:true routes_in_production:false routed_manifest_ids:[].
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

FLAGS = {"is_gate": False, "research_only": True, "review_only": True,
         "routes_in_production": False, "routed_manifest_ids": []}

# contract/interface/library opener (to attribute functions to their container).
_CONTAINER_RE = re.compile(r"\b(contract|interface|library)\s+([A-Za-z_]\w*)")
# function header up to the body-opening `{` or interface-decl `;`.
_FUNC_RE = re.compile(r"\bfunction\s+([A-Za-z_]\w*)\s*\((.*?)\)([^{;]*)(\{|;)", re.S)
_CTOR_RE = re.compile(r"\bconstructor\s*\((.*?)\)([^{]*)\{", re.S)

_VIS = ("external", "public", "internal", "private")
_MUT = ("view", "pure", "payable")


def _strip_comments(src: str) -> str:
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.S)
    src = re.sub(r"//[^\n]*", "", src)
    return src


def _line_of(src: str, pos: int) -> int:
    return src.count("\n", 0, pos) + 1


def _container_at(containers: List, pos: int) -> str:
    name = "?"
    for cpos, cname in containers:
        if cpos <= pos:
            name = cname
        else:
            break
    return name


def _scan_text(src: str, file_label: str) -> List[Dict[str, Any]]:
    clean = _strip_comments(src)
    containers = [(m.start(), m.group(2)) for m in _CONTAINER_RE.finditer(clean)]
    out: List[Dict[str, Any]] = []

    for m in _CTOR_RE.finditer(clean):
        mods = m.group(2)
        out.append({"contract": _container_at(containers, m.start()), "function": "constructor",
                    "visibility": "public", "mutability": "payable" if "payable" in mods else "nonpayable",
                    "file": file_label, "source_span": [_line_of(clean, m.start()), _line_of(clean, m.end())],
                    "is_constructor": True})

    for m in _FUNC_RE.finditer(clean):
        name = m.group(1)
        mods = m.group(3) or ""
        vis = next((v for v in _VIS if re.search(r"\b" + v + r"\b", mods)), "internal")  # default internal/no-kw
        mut = next((u for u in _MUT if re.search(r"\b" + u + r"\b", mods)), "nonpayable")
        out.append({"contract": _container_at(containers, m.start()), "function": name,
                    "visibility": vis, "mutability": mut, "file": file_label,
                    "source_span": [_line_of(clean, m.start()), _line_of(clean, m.end())],
                    "is_constructor": False})
    return out


def inventory(src: Union[str, Path, List[Union[str, Path]]]) -> Dict[str, Any]:
    """Inventory all functions in the in-scope source. `src` may be a dir, a single file, or a list of files."""
    paths: List[Path] = []
    if isinstance(src, (list, tuple)):
        paths = [Path(p) for p in src]
    else:
        p = Path(src)
        paths = sorted(p.glob("*.sol")) if p.is_dir() else [p]

    fns: List[Dict[str, Any]] = []
    for p in paths:
        try:
            fns.extend(_scan_text(p.read_text(encoding="utf-8"), p.name))
        except (OSError, UnicodeDecodeError):
            continue

    public_external = [f for f in fns if (not f["is_constructor"]) and f["visibility"] in ("public", "external")]
    internal_private = [f for f in fns if (not f["is_constructor"]) and f["visibility"] in ("internal", "private")]
    constructors = [f for f in fns if f["is_constructor"]]
    return {
        **FLAGS,
        "functions": fns,
        "public_external": public_external,
        "internal_private": internal_private,
        "constructors": constructors,
        "counts": {"total": len(fns), "public_external": len(public_external),
                   "internal_private": len(internal_private), "constructors": len(constructors),
                   "files": len(paths)},
    }


_SAMPLE = """
// SPDX
contract Foo {
    uint256 public x;
    constructor(uint256 _x) payable { x = _x; }
    function pubView() public view returns (uint256) { return x; }
    function extWrite(uint256 v) external { x = v; }
    function _helper() internal { x++; }
    function privThing() private pure returns (bool) { return true; }
    function noKw() returns (uint256) { return x; }   // defaults to internal
}
interface IBar { function ext() external; }
"""


def _self_test() -> int:
    ok = True
    def chk(cond, m):
        nonlocal ok; ok &= bool(cond); print(f"  [{'PASS' if cond else 'FAIL'}] {m}")
    inv = inventory.__wrapped__ if hasattr(inventory, "__wrapped__") else None  # noqa
    r = _scan_text(_SAMPLE, "Foo.sol")
    res = {"functions": r, "public_external": [f for f in r if not f["is_constructor"] and f["visibility"] in ("public", "external")],
           "constructors": [f for f in r if f["is_constructor"]]}
    names = {(f["function"], f["visibility"]) for f in r}
    chk(("pubView", "public") in names, "captures public function")
    chk(("extWrite", "external") in names, "captures external function")
    chk(("ext", "external") in names, "captures interface external function")
    chk(any(f["function"] == "constructor" and f["is_constructor"] for f in r), "captures constructor separately")
    pe = {f["function"] for f in res["public_external"]}
    chk("pubView" in pe and "extWrite" in pe and "ext" in pe, "public/external surface set")
    chk("_helper" not in pe and "privThing" not in pe, "internal/private excluded from public/external surface")
    chk("constructor" not in pe, "constructor not in public/external surface")
    chk(any(f["function"] == "pubView" and f["mutability"] == "view" for f in r), "mutability=view captured")
    chk(any(f["function"] == "constructor" and f["mutability"] == "payable" for f in r), "payable constructor")
    chk(all(len(f["source_span"]) == 2 for f in r), "source_span recorded")
    chk(FLAGS["is_gate"] is False, "FLAGS un-wired")
    print("SELF-TEST:", "OK" if ok else "FAILED")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--src", help="dir or file to inventory")
    ap.add_argument("--out", help="write inventory JSON here")
    args = ap.parse_args()
    if args.self_test:
        return _self_test()
    if not args.src:
        ap.error("--src is required (or --self-test)")
    res = inventory(args.src)
    if args.out:
        Path(args.out).write_text(json.dumps(res, indent=2))
        print(f"wrote {args.out} ({res['counts']})")
    else:
        print(json.dumps(res, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
