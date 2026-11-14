# Workflow — Claim Verification

**Goal:** before relying on a claimed result — or building on it — establish that it
exists and what its real status is: `established`, `established with conditions`,
`contested`, `conjectured (open)`, or `not found`. Applies to theorems, empirical
findings, and folk claims alike.

## Steps

### 1. Formalize the claim
- **Formal (math/logic):** one precise statement — objects, hypotheses, conclusion,
  explicit quantifiers (`∀x ∈ A: P(x)`).
- **Empirical:** one operational statement — population, intervention/effect,
  conditions, effect size, scope. "X improves memory" is not a claim; "X improved
  recall scores by ~15% in 18–25 y/o undergraduates (n=…) after 4 weeks" is.
- Identify the field — it selects the sources (steps 2–3 and
  [references/tool-map.md](../references/tool-map.md)).

### 2. Named-result lookup
- Search for the **canonical name plus synonyms** ("Bayes' theorem" vs "Bayes rule";
  names differ across traditions and languages).
- Math: `proofwiki_search` → `proofwiki_get` for the exact statement + proof status +
  prerequisite wikilinks. Physics: `inspire_search`. General: `search_papers`
  (parallel `queries: [informal claim, "proof of X", "X theorem generalization"]`).
- Sequences/integer claims → OEIS (manual: https://oeis.org).

### 3. Literature search for the claim itself
`search_papers` with multi-keyword + year windows when relevant (frontier: `year_from`).
Preprints: `arxiv_search` with the right category (`cat:cs.*`, `cat:math.*`,
`cat:q-bio.*`, …). Literature-scan details: [literature-scan.md](literature-scan.md).

### 4. For empirical claims: check contestation, not just existence
- Citations of the original work: `openalex_search`/`semantic_scholar_search` — is it
  built on, corrected, or contradicted?
- Search explicitly for disconfirmation:
  `queries: ["X failed replication", "no effect of X", "X retraction", "critique of X"]`.
- Look for **meta-analyses / systematic reviews** first — they weigh the whole field,
  not one paper.
- Retraction/status check: retraction watch (manual: https://retractionwatch.com),
  publisher notices via `crossref_doi`.

### 5. Compare the exact conditions
Similar is not the same. Differences that change everything: finite vs infinite
dimension; sample vs population; correlation vs causation; dose/duration; the
hypotheses of the theorem vs the claim's assumptions; one country/species/cohort vs
another. Produce a small comparison table (claim conditions vs found-result conditions).

### 6. Output: status table

| Claim | Status | Best reference | Where the evidence lives |
|---|---|---|---|
| … | `established` / `established with conditions` / `contested` / `conjectured (open)` / `not found` | name + year + DOI/URL | ProofWiki page / arXiv id / journal (paywalled?) / meta-analysis |

**Routing:**
- A public proof/derivation exists → [proof-verification.md](proof-verification.md).
- An empirical result backs it → audit study quality with the empirical section of
  [references/rigor-checklist.md](../references/rigor-checklist.md).
- Only weaker variants found → flag the gap: "the strong form the user wants was not
  found; the weak form is established".
- Suspicion grows after verification → [counterexample-hunt.md](counterexample-hunt.md).
- Nothing found anywhere → report "not found in: <list of sources searched>"
  (rule 0.2) and route to original work.

## Fallback without MCP
Google Scholar → zbMATH Open (math reviews, free) → PubMed (biomed) → arXiv listing;
field-specific portals per [references/tool-map.md](../references/tool-map.md).
