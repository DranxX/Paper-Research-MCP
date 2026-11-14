# Workflow — Counterexample & Disconfirmation Hunt

**Goal:** disconfirm a claim with an explicit, precise counterexample or contrary
evidence — formal (math, logic, CS), doctrinal (law), or empirical — not an
intuition that "it seems false".

## The logic (the whole mechanism)

A universal claim `∀x P(x)` is destroyed by a single instance of `¬P(x)`. An
inference form is destroyed by one case with true premises and a false conclusion.
Everything below is strategy for FINDING that one instance. Finding nothing does
not prove the claim — it only fails to refute it.

| Field | The "∀ claim" | What kills it |
|---|---|---|
| Math | theorem "for all objects satisfying H, C holds" | object satisfying every H, failing C |
| Logic | inference claimed valid | case with true premises, false conclusion |
| CS correctness | "function/spec never does X" | input producing X |
| Law | "rule applies to all such cases" | contrary precedent, or fact pattern outside the rule's scope |
| Empirical | "X always/only raises Y" | documented population/setting where it fails; failed replication |
| General/universal statement | "all A are B" | one A that is not B |

## Steps

### 1. Identify the attack surface
- Hypotheses/conditions = the claim's stated scope. **Each condition is a potential
  attack point**: remove one and a classic counterexample usually appears (claims
  without commutativity, completeness, compactness, continuity, random sampling,
  without "within jurisdiction X", without "under condition Y", …).
- Map the parameter space: dimension, size, function class, structure type — or,
  for empirical claims, population/setting/measure; for legal claims, fact patterns.

### 2. Small and degenerate cases first
Cheap before expensive: `n = 0, 1, 2` · dimension 1 · empty/singleton sets · trivial
structures · constants `0, 1, -1, π` · sign flips · boundary values of the stated
ranges. Many "proven" statements hold only for `n ≥ 2` and fail silently at `n = 1`.

### 3. Extremal parameters
`→ 0`, `→ ∞`, functions non-differentiable at a single point, very slowly convergent
sequences, near-degenerate objects (determinant ≈ 0, distances ≈ 0), populations at
the edges of the claimed scope.

### 4. Famous families (when the claim smells like analysis/structure)
Match the claim against families designed to break the same intuition —
math-specific but widely imitated:

| Family | Breaks claims of the type |
|---|---|
| Weierstrass function | "continuous ⇒ differentiable somewhere dense" |
| Cantor set | "infinite set ⇒ contains an interval" |
| Dirichlet function | "Riemann-integrable for any function" |
| `x ↦ sin(1/x)` near 0 | "bounded ⇒ limit exists" |
| `∑ 1/n` | "terms → 0 ⇒ series converges" |
| large primes / small twin pairs | number theory "for all n" claims |
| small cycle/bipartite/complete graphs | combinatorics "for all graphs" claims |

For logic: run the inference form over truth-table edges (empty domain for
quantified forms, boundary valuations). For CS: adversarial inputs — empty/unicode/
negative/overflow values, race interleavings.

### 5. For empirical claims: falsify with evidence, not vibes
- **Search for existing refutation first** (cheaper than constructing one):
  `queries: ["X failed replication", "no effect of X", "critique of X", "X retraction"]`,
  citation trail via `openalex_search`/`semantic_scholar_search`, meta-analyses first.
- **Recompute from the paper's own numbers** ([numeric-sanity.md](numeric-sanity.md)):
  percentages, effect sizes, base rates — arithmetic errors are common and decisive.
- **Test the claim on edge populations/settings** it was never validated on, and
  check whether the association survives obvious confounds
  ([references/rigor-checklist.md](../references/rigor-checklist.md) §10).
- A refuting *paper* is evidence; a refuting *computation from reported data* is a
  check; only an explicit counterexample/failed replication settles it.

### 6. For legal/doctrinal claims
- Search for **contrary authority**: `queries: ["<rule> exception", "limitation of
  <rule>", "contra <precedent>"]` (manual: official statute books, court databases,
  SSRN for commentary).
- Build a fact pattern at the rule's boundary: same key facts, one element missing
  → if the rule's conclusion would still be asserted, the rule's scope is wrong.
- Cite the exact text (statute/article/paragraph), never a summary.

### 7. Numeric first, formal second
Use [numeric-sanity.md](numeric-sanity.md) to search for candidates (random search +
adversarial cases). A numeric candidate is **not** the final counterexample.

### 8. Formalize the counterexample
- EXPLICIT construction (never "there exists" without construction; for logic: the
  full valuation/model; for law: the complete fact pattern).
- Verify both directions: the instance satisfies ALL the claim's hypotheses/scope,
  and the conclusion fails for it. A counterexample that does not meet the
  hypotheses refutes nothing.
- Re-check definitions: the counterexample must use the SAME definitions/rules as
  the claim (classic error: refuting a continuity claim with a uniform-continuity
  notion; refuting a statute-based claim with a different jurisdiction).

### 9. If nothing is found
"No counterexample found among N candidates" ≠ the claim is true — report that
plainly, then continue with [proof-verification.md](proof-verification.md) (the
claim may well be true, and the falsification effort usually reveals which
hypothesis carries the weight).

### 10. Output
```
COUNTEREXAMPLE / CONTRARY EVIDENCE: <explicit construction, valuation, fact pattern,
                                    or citation with DOI/URL>
HYPOTHESES/SCOPE SATISFIED: <proof per condition>
CONCLUSION FAILS AT: <explicit evaluation / reported result>
CLAIM STATUS: ❌ refuted as stated / ⚠️ refuted only without condition X (claim must add condition X)
```
