# Reference — Rigor Checklist

Catalog of classic failure modes in proofs, formal arguments, and empirical claims.
**Required during proof-verification (step 4)** — run against the evidence, one item
at a time. Sections 1–9 = formal machinery (shared by math, logic, CS correctness,
theoretical derivations); section 10 = empirical/statistical claims; section 11 =
argumentation fallacies (philosophy, law, debate, review writing).

Usage: for each applicable item, search the proof/claim for an occurrence. A finding
= flag the step + quote the ORIGINAL text. Items that do not apply are skipped and
the skip is noted.

## 1. Quantifiers
- [ ] **Swapped quantifier order**: `∀x ∃y` ≠ `∃y ∀x`. A proof treating one `y` as
  valid for all `x` when it depends on `x` (or vice versa) — the #1 error at this level.
- [ ] **Negation of nested quantifiers**: `¬(∀x P(x)) = ∃x ¬P(x)` and
  `¬(∃x P(x)) = ∀x ¬P(x)` — a wrongly-directed negation ruins the contradiction.
- [ ] **Quantifier domain silently narrowed**: "for all x" becoming "for all x ≠ 0"
  halfway through.

## 2. Division & invertibility
- [ ] **Division by zero / zero factors**: dividing both sides by an expression that
  can be 0.
- [ ] **Non-invertible objects**: singular matrices, non-bijective functions treated
  as invertible, mod arithmetic without gcd 1.
- [ ] **Assumed existence**: "take z such that …" with no construction/existence
  argument (unattained suprema in non-compact spaces; "pick a basis" needs AC in
  general spaces).

## 3. Degenerate cases & endpoints
- [ ] **Empty sets / trivial structures**: "for all" claims whose proof starts from
  a non-trivial example.
- [ ] **`n = 0, 1`**: many theorems hold only for `n ≥ 2`; proofs that fail on the
  small cases.
- [ ] **Interval endpoints**: inclusive vs exclusive (`[0,1)` vs `(0,1]`), `≤` vs
  `<` — check every inequality actually used.
- [ ] **Vacuous cases**: implications with false premises are automatically true —
  "holds" claims that are only vacuously true in the interesting regime.

## 4. Limits, convergence, interchange
- [ ] **Interchanging limits/integrals/derivatives** without uniformity (dominated
  convergence, uniform convergence) — `lim f_n ≠ f_lim` without conditions.
- [ ] **Terms → 0 ⇒ series converges**: the classic `∑ 1/n`.
- [ ] **Convergent ≠ absolutely convergent**: reordering sums needs absolute convergence.
- [ ] **"Sufficiently large" never established**: "for n sufficiently large" — which
  n₀, and why does it exist?

## 5. Logical structure
- [ ] **Circular reasoning**: a step uses the theorem being proven (or an unproven
  equivalent form).
- [ ] **Off-by-one induction**: the step `n → n+1` is right but the base case starts
  at the wrong `n₀` / is not covered.
- [ ] **Incomplete case split**: the listed cases do not exhaust the possibilities
  (`<`, `=`, `>` with one case missing).
- [ ] **"Obvious"/"clearly"/"standard"**: these phrases = a step without a basis —
  unpack until the inference is explicit (proof-verification step 3).

## 6. Definitions & terminology
- [ ] **Two definitions for one term**: continuity (ε-δ vs sequential),
  integrability (Riemann vs Lebesgue), cross-book variants — proof uses definition
  A, claim is used in a context using definition B.
- [ ] **Continuous vs uniformly continuous, convergent vs Cauchy, bounded vs
  convergent** — pairs equivalent only in special spaces (compact/complete).
- [ ] **Claim strength mismatch**: proving the weak form but concluding the strong
  form (or citing the strong form without its hypotheses).

## 7. Probability & measure
- [ ] **Independence assumed** without conditions.
- [ ] **Union bound misapplied** / conditional probabilities in the wrong direction.
- [ ] **"Almost surely" confused with "surely"**; measure-zero sets ≠ empty sets.

