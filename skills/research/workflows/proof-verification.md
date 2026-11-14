# Workflow — Proof & Argument Verification

**Goal:** validate ANY chain from premises to conclusion — a mathematical proof, a
formal logic derivation, a program-correctness argument, a theoretical derivation in
science, a legal argument, or a philosophical argument — down to a labeled verdict.
Two independent questions, answered separately: is the chain **valid** (each step
follows by the rules) and is it **sound** (the premises actually hold)?

**Load first:** [references/rigor-checklist.md](../references/rigor-checklist.md)
(required for step 4: §1–9 formal machinery, §10 empirical, §11 fallacies) and the
valid-forms/fallacies table in
[references/proof-techniques.md](../references/proof-techniques.md).

## What "proof" means per field — the procedure is the same for all

| Field | Premises | Inference rules | What a refutation looks like |
|---|---|---|---|
| Mathematics | definitions, axioms, prior theorems | deductive rules | countermodel: object meeting the hypotheses, failing the conclusion |
| Formal logic | axioms, assumptions | natural deduction / calculus rules | model with true premises, false conclusion; invalid form instance |
| CS correctness | spec, invariants, contracts | program logic / induction on execution | input that breaks the invariant |
| Theoretical science | accepted theory + approximations | derivation | regime where the approximation breaks; violated prediction |
| Law | facts + legal rules (statutes, precedent) | legal syllogism | contrary precedent; fact pattern outside the rule's scope |
| Philosophy | stated premises | valid inference forms | counterexample to a premise or to the inference form |

## Input
`claim + argument` (text). If it only exists in a paper/PDF: `unpaywall_resolve`/
`crossref_doi` for DOIs; ProofWiki pages via `proofwiki_get` (wikitext shows
prerequisite wikilinks — step 2); statutes/precedent cited in legal arguments —
fetch the actual text, never a paraphrase.

## Steps

### 1. Re-formalize the claim and the premises
- State the conclusion with explicit quantifiers `∀/∃` and quantifier **order**
  (`∀∃` vs `∃∀` differ in meaning).
- List EVERY premise, including the unstated ones you will audit later. In law:
  facts asserted + rule invoked. In science: theory + approximations made. In
  philosophy: each numbered premise.
- Resolve every term to an exact definition (ProofWiki `Definition:` page via
  `proofwiki_search`/`proofwiki_get`, standard text, statute text, operational
  definition). **Ambiguity = stop**, flag it, settle an explicit reading.

### 2. Build the dependency tree
List every authority the argument invokes (axioms, theorems, statutes, precedents,
theories, prior studies). For each:
- is its statement exactly what is needed here (not a variant)?
- are ITS premises satisfied in this context? (Most frequent gap: an authority
  invoked outside its hypotheses/scope — a theorem outside its assumptions, a
  precedent distinguishable on its facts, a study overgeneralized beyond its sample.)

### 3. Trace step by step
Table: `step → statement → basis (definition/rule/theorem/precedent/previous step) → status`.
- Every inference must have an explicit basis. A leap is flagged ⚠️, never papered
  over with "obviously" / "clearly" / "similarly" / "by a standard argument" —
  those phrases always get unpacked.
- Check the FORM of each inference against the valid-forms table
  ([references/proof-techniques.md](../references/proof-techniques.md)): modus
  ponens/tollens are valid; affirming the consequent, denying the antecedent, and
  converse/inverse errors on quantified conditionals are NOT — they are verdict
  changers (❌ invalid inference), not stylistic issues.

### 4. Audit hidden assumptions
Run [references/rigor-checklist.md](../references/rigor-checklist.md): §1–9 for
formal machinery (quantifiers, division/invertibility, degenerate cases, limits,
logic structure, definitions, probability, finite/infinite), §11 for informal
fallacies (equivocation, question-begging, false dilemma, hasty generalization,
straw man vs steelman, ad hoc rescue).

### 5. Boundary tests
Substitute degenerate/boundary cases into every step: `0, 1, -1`, empty sets,
dimension 1, trivial structures, `→ ∞` for formal arguments; the edge of the
rule's scope for legal arguments; the regime where the approximation breaks for
theoretical science. A step that explodes at the boundary usually hides an
assumption. For concrete claims, invoke [numeric-sanity.md](numeric-sanity.md).

### 6. Cross-check against reference arguments
If claim-verification found an alternative argument (ProofWiki/text/paper/precedent
line): compare **structure**. Divergence is not automatically an error — but every
divergence is an extra inspection point, and divergence at the spot where the
reference argument needs its heaviest machinery gets priority scrutiny.

### 7. Verdict

| Label | Meaning |
|---|---|
| ✅ sound | valid AND premises hold (cite the support for the premises) |
| ✅ valid with fixes | follows correctly, but a premise needs support/boundary repair — list the fixes |
| ⚠️ gaps | leaps/hidden assumptions that are non-routine — list per step + candidate strategies |
| ❌ invalid inference | the form itself fails (name the fallacy / give the countermodel) |
| ❌ unsound premise | form is fine, a premise is false (cite the counterexample/evidence) |

Final output uses the VERDICT format from SKILL.md §4. Quote the ORIGINAL step text
when flagging a gap — never paraphrase until the risk disappears.
