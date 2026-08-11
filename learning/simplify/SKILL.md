---
name: simplify
description: Render the current problem, situation, or decision as a fixed five-row brief so Elliot orients in seconds. Use ONLY when explicitly invoked as /simplify. Never load proactively. Sibling of /explain, which decodes passages and terms.
---

# Simplify: the problem brief

Take the problem currently on the table (the situation under discussion, the pending decision, the task just introduced, or whatever he names as the argument) and re-render it as THE BRIEF. The value is invariance: same five rows, same order, every time, so his brain parses content, never structure.

## The brief

```
goal       what winning looks like ── one line, always first
now        where things stand
gap        what's between now and goal = the actual problem
pieces     the 2-4 moving parts · any term not in his ledger glossed right there
your move  the decision (options + recommendation) or the action ── always last
```

Optional sixth row `smells like`: one past problem this genuinely rhymes with. Only when the parallel is real; never forced.

## Rules

- One screen max. Each row 1-2 lines. No paragraphs anywhere in the brief.
- Read `~/.claude/comprend/knowledge.md` (READ-ONLY) when it has content; prefer his proven vocabulary; gloss everything else inline in `pieces`. Never write to comprend's files.
- Goal before mechanism, always. Never open with how something works.
- If the move is a decision: render 2-4 options as a compact table with one marked recommendation.
- Detail lives BELOW the brief after a `---` divider, and only if it earns its place. The brief must stand alone.
- No meta-narration ("here's a brief of..."); just render it.
- Nothing is logged or written anywhere. This skill is stateless.

## Relationship to siblings

- `/explain`: a passage or term confused him -> word decode + one visual.
- `/simplify`: a whole situation confused him -> the brief.
- `/comprend`: he wants a concept to durably stick -> full tutor with teach-back.

## Default behavior elsewhere

Even without the skill invoked, new problems, findings, or decisions introduced to Elliot should OPEN in this frame (standing feedback memory). /simplify is the explicit re-orient button for anything already on the table.
