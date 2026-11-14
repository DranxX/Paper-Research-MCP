# Skills in this repo

Agent skills that pair with Paper-Research-MCP. Same format as any agent-skills
collection (SKILL.md router + `workflows/` + `references/`).

| Skill | Contents |
|---|---|
| [`research/`](research/) | general research methodology: literature scans, claim verification, proof verification, counterexample/falsification hunts, numeric sanity checks — uses the ProofWiki connector + the paper sources of this MCP |

## Install ("skills install something?")

A skill is a folder. Installing = **copy the skill folder into your agent's skills
directory** — the skill then auto-triggers on matching tasks (see the `description`
frontmatter in its `SKILL.md`).

```bash
git clone https://github.com/DranxX/Paper-Research-MCP
cd Paper-Research-MCP

# ZCode
mkdir -p ~/.zcode/skills && cp -r skills/research ~/.zcode/skills/

# Claude Code
mkdir -p ~/.claude/skills && cp -r skills/research ~/.claude/skills/

# Any other generic agent-skills location (`.agents/skills/`, etc.) — same idea:
cp -r skills/research <agent-skills-dir>/
```

Updating = copy the folder again (skill files are self-contained, no external state).

## MCP pairing (optional but recommended)

The skill is designed to pair with the **paper-research-mcp** MCP server from this
repo — the `proofwiki_*` connector and the paper sources (OpenAlex/arXiv/Crossref/…)
are what its workflows call. Without the MCP the skill still works: every workflow
has manual fallbacks (see `references/tool-map.md` inside the skill).

```jsonc
{ "mcpServers": { "paper-research": { "command": "uvx", "args": ["paper-research-mcp"] } } }
```
