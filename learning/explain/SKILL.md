---
name: explain
description: Decode the last thing said into plain language with Warp-optimized formatting. Use ONLY when explicitly invoked as /explain. Never load proactively. Not a tutor; see comprend for durable learning.
---

# Explain: the decoder

Elliot calls this when the last thing said lost him: a tradeoff, a new topic, a research idea. The job is instant re-parsing, not durable learning. Nothing is written anywhere, ever. If `~/.claude/comprend/knowledge.md` exists, read it (READ-ONLY) and prefer vocabulary he has already proven; never write to comprend's files from here.

Target: the previous assistant message, or the specific term/phrase passed as the argument.

## Default mode: in-chat, instant

Output contract, in order, no exceptions:

1. **One-sentence plain answer.** First line, bolded lead-in "In one sentence:". No jargon.
2. **The words.** A 2-column table decoding every load-bearing term from the confusing passage. Terms only he might not know; skip incidentals. Max 2 columns, terse cells.
3. **Visuals are the centerpiece, not decoration.** Elliot: the labeled bar graphs are "singlehandedly the most helpful part" (2026-08-06). Rules:
   - ALWAYS include a visual when any quantitative comparison exists; number-labeled unicode bars in a fence are the default and the favorite (`0-5k  ████████████ 0.98   <- annotation`).
   - Every bar row carries its number; put a `<- annotation` on the rows that matter.
   - Multi-finding explains may use one small visual PER finding (cap ~5, each ≤10 lines) with a one-line caption; cut prose before cutting bars.
   - Other shapes when bars don't fit: tradeoff/choice -> comparison table; process/flow -> arrow diagram (`──▶`, `┌─┐`); structure/containment -> tree (`├──`); trend -> sparkline WITH its number row above (`▁▃▅▇` alone is unreadable).
4. **Spacing laws:** no paragraph over 2 sentences. Blank line between every block. Under ~120 words of prose total. Never one dense paragraph.
5. **Last line:** `*Fuzzy word left? Name it. Want it to stick? /comprend.*`

Warp rendering facts (verified 2026-08-06): markdown tables, fences, bold, and all Unicode render; ANSI colors, inline images, and mermaid do NOT survive the Claude Code transcript. Do not attempt them in chat.

## Rich mode: /explain rich

A designed card, rendered by headless Chromium, pushed as pixels into his Warp display pane. Use when he asks for `rich`, or offer it (do not force) when the idea is genuinely graphical.

1. Read `DESIGN.md` and `card-template.html` (this directory). The template contains a data-driven chart engine; you supply content and data, NEVER CSS or SVG coordinates. Fill tokens:
   - `{{ACCENT}}`: #7aa2f7 concept | #fbbf24 tradeoff | #4ade80 process
   - `{{TOPIC}}` chip text; `{{HERO_HTML}}` the one-sentence answer, with `<em>` around the key phrase
   - `{{ROWS_HTML}}`: `<div class="row"><dt>word</dt><dd>plain meaning</dd></div>` per term (3-5 rows)
   - `{{VISUAL_LABEL}}` + `{{VISUAL_JSON}}`: one of the five components (flow, bars, compare, tree, spark), schemas and selection rules in DESIGN.md
2. Write the filled card to `/tmp/explain-card.html` (must be /tmp: browse sandbox).
3. Run: `zsh ~/.claude/skills/explain/render-card.sh /tmp/explain-card.html <kebab-topic>`
4. **Read the PNG and evaluate readability before reporting** (standing styling rule). Fix and re-render if anything is cramped or illegible.
5. Delivery is verified by the script itself: it pushes to the display pane only if the watcher process is actually alive, otherwise it opens the PNG directly. Trust its `SHOWN:` line and report that channel. NEVER claim he can see a card without a `SHOWN:` confirmation. Images in this chat's tool results are visible to you, not to him.

Also give the in-chat one-sentence answer alongside the card; the card supplements, never replaces the text.
