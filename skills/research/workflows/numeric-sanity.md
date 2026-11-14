# Workflow — Numeric Sanity

**Goal:** quick computational checks of concrete claims — to **falsify fast, reveal
patterns, and test boundaries**. Never proves anything (rule 0.3 in SKILL.md).

## Principles
- Agreement with numerics ≠ proof. DISAGREEMENT = the claim is false OR a
  constant/boundary/definition was mistranscribed — both are valuable findings.
- Always report: "passed N cases including degenerate ones" plus the disclaimer that
  this is not proof.

## Steps

### 1. Concretize the claim
Turn the claim into a computable function: inputs (objects + parameters), expected
output. Works for mathematical formulas **and** reported statistics (percentages,
effect sizes, base rates from a paper's own tables). If it cannot be concretized →
not a numeric candidate; return to [proof-verification.md](proof-verification.md) or
claim-verification.

### 2. Tiered test cases
1. **Canonical**: the most standard example (theory's ruler — must be right, else the
   transcription is wrong).
2. **Random**: 100–1000 random instances across the parameter space.
3. **Degenerate**: `0, 1, -1`, empty sets, dimension 1, singular/near-singular.
4. **Adversarial**: values that usually trigger failure — very large/small, alternating
   signs, irrationals (π, √2) where rationals were assumed, boundary values of stated
   ranges.

### 3. Small script, one file
Plain Python, or SymPy if available (runs locally even with MCP/network down). Same
shape every time:

```python
def claim(x): ...        # exact transcription of the claim
def expectation(x): ...  # what the claim predicts
cases = [canonical] + [random_cases(200)] + [degenerate] + [adversarial]
for c in cases: compare(claim(c), expectation(c), tol=...)
```

- Compare with an explicit tolerance (`tol`) — and report the tolerance.
- A small, consistent mismatch (e.g. always ≈ 10⁻¹⁰ relative) signals a wrong
  constant/normalization in the transcription or the claim — trace it, don't average
  it away.

### 4. Invariant checks (for structural claims)
Many claims are easier to test as invariants: "result is always positive", "monotone
in the parameter", "symmetric under swapping", "total mass conserved", "reported
counts sum to the stated totals". Test invariants across all cases.

### 5. Output

| Case | Expected | Got | Status |
|---|---|---|---|

Reportable numeric verdicts:
- ❌ "claim FAILS on cases: … (concrete, reproducible)" → straight to
  [counterexample-hunt.md](counterexample-hunt.md) for formalization/evidence.
- ✅ "passed N cases (canonical + random + degenerate + adversarial, tol=…)" — with
  the numeric disclaimer; then continue proving via
  [references/proof-techniques.md](../references/proof-techniques.md) or claim
  verification.
