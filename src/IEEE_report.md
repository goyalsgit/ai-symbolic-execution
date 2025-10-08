# IEEE Report: AI-Assisted Symbolic Execution and Automated Repair

## Title
AI-Assisted Symbolic Execution and Automated Bug Repair Using SMT Solving and ML-Assisted Patch Generation

## Abstract
(Write 4-6 lines summarizing the project: goals, methods, results.)

## 1. Introduction
- Problem statement
- Motivation
- Objectives

## 2. Literature Review
- Symbolic execution (Angr, KLEE)
- SMT solvers (Z3)
- Automated Program Repair (SEQUENCER, T5APR, Angelix)

## 3. Proposed System
- Overview diagram (DFD Level-0 and Level-1)
- Components: preprocessor, symbolic engine, solver, repair engine, validator

## 4. Design and Algorithms
- Step-by-step algorithm (detection → synthesis → validation)
- Pseudocode for main pipeline

## 5. Implementation
- Tools used: GCC, angr, claripy, z3, Python
- File structure (list files from README)

## 6. Experiments and Results
- Demo case: description of `bugprog.c`
- Steps executed and observed outputs
- Table: detected inputs, patches generated, tests passed

## 7. Discussion
- Strengths and limitations (path explosion, overfitting)
- Ethical considerations (AI suggested patches must be reviewed)

## 8. Conclusion and Future Work
- Summarize and propose future extensions (apply to Defects4J, integrate CodeT5)

## References
- Use IEEE citation style for papers and tool links.
