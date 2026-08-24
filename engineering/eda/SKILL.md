---
name: eda
description: Use when opening a new or unfamiliar dataset, before any modeling, dashboard, or join work. Also when numbers look wrong and the raw data itself is suspect.
---

# EDA First Pass

## Overview

Profile a dataset before you build on it. Every downstream bug is cheaper to catch here.

## Workflow

1. Load with explicit dtypes. Record rows, columns, memory.
2. Build a schema table: name, dtype, % missing, n unique, one example value.
3. Verify keys. Confirm expected uniqueness. Re-check row counts after every join.
4. Scan distributions. Flag impossible values: negatives that can't be, dates in the future, categories with 1 member.
5. If temporal: min/max date, gaps, timezone, volume per period.
6. Read missingness as a pattern, not a rate. Structural or random?
7. Leakage scan: would this column be known at prediction time?
8. Write findings to `EDA.md`: 5 to 15 bullets, each one fact with one number.

## Quick reference

| Check | One-liner |
|---|---|
| Size | `df.shape`, `df.memory_usage(deep=True).sum()` |
| Schema + missing | `df.dtypes`, `df.isna().mean().sort_values()` |
| Key uniqueness | `df["id"].is_unique` |
| Numeric sanity | `df.describe(percentiles=[.01, .99])` |
| Category junk | `df["col"].value_counts(dropna=False).head(20)` |

## Common mistakes

- Running `describe()` only. It hides categorical junk and duplicated keys.
- Trusting column names. Verify meaning against a few real rows.
- Skipping the writeup. Unrecorded findings get re-discovered next week.
