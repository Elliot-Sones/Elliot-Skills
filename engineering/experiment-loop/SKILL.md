---
name: experiment-loop
description: Use when training or evaluating models, engineering features, or comparing modeling approaches. Also when a score looks too good, or results change between identical runs.
---

# Experiment Loop

## Overview

One metric, one split, one change at a time, every run logged.

## Workflow

1. Fix the split before anything else. Temporal data: split by time. Grouped data (players, customers, sessions): split by group. Never random-split rows that share an entity.
2. Pick one primary metric. Write it down before the first run.
3. Establish a dumb baseline: majority class, mean, last value, or a one-line heuristic. This is the number to beat.
4. Change one thing per run.
5. Log every run in `RESULTS.md`: run id, what changed, metric, seed, commit hash. Failed runs stay in the log.
6. On a suspicious jump, test for leakage before celebrating: shuffle the target and re-run. The score must collapse to baseline.
7. Touch the test set once, at the end.

## Common mistakes

- Comparing runs made on different splits. Those numbers are not comparable.
- Tuning against the test set. That is training on it, slowly.
- Deleting failed runs. The log is the experiment's memory.
- No seed control, then debugging "random" regressions.
