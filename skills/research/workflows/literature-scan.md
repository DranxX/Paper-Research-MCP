# Workflow — Literature Scan

**Goal:** survey a topic in any discipline → annotated bibliography + reading order +
visible research gaps.

## Steps

### 1. Map the field
- Area + sub-area (e.g. "optimal transport" ⊂ analysis/geometry; "RLHF robustness" ⊂ ML).
- Two keyword sets: **canonical terms** (theorem names, standard constructs) and
  **informal variants** (different communities name the same thing differently —
  "cobordism" vs "bordism", "graph" vs "network", "attention" vs "transformer layer").

### 2. Two time windows
Run `search_papers` with parallel `queries:`, twice:
- **Foundations:** `year_to` (early years of the area) → seminal papers, sort by
  citations (`cited_by_count` in openalex/crossref `extra`).
- **Frontier:** `year_from` (last ~5 years) → current directions.
Preprints for the frontier: `arxiv_search` with field categories
(`cat:cs.LG`, `cat:math.AG`, `cat:physics.*`, `cat:q-bio.*`, …).

### 3. Field-specific sources
| Field | Primary | Supplements |
|---|---|---|
| Math | arXiv `math.*`, `zbmath_search`, ProofWiki | zbMATH web for MSC browsing |
| Formal logic / philosophy / law | ProofWiki Logic pages, `doaj_search`, `search_papers` | PhilPapers, Stanford Encyclopedia of Philosophy, SSRN (manual) |
| CS / ML / AI | arXiv `cs.*`, `hf_search` | `pwc_search` (code), `openreview_search` (reviews/rebuttals) |
| Physics | `inspire_search` | arXiv `physics.*`/`gr-qc`/`hep-*` |
| Life sciences / medicine | `europepmc_search`, `pubmed_search` | prefer meta-analyses first |
| Education | `eric_search` | DOAJ |
| Social sciences / humanities | `openalex_search`, `doaj_search` | regional platforms |
| China literature | `nssd_search`, `baidu_scholar_search`, `sciencedb_search` | `aminer_search` (key) |
| Indonesia | `garuda_search`, `neliti_search`, `brin_search`, `onesearch_search` | `sinta_search` (accreditation), `rama_search` (theses) |
| People / affiliations | `orcid_works` | — |

Full mapping + fallbacks: [references/tool-map.md](../references/tool-map.md).

### 4. Canon of definitions & terminology
ProofWiki (`proofwiki_search`/`proofwiki_get`) for standard definitions; field
standards elsewhere. Build a **terminology map** — the same concept under different
names across papers is the #1 cause of false "novelty".

### 5. Access check
`unpaywall_resolve` per core DOI — mark what can be read now vs needs institutional
access. Unreadable papers still enter the bibliography with abstract + DOI.

### 6. Reading order
1. **Textbook / definitions** (ProofWiki `Definition:` pages + standard texts)
2. **Best recent survey**
3. **Seminal papers** (highest-cited from the foundations window)
4. **Frontier** (last 5 years, grouped by research line)

### 7. Output

| # | Title | Year | Source | Role (foundation/survey/frontier) | Access | 1–2 line note |
|---|---|---|---|---|---|---|

Plus: **terminology map** and **visible gaps** ("A and B are both active but do not
cite each other"; "the X direction is claimed only in non-peer-reviewed preprints").

## Fallback without MCP
Google Scholar → field portal (zbMATH/PubMed/arXiv) → never conclude "no literature"
from a single site.
