---
name: research
description: >
  General academic research methodology for any discipline: literature scans, verifying
  whether a claimed result actually exists and what its real status is, step-by-step
  validation of proofs, derivations, and structured arguments (mathematics, formal
  logic, computer-science correctness, legal reasoning, philosophy, theoretical
  science), falsification hunts (counterexamples, failed replications, contrary
  evidence), and numeric sanity checks. Pairs with paper-research-mcp (31 connectors:
  OpenAlex, Crossref, arXiv, ProofWiki, INSPIRE-HEP, ERIC, DOAJ, OpenReview, Papers
  with Code, Unpaywall, ORCID, China and Indonesia platforms) but degrades gracefully
  without it (manual fallbacks everywhere). Trigger when the user asks to survey a
  topic, find prior work, verify a claim/proof/argument/theorem, check whether a
  result is already known, disprove something, find counterexamples, or sanity-check
  quantitative reasoning. Do NOT trigger for trivial one-off lookups.
user-invocable: true
---

# Research

One skill for research-grade work across fields: finding prior results, verifying
claims, proofs, and arguments, falsifying what looks wrong, and mapping a
literature — with public evidence sources (OpenAlex, Crossref, arXiv, ProofWiki,
INSPIRE-HEP, DOAJ, ERIC, OpenReview, Papers with Code, Unpaywall, ORCID, China and
Indonesia platforms) accessed through the **paper-research-mcp** server when
connected, or manual fallbacks when not.

Structure: `workflows/` (execution procedures) + `references/` (knowledge base).

## 0. Rules that always apply

1. **Premises & definitions first, always.** Before touching any claim, normalize
   every term to its exact definition (ProofWiki `Definition:` pages, field-standard
   texts, statutes/precedent in law, operational definitions in empirical work, or
   the user's own definition) and make every premise explicit. An ambiguous claim is
   not verifiable — flag it and settle an explicit reading first.
2. **"Not found" ≠ "doesn't exist", and one empty source proves nothing.** Empty
   searches are reported as-is ("not found in: X, Y"), never inflated into "nobody
   has shown this". Match sources to the field
   ([references/tool-map.md](references/tool-map.md)) before judging novelty.
3. **Numerics never prove.** Computation only (a) falsifies fast, (b) reveals
   patterns, (c) tests boundaries. "Passed N cases" always carries that disclaimer.
4. **Attribute everything.** ProofWiki content is CC BY-SA 3.0 / GFDL — quoting or
   adapting requires page title + URL + license
   ([references/proofwiki-guide.md](references/proofwiki-guide.md)). Every factual
   result cites its source (DOI/URL); legal arguments cite the rule/precedent.
5. **Status labels are mandatory.** Every result is labeled: `established
   (reference)` / `established with conditions` / `contested` / `conjectured (open)`
   / `not found` / `refuted (counterexample or evidence)`. Unlabeled results are not
   presented.
6. **Gaps are reported per step.** Verification that finds a leap reports which
   step, what is missing, and candidate fixes — never a vague "looks right".
7. **Separate validity from soundness.** An argument can follow correctly from
   premises (valid) yet rest on a false premise (unsound) — verdicts state which
   one failed. See [references/proof-techniques.md](references/proof-techniques.md).

## 1. Task → workflow routing

| Situation | Workflow |
|---|---|
| Survey a field / annotated bibliography / find the gap | [workflows/literature-scan.md](workflows/literature-scan.md) |
| "Is this result real? is it known? what's its actual status?" | [workflows/claim-verification.md](workflows/claim-verification.md) |
| Validate a proof, derivation, or structured argument — math, formal logic, CS correctness, legal reasoning, philosophy, theoretical science | [workflows/proof-verification.md](workflows/proof-verification.md) |
| Suspect a claim is false / need disconfirmation — counterexamples, failed replications, contrary evidence, any field | [workflows/counterexample-hunt.md](workflows/counterexample-hunt.md) |
| Quick numeric check of a concrete claim (anytime) | [workflows/numeric-sanity.md](workflows/numeric-sanity.md) |

Chaining: **claim-verification → proof-verification** for formal results;
**claim-verification → counterexample-hunt** when suspicion grows; numeric-sanity
fires whenever the claim is concrete enough to compute. literature-scan stands
alone for survey tasks.

## 2. References (load when needed)

| Need | Reference |
|---|---|
| Field → which sources/connectors to trust, with fallbacks | [references/tool-map.md](references/tool-map.md) |
| ProofWiki: API, page conventions, wikitext, licensing | [references/proofwiki-guide.md](references/proofwiki-guide.md) |
| Proof strategies + general logic (valid forms, fallacies, validity vs soundness) | [references/proof-techniques.md](references/proof-techniques.md) |
| Rigor audit — formal arguments (§1–9), empirical claims (§10), fallacies (§11) | [references/rigor-checklist.md](references/rigor-checklist.md) |

## 3. Pairing with paper-research-mcp

The skill is designed to pair with the **paper-research-mcp** server (same repo).
Source discipline: **match the field to the connector** (full table in
[references/tool-map.md](references/tool-map.md)):

- **Math** — `proofwiki_search`/`proofwiki_get` (canon + complete proofs), `arxiv_search` (`cat:math.*`)
- **Formal logic / philosophy / law** — `proofwiki_search` (Logic pages: propositional
  & predicate calculus results), `doaj_search`, `search_papers`; PhilPapers / Stanford
  Encyclopedia of Philosophy / SSRN (manual)
- **CS / ML / AI** — `arxiv_search` (`cat:cs.*`), `pwc_search` (implementations), `openreview_search`/`openreview_notes` (peer review trails), `alphaxiv_search` (key)
- **Physics** — `inspire_search` (INSPIRE-HEP)
- **Multidisciplinary / life & social sciences** — `search_papers` (federated), `openalex_search`, `crossref_search`, `doaj_search`
- **Education** — `eric_search`
- **Open access & metadata** — `unpaywall_resolve`, `crossref_doi`, `orcid_works`
- **China platforms** — `nssd_search`, `baidu_scholar_search`, `aminer_search` (key), `sciencedb_search`, `cstr_resolve` (key)
- **Indonesia** — `garuda_search`, `sinta_search`, `onesearch_search`, `rama_search`, `moraref_search`, `neliti_search`, `brin_search`, `google_scholar_search`

Without the MCP: every workflow keeps running via the manual fallbacks in
[references/tool-map.md](references/tool-map.md). A `blocked` connector (bot-wall)
is never a workflow failure — move to the next source or the fallback.

> ⚠️ ProofWiki sits behind Cloudflare on some networks (`blocked` envelope) — that is
> not a workflow failure; open the URL manually in a browser or retry later. Details
> in [references/proofwiki-guide.md](references/proofwiki-guide.md).

## 4. Standard verdict format

For verification tasks, end with a labeled verdict:

```
VERDICT: ✅ sound (valid + premises hold) | ✅ valid with fixes | ⚠️ gaps found
       | ❌ invalid inference | ❌ unsound premise / refuted | 🔍 not found
CLAIM  : <one-line precise statement>
TRACE  : step/table → basis (definition/rule/theorem/data source) → status
GAPS   : <leaps + candidate fixes, if any>
SOURCES: <each with DOI/URL/citation; ProofWiki quotes carry CC BY-SA attribution>
```
