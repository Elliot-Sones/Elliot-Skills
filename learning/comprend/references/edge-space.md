# Edge space: what it is, what was tested, what shipped

The concept map is 213 nodes and 348 prerequisite edges. The edge space asks: if
we embed each concept as a vector, does the *relationship* between two concepts
(the difference vector of an edge) carry usable signal? Experiments in 2026-08
(local `nomic-embed-text` via ollama) answered yes, with sharp limits. This doc
is the durable record so future changes don't re-litigate settled findings.

## What was tested

| test | result | verdict |
|---|---|---|
| edge difference vectors cluster by relationship kind | star pairs rank #1 of ~340 (e.g. MLP->backprop ~ RNN->BPTT, 0.48) | REAL, retrieval-grade |
| "everything is ML" explains the matches | false: random same-domain edge pairs average ~0.00 cosine; subtraction cancels the shared component | objection disproven |
| widening arrows with step *descriptions* | type-prediction 75% (subtraction) vs 83% (subtraction + description), 24-edge pilot | promising, not yet shipped |
| analogy *arithmetic* A:B::C:? by vec math | 17% top-1, barely above the "answer near C" control | KILLED as a generator |
| confusable detection (nearest node pairs) | clean: gradient/gradient-descent, top-k/top-p, perceptron/MLP, etc. | SHIPPED |
| bridges (close-in-name, far-on-map) | mostly false friends (sequences-and-limits ~ context-length-limits) | inverted to a WARNING feature |
| custom-trained embedding (TransE on the map) | link-prediction median rank 109 vs pretrained 55 (worse than random) | KILLED: map too small to learn geometry |

Core lesson: **annotate the pretrained space, never retrain it.** 348 edges is
thousands short of what a graph-embedding needs. The pretrained model wins because
it imports world knowledge the map can't supply.

## What shipped (six features, in SKILL.md "## Edge space")

1. analogy anchors: open a new step from a known parallel step (rank-1 retrieval)
2. analogy-completion quiz: A:B::C:? with map-verified answers only
3. confusable contrast: 2-row side-by-side for name-twins (cosine >= 0.80)
4. false-friend warning: one-line disarm for name-similar/map-far pairs
5. edge-type ability: profile learns per-kind effort (additive to profile.md)
6. ACT-R rechecks: `uses`/`last` on ledger lines, due at 7*uses^2 days

## Thresholds (in build-space.py, tunable)

- `CONFUSE_MIN = 0.80` name-twin cosine floor
- `FF_SIM_MIN = 0.66`, `FF_DIST_MIN = 5` false-friend: this similar in name-space, this far on the map
- `PARALLELS_PER_EDGE = 6` analogy candidates stored per edge (runtime filters to known)

## Kill metrics

Each feature carries a removal condition (see SKILL.md). Check once ~20 relevant
episodes exist. The governor: no new edge-space feature wires in until an existing
one has data supporting it. Evidence gates complexity; nothing survives on
plausibility.

## Rebuild

`python3 ~/.claude/skills/comprend/build-space.py` (needs `ollama serve`), then
stamp `built`. Rebuild only when prereqs.md grows. Output is `~/.claude/comprend/
space.json`, derived and gitignored from the data dir; absence degrades the skill
to plain comprend.
