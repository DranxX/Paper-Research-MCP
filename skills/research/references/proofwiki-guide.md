# Reference — ProofWiki Guide

What ProofWiki is, how to use it through the MCP, page conventions, and licensing.

## What it is
[ProofWiki](https://proofwiki.org) — a community wiki holding **definitions, theorems,
and complete proofs** for classical to intermediate mathematics. Strengths: proofs are
structured, link to their prerequisites via wikilinks, and serve as cross-book
reference. Weaknesses (stated honestly): not formally peer-reviewed — canonical
theorems are heavily cross-checked, niche topics can have gaps; for publishable work,
cross-check primary sources.

## Access via ScholarMesh (scholarmesh MCP)
Two tools in the `proofwiki` connector (MediaWiki API `api.php`, free, no key):

| Tool | For | Notes |
|---|---|---|
| `proofwiki_search {query, limit}` | find theorem/definition pages by name | returns snippet + wordcount + `last_edit` |
| `proofwiki_get {page}` | fetch the full wikitext of one page | prerequisite wikilinks visible in the wikitext |

**Cloudflare:** ProofWiki sits behind Cloudflare. From clean-IP networks it usually
returns 200; elsewhere you get a JS challenge → `blocked` envelope + manual fallback
URL. That is not a workflow failure: open the URL in a browser or retry later. Probe
14 Nov 2026 (sandbox network): challenge → blocked.

## Page conventions (important for `proofwiki_get`)
- Titles must be **exact**. Common shapes:
  - Theorems: `Pythagorean Theorem`, `Cantor's Theorem`, `Hahn-Banach Theorem`
  - Definitions: `Definition:Metric Space`, `Definition:Eigenvector`
  - Categories: `Category:Proofs`, `Category:Theorems`, `Category:Axioms` — for
    browsing structure, not `proofwiki_get`.
- The right flow: **search first → take the exact title → get**.
  (Common mistake: `get` with an invented title → `empty`.)

## Wikitext & the dependency tree
Wikitext is not dead HTML — it carries extractable structure:
- `[[Definition:Metric Space]]`, `[[Hahn-Banach Theorem]]` — wikilinks to
  **prerequisites**: collect them for the proof's dependency tree (used by
  proof-verification step 2).
- `Proof` sections are usually split per case/variant (`Proof 1`, `Proof for finite
  case`) — match the variant to the claim being validated.
- Category links at the bottom → sibling theorems for cross-checking.

## License & attribution (MANDATORY — rule 0.4 in SKILL.md)
ProofWiki content is **CC BY-SA 3.0 / GFDL dual-licensed**. When quoting or adapting
(not just reading): cite `"Source: ProofWiki — <page title> (<URL>), CC BY-SA 3.0"`.
The `ok` envelopes already carry this attribution string in `meta` and
`extra.attribution`.
- Adapting proofs for publication → the derivative is also BY-SA bound; verify
  against primary sources (standard texts) as well.
- Reading for your own verification → no public obligation, but citing is good
  practice.

## Limitations to state to the user
1. Not formally peer-reviewed — cross-check canonical statements against standard
   texts for serious work.
2. Coverage leans toward "classical curriculum" mathematics — frontier research
   lives on arXiv.
3. Theorem names vary across traditions (UK/US, math/physics) — search synonyms
   (claim-verification step 2).
