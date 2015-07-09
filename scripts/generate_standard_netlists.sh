#!/bin/bash

# Generates a set of synthetic netlists of various sizes

BASE_DIR="$(dirname "$0")/.."

SCRIPTS_DIR="$BASE_DIR/scripts"
NETLISTS_DIR="$BASE_DIR/netlists"


# The various numbers of chips to include in each size of the benchmarks
NUM_CHIPS=(4 48 144)

for num in "${NUM_CHIPS[@]}"; do
    python "$SCRIPTS_DIR/generate_synthetic_benchmark.py" \
        $(($num*15)) -P 16 \
        > "$NETLISTS_DIR/${num}_chips_nengo.json"
    
    python "$SCRIPTS_DIR/generate_synthetic_benchmark.py" \
        $(($num*15)) -P 16 -r 0.05 \
        > "$NETLISTS_DIR/${num}_chips_nengo_random_0.05.json"
    
    python "$SCRIPTS_DIR/generate_synthetic_benchmark.py" \
        $(($num*15)) -n hexmesh \
        > "$NETLISTS_DIR/${num}_chips_hexmesh.json"
    
    python "$SCRIPTS_DIR/generate_synthetic_benchmark.py" \
        $(($num*15)) -n hexmesh -r 0.05 \
        > "$NETLISTS_DIR/${num}_chips_hexmesh_random_0.05.json"
    
    python "$SCRIPTS_DIR/generate_synthetic_benchmark.py" \
        $(($num*15)) -d 2Dtorus 4 "gauss(0, 4)" \
        > "$NETLISTS_DIR/${num}_chips_gauss_4_4.json"
done
