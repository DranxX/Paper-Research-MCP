# Workflow — Proof Verification

**Goal:** validate a proof or formal/logical argument step by step — the user's own,
from a paper, or from ProofWiki — down to a labeled verdict, not an impression of
"seems right".

**Load first:** [references/rigor-checklist.md](../references/rigor-checklist.md)
(catalog of classic failures — required for step 4).

## Input
`claim + proof` (text). If the proof only exists in a paper/PDF, fetch it first:
`unpaywall_resolve`/`crossref_doi` for DOIs, or a ProofWiki page via `proofwiki_get`
(its wikitext shows prerequisite wikilinks — useful in step 2).

## Steps

### 1. Re-formalize
- Restate the claim with explicit quantifiers `∀/∃`, quantified domains, and
  quantifier **order**. `∀∃` vs `∃∀` differ in meaning — confirm the claim under
  review really asserts what you wrote.
- For every term: which exact definition applies? (ProofWiki `Definition:` page via
  `proofwiki_search`/`proofwiki_get`, standard text, or the user's definition.)
  **Ambiguous definition = stop**, flag it, settle an explicit one.

### 2. Build the dependency tree
List every result the proof uses (axioms, definitions, prior theorems). For ProofWiki
proofs: extract the wikilinks from the wikitext. For each used result:
- is its statement exactly what is needed here (not a variant)?
- are its hypotheses actually satisfied in this context? (The most frequent gap:
  a theorem invoked outside its hypotheses.)

### 3. Trace line by line
Table: `step → statement → basis (definition/axiom/theorem/previous step) → status`.
- Every inference must have an explicit basis. A leap is flagged ⚠️, never papered
  over with "obviously" / "it is easy to see".
- Dangerous phrases that must always be unpacked: "it is obvious", "clearly", "one
  easily shows", "by a standard argument", "similarly".

### 4. Audit hidden assumptions
Run [references/rigor-checklist.md](../references/rigor-checklist.md) for: division
by zero/non-invertible objects, quantifier swaps, vacuous/empty cases, interval
endpoints, limit/integral interchanges without uniformity, induction with a failing
base case, circular reasoning, "sufficiently large" never established, objects whose
existence is assumed without construction.

### 5. Boundary tests (degeneration)
Substitute degenerate cases into every step: `0, 1, -1`, empty sets, dimension 1,
trivial structures, `→ ∞`. A step that explodes on degenerate input usually hides an
assumption. For concrete claims, invoke [numeric-sanity.md](numeric-sanity.md) here.

### 6. Cross-check against reference proofs
If claim-verification found an alternative proof (ProofWiki/text/paper): compare
**structure**. Structural divergence is not automatically an error — but every
divergence is an extra inspection point. A proof that departs at the same place the
reference proof also needs its heaviest machinery → that spot gets priority scrutiny.

### 7. Verdict

| Label | Requirement |
|---|---|
| ✅ valid | every step has an explicit basis + clean audit + boundaries safe |
| ✅ valid with fixes | a step lacks a basis, but the fix is routine (list the fixes) |
| ⚠️ gaps | non-routine leaps/hidden assumptions — list per step + candidate strategies |
| ❌ refuted | a counterexample was found (formalize via [counterexample-hunt.md](counterexample-hunt.md)) |

Final output uses the VERDICT format from SKILL.md §4. Quote the ORIGINAL step text
when flagging a gap — never paraphrase until the risk disappears.
