# Skills di repo ini

Skill agent yang berpasangan dengan Paper-Research-MCP. Format sama dengan koleksi
`Collection/Markdown/Skills` (SKILL.md router + `workflows/` + `references/`).

| Skill | Isi |
|---|---|
| [`math-research/`](math-research/) | riset matematis: theorem-hunt, proof-verification, counterexample-hunt, literature-scan, numeric-sanity — memakai connector ProofWiki + sumber paper MCP |

## Install ("skills install something?")

Skill = folder. Install = **salin folder skill ke direktori skills agent-mu** —
lalu skill auto-trigger pada tugas yang cocok (lihat frontmatter `description` di
`SKILL.md`-nya).

```bash
git clone https://github.com/DranxX/Paper-Research-MCP
cd Paper-Research-MCP

# ZCode
mkdir -p ~/.zcode/skills && cp -r skills/math-research ~/.zcode/skills/

# Claude Code
mkdir -p ~/.claude/skills && cp -r skills/math-research ~/.claude/skills/

# Lokasi generik agent-skills lain (`.agents/skills/`, dsb.) — sama saja:
cp -r skills/math-research <direktori-skills-agent>/
```

Update = salin ulang folder (file skill self-contained, tidak ada state luar).

## Pasangan MCP (opsional tapi disarankan)

Skill didesain pair dengan MCP server **paper-research-mcp** ini — connector
`proofwiki_*` + sumber paper (OpenAlex/arXiv/Crossref/…) dipakai oleh workflow-nya.
Tanpa MCP pun skill tetap jalan: setiap workflow punya fallback manual
(lihat `references/tool-map.md` di dalam skill).

```jsonc
{ "mcpServers": { "paper-research": { "command": "uvx", "args": ["paper-research-mcp"] } } }
```
