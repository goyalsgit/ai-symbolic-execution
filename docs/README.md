# AI-assisted Symbolic Execution Demo (Complete Implementation)

This repository contains a complete, beginner-friendly implementation of an **AI-assisted symbolic execution** demo suitable for demonstration and an IEEE-style report. It includes:

- `bugprog.c` — a tiny buggy C program (divide-by-zero / crash).
- `find_bug.py` — angr script to find inputs that trigger the crash (requires `angr` and `claripy`).
- `bugprog_fixed.c` — a manual fix to avoid the crash.
- `auto_patch.py` — simple automated patcher: template-based; optional AI integration via OpenAI API.
- `z3_example.py` — a short Z3 SMT solver example showing constraint solving.
- `build_and_run.sh` — convenience script to compile and run the demo steps.
- `IEEE_report.md` — a skeleton IEEE-format report you can use in your submission.

## Quick start (on your machine)

1. Compile:
   ```bash
   gcc -o bugprog bugprog.c
   ```
2. (Optional, recommended) Create Python venv and install angr:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install angr z3-solver
   ```
3. Run angr script to discover the failing input:
   ```bash
   python3 find_bug.py
   ```
4. Reproduce crash:
   ```bash
   ./bugprog 0
   ```
5. Apply automatic template patch:
   ```bash
   python3 auto_patch.py --mode template bugprog.c bugprog_fixed_auto.c
   gcc -o bugprog_fixed_auto bugprog_fixed_auto.c
   ./bugprog_fixed_auto 0
   ```
6. See Z3 example:
   ```bash
   python3 z3_example.py
   ```
