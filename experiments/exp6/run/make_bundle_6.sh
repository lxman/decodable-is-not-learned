#!/usr/bin/env bash
# Exp 6, MAC side: bundle master and exp6-* tags for the box and print its
# sha256 (check it on the box after scp). No credential is placed on a rented host: the box gets
# the repository by bundle and returns results by rsync pull FROM the Mac.
# This limits refs, not content: private files/history reachable from master are still carried.
# Usage: run/make_bundle_6.sh [out] [endpoint|sweep]
set -euo pipefail
OUT=${1:-${TMPDIR:-/tmp}/exp6.bundle}
STAGE=${2:-endpoint}
case "$STAGE" in endpoint|sweep) ;; *) echo "REFUSING: stage must be endpoint or sweep"; exit 2 ;; esac
export PATH="/opt/homebrew/bin:$PATH"
cd "${REPO_DIR:-/Users/michaeljordan/emergence-paper}"
[ "$(git symbolic-ref --short HEAD)" = master ] || { echo "REFUSING: checkout is not master"; exit 2; }
git diff --quiet HEAD -- || { echo "REFUSING: tracked changes are not committed"; exit 2; }
need="exp6-preregistered exp6-predictor-sealed"
[ "$STAGE" = "sweep" ] && need="$need exp6-endpoint-sealed"
for t in $need; do
  git show-ref --verify --quiet "refs/tags/$t" || { echo "REFUSING: missing $t"; exit 2; }
done
if [ "$STAGE" = "sweep" ]; then
  git cat-file -e master:experiments/exp6/projection.md || { echo "REFUSING: projection is not committed"; exit 2; }
fi
# Check the actual bytes BEFORE the bundle can be sent to a box. No model is loaded.
"${EXP6_PYTHON:-$HOME/emergence-lab/.venv/bin/python}" - "$STAGE" <<'PY'
import sys
from experiments.exp6 import battery_6 as b6, pins_6 as p6
from experiments.exp6.run import endpoint_6 as ep, sweep_6 as sw
print("preregistration", p6.require_prereg_6()["n_bound"], "blobs bound")
print("predictor seal", ep.require_predictor_seal(b6.EXP6)["sha256"])
if sys.argv[1] == "sweep":
    print("endpoint seal", sw.require_endpoint_seal(b6.EXP6))
PY
refs=(refs/heads/master)
while IFS= read -r ref; do refs+=("$ref"); done < <(git for-each-ref --format='%(refname)' 'refs/tags/exp6-*')
git bundle create "$OUT" "${refs[@]}"
git bundle verify "$OUT"
# No missing required ref and no extra ref may be hidden by the local checkout.
diff <(printf '%s\n' "${refs[@]}" | sort) <(git bundle list-heads "$OUT" | awk '{print $2}' | sort)
shasum -a 256 "$OUT"
