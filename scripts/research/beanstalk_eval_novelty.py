#!/usr/bin/env python3
"""P298 — beanstalk eval novelty (RESEARCH-ONLY, ADVISORY).

Per merged finding, query the indexed KB (kb/chroma `solodit_findings`, the all-MiniLM-L6-v2 embedder the KB was
built with) by the finding's title+description -> top cosine similarity. Classify novel (sim < threshold) vs
known/duplicate (>= threshold), mirroring the CLAUDE.md Hermes rule (KB sim < 0.4 + High/Critical -> human review).
Read-only over the KB. Emits novelty.json.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CFG = json.loads((ROOT / "config/research_beanstalk_eval.json").read_text())
OUT = ROOT / "documentation/research/assisted_mode/p298_beanstalk_eval/outputs"
THRESH = float(CFG["novelty_threshold"])
_STAMP = {"research_only": True, "is_gate": False, "severity": None, "reportable": False, "submission_ready": False}


def _findings():
    mf = json.loads((ROOT / CFG["merged_findings"]).read_text())
    return mf if isinstance(mf, list) else (mf.get("findings") or [])


def run():
    OUT.mkdir(parents=True, exist_ok=True)
    import chromadb
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(CFG["novelty_model"])
    client = chromadb.PersistentClient(path=str(ROOT / "kb/chroma"))
    col = client.get_collection(CFG["novelty_collection"])
    space = (col.metadata or {}).get("hnsw:space", "l2")

    rows = []
    findings = _findings()
    for f in findings:
        text = (f.get("title", "") + ". " + (f.get("description", "") or ""))[:2000]
        emb = model.encode([text], normalize_embeddings=True)[0].tolist()
        res = col.query(query_embeddings=[emb], n_results=3,
                        include=["distances", "metadatas", "documents"])
        dists = (res.get("distances") or [[None]])[0]
        d0 = dists[0] if dists and dists[0] is not None else None
        # cosine similarity from distance (chroma cosine distance = 1 - cos_sim; l2 over normalized ~ 2-2cos)
        if d0 is None:
            sim = None
        elif space == "cosine":
            sim = round(1.0 - d0, 3)
        else:  # l2 on normalized vectors: d^2 = 2 - 2cos -> cos = 1 - d^2/2
            sim = round(1.0 - (d0 * d0) / 2.0, 3)
        meta0 = ((res.get("metadatas") or [[{}]])[0] or [{}])[0] or {}
        cls = "novel" if (sim is not None and sim < THRESH) else "known_or_duplicate"
        rows.append({"id": f.get("id"), "severity": f.get("severity"), "title": f.get("title", "")[:70],
                     "top_similarity": sim, "novelty_class": cls,
                     "nearest_kb": (meta0.get("title") or meta0.get("source") or "")[:70]})

    novel = [r for r in rows if r["novelty_class"] == "novel"]
    high_crit_novel = [r for r in novel if str(r["severity"]).lower() in ("high", "critical")]
    out = dict(_STAMP, model=CFG["novelty_model"], collection=CFG["novelty_collection"], space=space,
               threshold=THRESH, n_findings=len(rows),
               distribution={"novel": len(novel), "known_or_duplicate": len(rows) - len(novel),
                             "high_critical_novel_to_human_review": [r["id"] for r in high_crit_novel]},
               findings=rows)
    (OUT / "novelty.json").write_text(json.dumps(out, indent=2))
    print(json.dumps({"n": len(rows), "novel": len(novel), "known": len(rows) - len(novel),
                      "high_crit_novel": [r["id"] for r in high_crit_novel],
                      "space": space}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
