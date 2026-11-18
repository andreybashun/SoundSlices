-- This module serves as the root of the `SoundSlices` library.
-- Import modules here that should be built as part of the library.
import SoundSlices.Basic

import Mathlib

namespace SoundSlices

/-! ## Tier 0: геометрическая рекурсия ошибки -/

lemma error_recursion_aux (d : ℕ → ℝ) (q g : ℝ) (hq0 : 0 ≤ q) (hq1 : q < 1) (_hg : 0 ≤ g)
    (h_rec : ∀ n, d (n+1) ≤ q * d n + g) (h_0 : d 0 = 0) :
    ∀ n, d n ≤ g * (1 - q^n) / (1 - q) := by
  intro n
  induction n with
  | zero =>
    rw [h_0, pow_zero]
    simp
  | succ n ih =>
    calc d (n+1)
      _ ≤ q * d n + g := h_rec n
      _ ≤ q * (g * (1 - q^n) / (1 - q)) + g := by
        gcongr
      _ = g * (1 - q^(n+1)) / (1 - q) := by
        have h1 : 1 - q ≠ 0 := by linarith
        field_simp [h1]
        ring

/-! ## T1.2: точный наклон аффинной петли -/

lemma affine_loop_exact (B c ε : ℝ) (hB : B < 1) (_hε_lt : ε < 1) (_hε_pos : 0 < ε) (h_denom : 1 - B - ε ≠ 0) :
  let x0 := c / (1 - B)
  let xs := c / (1 - B - ε)
  xs - x0 = (c * ε) / ((1 - B - ε) * (1 - B)) := by
  dsimp
  have hB_ne : 1 - B ≠ 0 := by linarith
  field_simp [hB_ne, h_denom]
  ring

/-! ## T1.1: главный сертификат (двухточечная форма) -/

theorem certified_two_point_seg
    (f0 fs : ℝ → ℝ) (x0 xs ε kappa : ℝ)
    (h_x0_fix : f0 x0 = x0) (h_xs_fix : fs xs = xs)
    (hε : 0 < ε) (_hε' : ε < 1) (_hK : kappa < 1 - ε) (_hK' : 0 ≤ kappa)
    (h_x0_pos : 0 < x0) (h_x0_le_xs : x0 ≤ xs)
    (h_lip : ∀ x y, x ≤ y → f0 y - f0 x ≤ kappa * (y - x))
    (h_slice : ∀ x, fs x = f0 x / (1 - ε))
    : (xs - x0) / x0 ≤ ε / ((1 - ε) - kappa) := by

  have h_denom_pos : 0 < 1 - ε := by linarith
  have h_denom_pos' : 0 < 1 - ε - kappa := by linarith
  have h1 : 1 - ε ≠ 0 := ne_of_gt h_denom_pos

  have h_fs_diff : fs xs - fs x0 = (f0 xs - f0 x0) / (1 - ε) := by
    rw [h_slice xs, h_slice x0]
    ring

  have h_lip_fs : fs xs - fs x0 ≤ kappa * (xs - x0) / (1 - ε) := by
    rw [h_fs_diff]
    have h_lip0 := h_lip x0 xs h_x0_le_xs
    have : (f0 xs - f0 x0) / (1 - ε) ≤ (kappa * (xs - x0)) / (1 - ε) := by
      gcongr
    linarith

  have h_fs_x0 : fs x0 - x0 = ε * x0 / (1 - ε) := by
    rw [h_slice x0, h_x0_fix]
    field_simp [h1]
    ring

  have h_xs_sub : xs - x0 = (fs xs - fs x0) + (fs x0 - x0) := by
    rw [h_xs_fix]
    ring

  have h_ineq : xs - x0 ≤ kappa * (xs - x0) / (1 - ε) + ε * x0 / (1 - ε) := by
    calc xs - x0
      _ = (fs xs - fs x0) + (fs x0 - x0) := h_xs_sub
      _ ≤ kappa * (xs - x0) / (1 - ε) + ε * x0 / (1 - ε) := by
          rw [h_fs_x0]
          linarith [h_lip_fs]

  have h_final : (xs - x0) * (1 - ε - kappa) ≤ ε * x0 := by
    have h_mul : (xs - x0) * (1 - ε) ≤ kappa * (xs - x0) + ε * x0 := by
      calc (xs - x0) * (1 - ε)
        _ ≤ (kappa * (xs - x0) / (1 - ε) + ε * x0 / (1 - ε)) * (1 - ε) := by
          apply mul_le_mul_of_nonneg_right h_ineq (le_of_lt h_denom_pos)
        _ = kappa * (xs - x0) + ε * x0 := by
          field_simp [h1]
    linarith

  have h_x0_ne : x0 ≠ 0 := ne_of_gt h_x0_pos
  have h_denom_ne : 1 - ε - kappa ≠ 0 := ne_of_gt h_denom_pos'
  field_simp [h_x0_ne, h_denom_ne]
  rw [mul_comm x0 ε] -- меняем местами x0 * ε на ε * x0
  exact h_final

  #print axioms certified_two_point_seg

end SoundSlices
