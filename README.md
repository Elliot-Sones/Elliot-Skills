# Elliot Skills

Personal library of Claude Code skills, organized by domain. This repo is the source of truth; skills are deployed from here into the projects that need them.

## Structure

- `learning/` : study, comprehension, and research workflows
- `engineering/` : software, data, and ML engineering
- `finance/` : financial analysis and tracking

Each section will hold skill folders in the standard Agent Skills format: a folder containing a `SKILL.md` (YAML frontmatter with name and description, then instructions), plus optional `references/` and `scripts/`.

## Usage

Skills load based on where a copy or symlink is placed, not where they live in this repo:

- One project only: link the skill into `<project>/.claude/skills/`
- Everywhere: link the skill into `~/.claude/skills/`

Example:

```sh
ln -s ~/Desktop/Home/Projects/Elliot-Skills/engineering/<skill-name> <project>/.claude/skills/<skill-name>
```

Symlinks keep a single editable copy here while each project loads only what it needs.

## MCP bundle

General research/dev MCP servers (arxiv, gyoshu, gbrain, obsidian) live in `mcp/general.mcp.json`.
Run `./install-mcp.sh /path/to/project` to scope them into one project instead of loading them everywhere.
This repo is **public** — `mcp/.env.example` shows the only secret (obsidian); never commit real `.env`.
