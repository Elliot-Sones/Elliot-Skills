---
name: python-scaffold
description: Use when starting a new Python project, analysis, or script that will outlive one session. Also when a notebook is turning into a real project.
---

# Python Scaffold

## Overview

uv-based layout so every project installs, runs, and tests the same way.

## Commands

```bash
uv init myproj && cd myproj
uv add pandas matplotlib          # runtime deps as needed
uv add --dev pytest ruff
mkdir -p src/myproj tests data output
```

## Rules

- Code lives in `src/`, with one entry point: `uv run python -m myproj`.
- Notebooks are for exploration only. The deliverable is a script or module, never a notebook.
- `data/` holds raw inputs, treated read-only. `output/` is regenerable. Both gitignored.
- Seed once, in one place: `random`, `numpy`, and the framework. Log the seed with results.
- Lint and test from day one: `uv run ruff check . && uv run pytest -q`.
- Configuration in one settings module or `.env`. No constants scattered across files.

## Common mistakes

- Mixing pip/venv with uv. Pick uv, delete the stray venvs.
- Importing functions from a notebook. Move the code to `src/` and import it in the notebook instead.
- Writing outputs into `data/`, then losing track of what is raw.
