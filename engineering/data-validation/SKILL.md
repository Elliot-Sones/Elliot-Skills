---
name: data-validation
description: Use when ingesting external data, syncing records between two systems, or joining tables from different sources. Also after any migration or backfill, before declaring parity.
---

# Data Validation

## Overview

Reconcile with invariants, not by eyeballing samples. Parity is a set of matching numbers, written down.

## Workflow

1. Row counts: source vs destination. Exact numbers. Explain every difference.
2. Key sets: list keys only in source, and only in destination. Each list is empty or explained.
3. Checksums on critical columns: sum, min, max, count per group. Money matches to the cent, or you list the offending rows.
4. Null audit: null counts per column, before vs after. New nulls need a reason.
5. Spot-check 5 records end to end in the source-of-truth UI. This catches semantic drift the aggregates hide.
6. Write the reconciliation artifact before touching more data: counts, checksums, known diffs, date.

## Common mistakes

- Sampling instead of full key-set diffs. The missing 40 rows are never in your sample.
- Validating aggregates only, or rows only. Do both: totals match AND individual records match.
- Declaring parity verbally. No artifact means the check never happened.
- Checking the happy columns and skipping the ones that were hard to migrate.
