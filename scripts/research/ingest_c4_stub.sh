#!/usr/bin/env bash
# Ingest a Code4rena contest's SOURCE (only) into an on-disk -fresh stub audit, blind.
# Usage: ingest_c4_stub.sh <audit_id> <c4_slug> <branch> <src_prefix>
# e.g.   ingest_c4_stub.sh phi-2024-08-fresh 2024-08-phi main src/
set -euo pipefail
AID="$1"; SLUG="$2"; BRANCH="${3:-main}"; SRCPFX="${4:-src/}"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
DEST="audits/$AID/contracts"
mkdir -p "$DEST"

# 1) register in registry.json audits[] (idempotent) + create subdirs (audit_context)
python3 - "$AID" "$SLUG" <<'PY'
import json,sys,datetime,os
aid,slug=sys.argv[1],sys.argv[2]
rp="audits/registry.json"; d=json.load(open(rp))
if aid not in [a['audit_id'] for a in d['audits']]:
    yr=slug[:4]; mo=slug[5:7]
    d['audits'].append({"audit_id":aid,"name":aid,"contest":slug,"platform":"Code4rena","status":"active",
      "start_date":f"{yr}-{mo}-01","deadline":f"{yr}-{mo}-28T23:59:00Z","submit_count":0,"poc_count":0,
      "last_active":datetime.datetime.now(datetime.timezone.utc).isoformat()})
    d['updated_at']=datetime.datetime.now(datetime.timezone.utc).isoformat()
    json.dump(d,open(rp,'w'),indent=2); print("registered",aid)
else: print("already registered",aid)
import scripts.audit_context as ac
base=f"audits/{aid}"
for s in ac._AUDIT_SUBDIRS: os.makedirs(os.path.join(base,s),exist_ok=True)
PY

# 2) curl all in-scope .sol verbatim (src prefix; skip test/mock/script/lib)
echo "fetching source for $SLUG @ $BRANCH ..."
FILES=$(curl -s "https://api.github.com/repos/code-423n4/$SLUG/git/trees/$BRANCH?recursive=1" \
  | python3 -c "import json,sys;d=json.load(sys.stdin);[print(t['path']) for t in d['tree'] if t['path'].endswith('.sol') and t['path'].startswith('$SRCPFX') and not any(k in t['path'].lower() for k in ['test/','/mock','script/','/lib/'])]")
N=0
for f in $FILES; do
  rel=${f#$SRCPFX}
  mkdir -p "$DEST/$(dirname "$rel")"
  curl -s "https://raw.githubusercontent.com/code-423n4/$SLUG/$BRANCH/$f" -o "$DEST/$rel"
  N=$((N+1))
done
echo "fetched $N .sol files"

# 3) write meta + freeze hash
python3 - "$AID" "$SLUG" "$BRANCH" <<'PY'
import json,sys,hashlib,glob
aid,slug,branch=sys.argv[1],sys.argv[2],sys.argv[3]
d=f"audits/{aid}/contracts"
h=hashlib.sha256()
for f in sorted(glob.glob(d+"/**/*.sol",recursive=True)): h.update(open(f,'rb').read())
json.dump({"audit_id":aid,"name":aid,"contest":slug,"platform":"Code4rena","language":"Solidity",
  "framework":"foundry","contract_path":"contracts","primary_contract_dir":"contracts",
  "source":f"github.com/code-423n4/{slug} @ {branch} (curl verbatim)",
  "eval_mode":"PIPELINE-PROOF (pre-cutoff; prior-knowledge confound — NOT a blind-streak iteration)",
  "blind_ok":True,"source_sha256":h.hexdigest(),"frozen_at":"2026-06-10"},
  open(f"audits/{aid}/meta.json",'w'),indent=2)
print("frozen source_sha256",h.hexdigest()[:16])
PY
echo "INGESTED $AID (source only; report NOT fetched). Next: switch + manifest + discover + reveal."
