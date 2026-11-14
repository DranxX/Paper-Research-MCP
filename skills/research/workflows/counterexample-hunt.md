# Workflow — Counterexample Hunt

**Goal:** disconfirm a claim with an explicit, precise counterexample — formal for
mathematical claims, empirical evidence for factual claims — not an intuition that
"it seems false".

## Steps

### 1. Identify the attack surface
- Hypotheses = the list of conditions. **Each condition is a potential attack
  point**: remove one condition and a classic counterexample usually appears
  (claims without commutativity, completeness, compactness, continuity, random
  sampling, …).
- Map the parameter space: dimension, size, function class, structure type — or, for
  empirical claims, population/setting/measure.

### 2. Small and degenerate cases first
Cheap before expensive: `n = 0, 1, 2` · dimension 1 · empty/singleton sets · trivial
structures · constants `0, 1, -1, π` · sign flips · boundary values of the stated
ranges. Many "proven" statements hold only for `n ≥ 2` and fail silently at `n = 1`.

### 3. Extremal parameters
`→ 0`, `→ ∞`, functions non-differentiable at a single point, very slowly convergent
sequences, near-degenerate objects (determinant ≈ 0, distances ≈ 0), populations at
the edges of the claimed scope.

### 4. Famous families (when the claim smells like analysis/structure)
Match the claim against families designed to break the same intuition:

| Family | Breaks claims of the type |
|---|---|
| Weierstrass function | "continuous ⇒ differentiable somewhere dense" |
| Cantor set | "infinite set ⇒ contains an interval" |
| Dirichlet function | "Riemann-integrable for any function" |
| `x ↦ sin(1/x)` near 0 | "bounded ⇒ limit exists" |
| `∑ 1/n` | "terms → 0 ⇒ series converges" |
| large primes / small twin pairs | number theory "for all n" claims |
| small cycle/bipartite/complete graphs | combinatorics "for all graphs" claims |

### 5. For empirical claims: falsify with evidence, not vibes
- **Search for existing refutation first** (cheaper than constructing one):
  `queries: ["X failed replication", "no effect of X", "critique of X", "X retraction"]`,
  citation trail via `openalex_search`/`semantic_scholar_search`, meta-analyses first.
- **Recompute from the paper's own numbers** ([numeric-sanity.md](numeric-sanity.md)):
  percentages, effect sizes, base rates — arithmetic errors are common and decisive.
- **Test the claim on edge populations/settings** it was never validated on, and
  check whether the observed association survives obvious confounds.
- A refuting *paper* is evidence; a refuting *computation from reported data* is a
  check; only an explicit counterexample/failed replication settles it.

### 6. Numeric first, formal second
Use [numeric-sanity.md](numeric-sanity.md) to search for candidates (random search +
adversarial cases). A numeric candidate is **not** the final counterexample.

### 7. Formalize the counterexample
- EXPLICIT construction (never "there exists" without construction).
- Verify both directions: the object satisfies ALL hypotheses of the claim, and the
  conclusion fails for it. A counterexample that does not meet the hypotheses
  refutes nothing.
- Re-check definitions: the counterexample must use the SAME definitions as the
  claim (classic error: refuting a continuity claim using a uniform-continuity notion).

### 8. If nothing is found
"No counterexample found among N candidates" ≠ the claim is true — report that
plainly, then continue with [proof-verification.md](proof-verification.md) (the claim
may well be true, and the falsification effort usually reveals which hypothesis
carries the weight).

### 9. Output
```
COUNTEREXAMPLE / EVIDENCE: <explicit construction or citation with DOI/URL>
HYPOTHESES SATISFIED: <proof per condition>
CONCLUSION FAILS AT: <explicit evaluation / reported result>
CLAIM STATUS: ❌ refuted as stated / ⚠️ refuted only without condition X (claim must add condition X)
```
