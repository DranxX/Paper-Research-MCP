# Reference — Tool Map (need → ScholarMesh tool → fallback)

Mapping of research needs → scholarmesh MCP tools → manual fallbacks. All workflows
in this skill use this table. A `blocked` connector is not a workflow failure — move
to the fallback (rules 0.2 + §3 in SKILL.md).

## Field → sources

| Field | Connectors | Manual fallbacks |
|---|---|---|
| Math | `proofwiki_search`/`proofwiki_get`, `zbmath_search`, `arxiv_search` (`cat:math.*`) | zbMATH web (MSC codes), OEIS (https://oeis.org) |
| Formal logic / philosophy / law | `proofwiki_search` (Logic pages), `doaj_search`, `search_papers` | PhilPapers (https://philpapers.org), Stanford Encyclopedia of Philosophy (https://plato.stanford.edu), SSRN (law), official statute/court databases |
| CS / ML / AI | `arxiv_search` (`cat:cs.*`), `hf_search`, `pwc_search`, `openreview_search`/`openreview_notes` | arXiv listing, OpenReview web, AlphaXiv (`alphaxiv_search`, key) |
| Physics / astronomy | `inspire_search`, `ads_search` (key) | INSPIRE-HEP web, https://ui.adsabs.harvard.edu |
| Biomed / life sciences | `europepmc_search` (+ `europepmc_fulltext` for OA text), `pubmed_search` | PubMed web; prefer meta-analyses/systematic reviews |
| Education | `eric_search` | ERIC web |
| Social sciences / humanities | `openalex_search`, `doaj_search` | field portals |
| Multidisciplinary (broad sweep) | `search_papers` (federated, multi-keyword, year windows) | Google Scholar |
| Datasets / software / OA books | `zenodo_search`, `datacite_search`, `osf_search`, `doab` (manual: https://directory.doabooks.org) | publisher repositories |
| EU / Global South aggregation | `openaire_search`, `core_search` (key, free registration) | OpenAIRE explore web |
| China literature | `nssd_search`, `baidu_scholar_search` (key), `sciencedb_search` | CNKI web |
| Indonesia | `garuda_search`, `neliti_search`, `brin_search`, `onesearch_search`, `rama_search`, `moraref_search` | platform websites; `sinta_search` for accreditation |
| People / affiliations | `orcid_works` | ORCID web |

## Need → tool

| Need | MCP tool | Fallback |
|---|---|---|
| Find a canonical theorem/definition | `proofwiki_search` | https://proofwiki.org/wiki/Special:Search?search=<q> |
| Read a complete proof + prerequisites | `proofwiki_get` | open the page URL in a browser |
| Math literature w/ MSC classification | `zbmath_search` | https://zbmath.org |
| Papers, multi-keyword parallel + year filters | `search_papers {queries:[], year_from, year_to}` | Google Scholar |
| Preprints by field category | `arxiv_search` (e.g. `cat:math.NT AND all:<term>`) | https://arxiv.org/list/<cat> |
| Broad metadata (citations, OA status) | `openalex_search` | https://openalex.org |
| Metadata, DOI-first (citations) | `crossref_search` / `crossref_doi` | https://search.crossref.org |
| Resolve a DOI → exact metadata | `crossref_doi` | https://doi.org/<doi> |
| Biomed search (49M records, OA flags) | `europepmc_search` | https://europepmc.org |
| Biomed OA full text | `europepmc_fulltext {pmcid}` | https://europepmc.org/article/<pmcid> |
| PubMed citations (MeSH expansion) | `pubmed_search` | https://pubmed.ncbi.nlm.nih.gov |
| EU aggregated products (150M+) | `openaire_search` | https://explore.openaire.eu |
| Datasets/software/preprints (CERN) | `zenodo_search` | https://zenodo.org |
| DOI records for datasets/software | `datacite_search` | https://datacite.org |
| OSF preprints / project nodes | `osf_search` | https://osf.io |
| Deepest OA full-text index | `core_search` (key, free registration) | https://core.ac.uk |
| Legal open-access location per DOI | `unpaywall_resolve` | https://unpaywall.org |
| Peer-review trail (AI/ML venues) | `openreview_search` + `openreview_notes` | OpenReview web |
| Community-trending ML papers | `hf_search` | https://huggingface.co/papers |
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
   Google Scholar / regional scrapers) when only official-API sources are needed.
4. **`proofwiki_get` `empty`** = title not exact → back to `proofwiki_search`
   (proofwiki-guide §page conventions).
5. **Biomed chain**: `europepmc_search` → `extra.pmcid` (+ `in_europepmc: Y`) →
   `europepmc_fulltext` for the OA full text.
6. **ProofWiki content** carries CC BY-SA 3.0 in `meta` — include the attribution
   when quoting (rule 0.4 in SKILL.md).
7. **Key-gated sources** (`core_search`, `ads_search`, `scopus_search`, `lens_search`,
   `dimensions_search`, `wos_search`, `alphaxiv_search`, `aminer_search`,
   `baidu_scholar_search`, `cstr_resolve`) return `auth-required` until their env var
   is set — use free equivalents or the fallbacks above.
