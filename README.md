# Sound Slices of Monotone Co-Design

This repository contains the code, numerical validation, and formal verification for the paper:
**"Certified Error Bounds for Soundly Sliced Multiphysics Loops"**

## Contents
* `paper/`: The preprint (PDF and LaTeX source).
* `python_validation/`: Python scripts reproducing the multiphysics case studies (eVTOL, quadcopter, ECS).
* `lean_formalization/`: Lean 4 code containing the formal proofs for Tier 0 (error recursion) and Tier 1 (two-point certificate).

## Lean 4 Verification
The algebraic core is fully machine-checked with **zero sorry**.
To verify the proofs, navigate to `lean_formalization/` and run:
```bash
lake build# SoundSlices