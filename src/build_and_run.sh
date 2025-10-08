#!/usr/bin/env bash
set -euo pipefail
echo "Compiling original program..."
gcc -o bugprog bugprog.c || { echo "gcc failed"; exit 1; }
echo "Running symbolic finder (requires angr)..."
python3 find_bug.py || true
echo "Demonstrating crash with concrete input:"
./bugprog 0 || true
echo "Compiling fixed program..."
gcc -o bugprog_fixed bugprog_fixed.c || true
echo "Running fixed program:"
./bugprog_fixed 0 || true
