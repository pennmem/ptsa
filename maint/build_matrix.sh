#!/usr/bin/env bash
# Build the full PTSA conda matrix locally, one cell per conda-build
# invocation (mirrors what .github/workflows/build.yml does per
# strategy.matrix cell). Per-cell invocation is REQUIRED: a single
# `conda-build` run driven by a zipped python/numpy variant list in
# conda_build_config.yaml mis-renders the cells (scrambled build envs,
# empty packages) — see that file's header.
#
# Usage:
#   maint/build_matrix.sh [output_dir]
#
# Produces 6 cells:
#   (py3.10, numpy 1.24) (py3.10, numpy 2)
#   (py3.11, numpy 1.24) (py3.11, numpy 2)
#   (py3.12, numpy 2)    (py3.13, numpy 2)
# numpy 1.24 × py3.12/3.13 are omitted (conda-forge has no numpy 1.24
# build for python >= 3.12).

set -euo pipefail

RECIPE="$(cd "$(dirname "$0")/.." && pwd)/conda.recipe"
OUT="${1:-$(cd "$(dirname "$0")/.." && pwd)/build/conda}"

# (python, numpy) cells — keep in sync with the GH workflow matrix.
CELLS=(
    "3.10 1.24"
    "3.10 2"
    "3.11 1.24"
    "3.11 2"
    "3.12 2"
    "3.13 2"
)

echo "Building ${#CELLS[@]} cells into $OUT"
for cell in "${CELLS[@]}"; do
    read -r py np <<< "$cell"
    echo "=============================================================="
    echo "  cell: python=$py numpy=$np"
    echo "=============================================================="
    conda-build "$RECIPE" \
        --output-folder="$OUT" \
        --python="$py" \
        --variants "{numpy: ['$np']}" \
        --no-anaconda-upload \
        -c pennmem -c conda-forge
done

echo ""
echo "Done. Built packages:"
ls -1 "$OUT"/linux-64/ptsa-*.conda 2>/dev/null || true
