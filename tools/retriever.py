#!/usr/bin/env python3
"""
retriever.py

Called by specialist agents to query the Solodit knowledge base.
Returns the top-k most similar findings for a given vuln_type and query.

Usage (called as subprocess by agents):
    python tools/retriever.py reentrancy "withdraw function external call before state update"
    python tools/retriever.py oracle-manipulation "chainlink staleness check missing"
    python tools/retriever.py --all "flash loan governance attack voting power"

Output: JSON array printed to stdout.
"""

import argparse
import json
import sys
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

KB_DIR = Path("kb")

VALID_VULN_TYPES = [
    "reentrancy", "access-control", "arithmetic", "oracle-manipulation",
    "flash-loan", "logic-error", "gas-griefing", "dos", "signature-replay",
    "storage-collision", "proxy-upgrade", "front-running", "other",
]

VALID_SOURCES = ["solodit", "code4rena", "sherlock", "immunefi"]


def query_kb(vuln_type: str, query: str, top_k: int = 5, all_types: bool = False,
             source: str | None = None) -> list[dict]:
    """Query the Chroma collection and return structured results."""

    chroma_path = KB_DIR / "chroma"
    if not chroma_path.exists():
        return [{
            "error": "Knowledge base not found. Run: python scripts/solodit_scraper.py",
            "findings": []
        }]

    client = chromadb.PersistentClient(path=str(chroma_path))

    try:
        collection = client.get_collection("solodit_findings")
    except Exception:
        return [{"error": "Collection 'solodit_findings' not found. Run the scraper first.", "findings": []}]

    total = collection.count()
    if total == 0:
        return [{"error": "Knowledge base is empty. Run: python scripts/solodit_scraper.py"}]

    # Load embedding model
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    query_embedding = model.encode([query])[0].tolist()

    # Build filter
    where_filter = None
    filters = []
    if not all_types and vuln_type in VALID_VULN_TYPES:
        filters.append({"vuln_type": {"$eq": vuln_type}})
    if source and source in VALID_SOURCES:
        filters.append({"source": {"$eq": source}})
    if len(filters) == 1:
        where_filter = filters[0]
    elif len(filters) > 1:
        where_filter = {"$and": filters}

    # Query
    try:
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, total),
            where=where_filter,
            include=["documents", "metadatas", "distances"],
        )
    except Exception as e:
        # If the filter returns 0 results, Chroma raises. Fall back to no filter.
        try:
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=min(top_k, total),
                include=["documents", "metadatas", "distances"],
            )
        except Exception as e2:
            return [{"error": f"Query failed: {e2}"}]

    findings = []
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    for doc, meta, dist in zip(docs, metas, distances):
        try:
            parsed = json.loads(doc)
        except (json.JSONDecodeError, TypeError):
            parsed = {"description": str(doc)}

        _score = round(1 - dist, 3)
        findings.append({
            "title": meta.get("title", parsed.get("title", "")),
            "severity": meta.get("severity", ""),
            "vuln_type": meta.get("vuln_type", ""),
            "protocol": meta.get("protocol", ""),
            "audit_firm": meta.get("audit_firm", ""),
            "source": meta.get("source", "solodit"),
            "description": parsed.get("description", "")[:600],
            "code_snippet": parsed.get("code_snippet", "")[:500],
            "fix": parsed.get("fix", "")[:400],
            "url": meta.get("url", ""),
            "similarity_score": _score,
        })
        # ── viz: emit KB_MATCH for high-similarity results ────────────────────
        if _score > 0.75:
            try:
                from viz.event_emitter import emit as _viz_emit
                _viz_emit("KB_MATCH", source_agent="retriever", payload={
                    "solodit_id": meta.get("finding_id", meta.get("url", f"KB-{len(findings)}")),
                    "title": meta.get("title", ""),
                    "similarity_score": _score,
                    "exploit_pattern": vuln_type,
                    "historical_severity": meta.get("severity", ""),
                    "protocol_type": meta.get("protocol", ""),
                    "query": query,
                })
            except Exception:
                pass

    return findings


def main():
    parser = argparse.ArgumentParser(
        description="Query the Solodit knowledge base for relevant audit findings"
    )
    parser.add_argument("vuln_type", nargs="?", default="other",
                        choices=VALID_VULN_TYPES + ["other"],
                        help="Vulnerability category to filter by")
    parser.add_argument("query", nargs="?", default="",
                        help="Natural language description of the pattern you're investigating")
    parser.add_argument("--top-k", type=int, default=5, help="Number of results to return")
    parser.add_argument("--all", action="store_true", dest="all_types",
                        help="Search across all vuln types (ignore vuln_type filter)")
    parser.add_argument("--source", choices=VALID_SOURCES, default=None,
                        help="Filter by knowledge base source (solodit, code4rena, sherlock, immunefi)")
    args = parser.parse_args()

    if not args.query:
        print(json.dumps({"error": "Query string is required"}, indent=2))
        sys.exit(1)

    results = query_kb(
        vuln_type=args.vuln_type,
        query=args.query,
        top_k=args.top_k,
        all_types=args.all_types,
        source=args.source,
    )

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
