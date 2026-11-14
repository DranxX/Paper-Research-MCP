# Reference — Tool Map (need → MCP connector → fallback)

Mapping of research needs → paper-research-mcp tools → manual fallbacks. All
workflows in this skill use this table. A `blocked` connector is not a workflow
failure — move to the fallback (rules 0.2 + §3 in SKILL.md).

## Field → sources

| Field | Connectors | Manual fallbacks |
|---|---|---|
| Math | `proofwiki_search`/`proofwiki_get`, `arxiv_search` (`cat:math.*`) | zbMATH Open (https://zbmath.org, free, MSC codes), OEIS (https://oeis.org) |
| Formal logic / philosophy / law | `proofwiki_search` (Logic pages: propositional & predicate calculus), `doaj_search`, `search_papers` | PhilPapers (https://philpapers.org), Stanford Encyclopedia of Philosophy (https://plato.stanford.edu), SSRN (law), official statute/court databases |
| CS / ML / AI | `arxiv_search` (`cat:cs.*`), `pwc_search`, `openreview_search`/`openreview_notes` | arXiv listing, OpenReview web, AlphaXiv (`alphaxiv_search`, key) |
| Physics | `inspire_search` | INSPIRE-HEP web |
| Life sciences / medicine | `openalex_search`, `crossref_search`, `doaj_search` | PubMed; prefer meta-analyses/systematic reviews |
| Education | `eric_search` | ERIC web |
| Social sciences / humanities | `openalex_search`, `doaj_search` | field portals |
| Multidisciplinary (broad sweep) | `search_papers` (federated, multi-keyword, year windows) | Google Scholar |
| China literature | `nssd_search`, `baidu_scholar_search`, `sciencedb_search` | CNKI web |
| Indonesia | `garuda_search`, `neliti_search`, `brin_search`, `onesearch_search`, `rama_search`, `moraref_search` | platform websites; `sinta_search` for accreditation |
| People / affiliations | `orcid_works` | ORCID web |

## Need → tool

| Need | MCP tool | Fallback |
|---|---|---|
| Find a canonical theorem/definition | `proofwiki_search` | https://proofwiki.org/wiki/Special:Search?search=<q> |
| Read a complete proof + prerequisites | `proofwiki_get` | open the page URL in a browser |
| Papers, multi-keyword parallel + year filters | `search_papers {queries:[], year_from, year_to}` | Google Scholar / zbMATH Open |
| Preprints by field category | `arxiv_search` (e.g. `cat:math.NT AND all:<term>`) | https://arxiv.org/list/<cat> |
| Broad metadata (citations, OA status) | `openalex_search` | https://openalex.org |
| Metadata, DOI-first (citations) | `crossref_search` / `crossref_doi` | https://search.crossref.org |
| Resolve a DOI → exact metadata | `crossref_doi {doi}` | https://doi.org/<doi> |
| Legal open-access full text | `unpaywall_resolve {doi}` | https://unpaywall.org |
| Peer-review trail (AI/ML venues) | `openreview_search` + `openreview_notes` | OpenReview web |
| Code implementations of papers | `pwc_search` | Papers with Code web |
| Retraction/status check | `crossref_doi` (publisher notices) | https://retractionwatch.com |
| Everything + statuses | `list_sources` | — |

## Efficient usage patterns

1. **Multi-keyword**: don't send one long query — split into
   `queries: [canonical term, synonym, "proof of <name>", "failed replication of <name>"]`;
   `search_papers` runs ALL of them in parallel and tags `matchedQueries` per item.
2. **Two year windows**: foundations (`year_to`) + frontier (`year_from`) —
   literature-scan step 2.
3. **Bot-wall skip**: `include_bot_wall: false` speeds things up (skips ProofWiki /
   Google Scholar / Indonesia scrapers) when only official-API sources are needed.
4. **`proofwiki_get` `empty`** = title not exact → back to `proofwiki_search`
   (proofwiki-guide §page conventions).
5. **ProofWiki content** carries CC BY-SA 3.0 in `meta` — include the attribution
   when quoting (rule 0.4 in SKILL.md).
6. **Premium connectors** (`ads_search`, `scopus_search`, `lens_search`,
   `dimensions_search`, `wos_search`, `alphaxiv_search`) return `auth-required`
   until their env var is set — use free equivalents or the fallbacks above.