## 8. Finite vs infinite
- [ ] **Finite arguments used on infinite sets**: ordered re-indexing, "take the
  largest" in unbounded sets, induction over uncountable sets.
- [ ] **Cardinality slips**: countable treated as finite, uncountable as countable.
- [ ] **Lost compactness**: equivalences valid in compact spaces applied in general ones.

## 9. Numerics (link to numeric-sanity)
- [ ] **Floating-point precision masking an error**: a small consistent difference
  is a signal, not noise.
- [ ] **Only canonical test cases**: without degenerate/adversarial cases, "passes"
  means nothing.

## 10. Empirical & statistical claims
For studies, papers, and quantitative claims:
- [ ] **Correlation ≠ causation** — no design that could support the causal reading
  (no randomization, no natural experiment, no controls).
- [ ] **Confounds unaddressed**: selection effects, unmodeled third variables,
  self-selection into treatment.
- [ ] **Sample size / power**: tiny samples, "p < 0.05" from n ≈ 10, no power
  discussion.
- [ ] **Multiple comparisons / p-hacking**: many tests, one highlighted; endpoints
  switched post hoc; subgroups emphasized only when significant.
- [ ] **Base-rate neglect**: impressive-sounding relative risks with a tiny absolute
  effect; Bayes-ignorant screening claims.
- [ ] **Survivorship/selection bias**: the sample only contains survivors, responders,
  or published (positive) studies.
- [ ] **Regression to the mean / novelty-placebo effects**: pre-post designs with no
  control group.
- [ ] **Data leakage (ML)**: train/test contamination, target leakage, preprocessing
  fit on the full dataset.
- [ ] **Cherry-picked windows/subsets**: time frames, cohorts, or metrics chosen
  after seeing results.
- [ ] **Arithmetic in the paper itself**: recompute percentages, effect sizes,
  totals, and base rates from the reported numbers (numeric-sanity) — arithmetic
  errors are common and decisive.
- [ ] **Publication/contestation status**: retractions, corrected versions, failed
  replications, meta-analyses contradicting the single study (claim-verification step 4).

## 11. Argumentation & fallacies (philosophy, law, debate, reviews)
- [ ] **Formal fallacies in conditionals**: affirming the consequent (`P→Q, Q, ∴ P`),
  denying the antecedent (`P→Q, ¬P, ∴ ¬Q`) — invalid regardless of how plausible
  the content sounds.
- [ ] **Illicit conversion/inverse on quantified conditionals**: `∀x(P(x)→Q(x))`
  licenses contraposition `∀x(¬Q(x)→¬P(x))` but NOT the converse `∀x(Q(x)→P(x))`
  nor the inverse `∀x(¬P(x)→¬Q(x))`.
- [ ] **Equivocation**: a key term shifts meaning mid-argument ("fair" as equitable
  then as probabilistic; "theory" as conjecture then as established framework).
- [ ] **Begging the question**: a premise is a restatement of the conclusion (the
  argument-level version of circular reasoning, §5).
- [ ] **False dilemma**: only two options presented where more exist (relevant to
  "either P or Q, not P, therefore Q" steps).
- [ ] **Hasty generalization**: universal claim from a weak/few instances —
  `∃x P(x)` does not support `∀x P(x)` (the mirror error of counterexample hunting).
- [ ] **Composition / division**: what holds of parts inferred for the whole (or
  vice versa) without justification.
- [ ] **Straw man**: the argument attacked is weaker than the one made — verify the
  claim against its STEELMAN (strongest reasonable form) before any verdict.
- [ ] **Ad hoc rescue / moving goalposts**: conditions added mid-argument to dodge
  a counterexample — legitimate only if the revised claim is then re-verified as a
  NEW claim.
- [ ] **Appeal to authority beyond its scope**: an expert cited outside their
  domain, or authority substituted for the argument itself (authorities set
  priors, they do not close questions).

## Audit output
For each failing item: `step/claim L → item (e.g. 4.2 or 10.3) → original quote →
impact (fatal / routine fix)`. Checked items with no findings → record "audit:
sections 1–10 clean" in the verdict — an audit that is not recorded is an audit
that cannot be trusted.
