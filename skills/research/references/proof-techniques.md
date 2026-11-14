# Reference — Proof Techniques

Taxonomy of proof strategies + when each applies + their traps. Load when proving
something that has no public proof yet (after an empty claim-verification), or when
choosing candidate fixes for gaps found in proof-verification.

## Quick selector

| Claim shape | First strategy | Backup |
|---|---|---|
| `P(n)` for all n ∈ ℕ | induction (weak) | strong induction / minimal counterexample |
| "no x satisfies P(x)" | contradiction | extremal/well-ordering |
| `P ⇒ Q` | direct | contraposition (`¬Q ⇒ ¬P`) — often smoother |
| "there exists x with P(x)" | explicit construction | non-constructive existence (only if needed) |
| "X is invariant under all allowed moves" | invariant/monovariant | case classification |
| "uncountable" | diagonalization | Cantor–Schröder–Bernstein bijection |
| "two objects share a property" | pigeonhole | probabilistic method |
| "least upper bound / extremal object" | supremum/extremal | sequential construction |
| combinatorial identities / recurrences | generating functions | transforms (Fourier/Laplace) |

## Strategies with detail

### Direct & contraposition
Start from definitions, push forward. **Trap:** silently using the converse of a
hypothesis (`P ⇒ Q` differs from `Q ⇒ P` — check the direction of every implication).

### Contradiction
Assume `¬Q`, derive an absurdity. **Traps:** the derived "absurdity" is merely
surprising, not logically contradictory; and the negated assumption mistyped
(rejecting part of Q while trying to prove Q).

### Induction (weak / strong / structural)
- Base + step — BOTH must be checked explicitly. **Trap:** the step holds for
  `n ≥ k` but the base `n₀` does not match `k` (off-by-one induction).
- Strong induction when the recursion calls smaller values that are not `n-1`.
  Structural induction for recursively defined structures (trees, formulas).
- Minimal-counterexample arguments = strong induction in reverse — good for
  "nothing exists" claims.

### Construction
For existence: give the object AND verify it satisfies ALL conditions (both
directions, as in counterexample-hunt step 7). **Trap:** constructions that quietly
use the axiom of choice — allowed, but name it.

### Diagonalization & pigeonhole
Diagonalization for "strictly more" (uncountability, undecidability). Pigeonhole for
"guaranteed collision". **Trap:** miscounting pigeons/holes or rounding the wrong way.

### Invariant / monovariant
Find a quantity unchanged (invariant) or moving one way (monovariant) under the
operations — for "impossible to reach", "process always terminates". Classics:
parity, mod m, total sum, area. **Trap:** an invariant that does not distinguish
start from goal states (true but useless).

### Extremal / supremum
Take an extremal object, show it has the property. **Trap:** assuming the extremum
EXISTS — existence needs compactness/completeness; in non-compact spaces a supremum
may be unattained.

### Probabilistic method
For existence: show the probability of the property is > 0. **Trap:** it is
non-constructive (the object is guaranteed but not given).

### Generating functions & transforms
For combinatorial identities/recurrences: encode as coefficients. **Trap:** swapping
sums and limits without checking the radius/conditions of convergence.

## Relation to the other workflows
- Reproving an existing result → start here only AFTER an empty claim-verification.
- Strategy keeps failing → the claim probably needs an extra hypothesis; probe with
  counterexample-hunt (drop one condition at a time, see which one blocks the proof).
- Once a draft proof exists → proof-verification, always.
