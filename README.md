markdown
# Certified Error Bounds for Soundly Sliced Multiphysics Loops

This repository contains the LaTeX source, numerical validation scripts, and Lean 4 formal verification for the paper: **"Certified Error Bounds for Soundly Sliced Multiphysics Loops"**.

## 📂 Repository Structure

*   **`paper/`**: The LaTeX source (`main.tex`), the compiled PDF (`main.pdf`), and all figures (`fig_*.png`).
*   **`python_validation/`**: Python scripts and JSON outputs reproducing the multiphysics case studies (quadcopter, eVTOL, ECS).
*   **`lean_formalization/`**: Lean 4 code containing the machine-checked proofs (zero `sorry`) for the algebraic core (Theorem 5.1 and Corollary 5.1).

---

## 🛡️ Lean 4 Verification

The algebraic core is fully formalized and machine-checked. To verify the proofs:
1. Navigate to the Lean directory:
   ```bash
   cd lean_formalization
2. Ensure you have Lean 4 and Mathlib installed.

3. Build the project:

bash
lake build
(The build should complete successfully with 0 sorry).

📊 Numerical Validation
To reproduce the data in Table 2, Table 4, and Figures 1–3:

1. Navigate to the Python directory:

bash
cd python_validation

2. Run the scripts:

bash
python act_final.py
python act_evtol.py
python act_ecs.py

The scripts will output the Pareto fronts, certified margins, and write the corresponding .json files.


