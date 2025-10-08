#!/usr/bin/env bash
set -euo pipefail
echo "Running full demo (compile -> find bug -> patch -> run)"
cd src
gcc -o bugprog bugprog.c
python3 find_bug.py || true
./bugprog 0 || true
python3 ../src/auto_patch.py bugprog.c bugprog_fixed.c || true
gcc -o bugprog_fixed bugprog_fixed.c || true
./bugprog_fixed 0 || true
echo "Demo finished."
