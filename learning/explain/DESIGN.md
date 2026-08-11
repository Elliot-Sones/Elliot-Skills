# Explain card design system

The template carries all styling; the model only supplies content and data. Never write CSS or SVG coordinates at runtime. If a visual doesn't fit the five components below, use the closest one or simplify the idea; do not freehand.

## Tokens (frozen in card-template.html)

| token | value | use |
|---|---|---|
| bg | #0b0d10 | card and page |
| surface | #10131a / #0b0e14 | panel / boxes inside it |
| text | #F8FAFC | primary |
| body | #c8cdd6 | secondary prose |
| muted | #8b93a1 / #6b7280 | labels, captions |
| hairline | rgba(255,255,255,.06-.09) | all borders |
| accent | via {{ACCENT}} | ONE per card |

Accent semantics: `#7aa2f7` concept · `#fbbf24` tradeoff/warning · `#4ade80` process/success. Extra ink colors exist only inside flow parts: `fk-amber`, `fk-red`, `fk-green`, `fk-dim`, `fk-accent`.

Type: serif hero 30px (one `<em>` max), mono for all labels/data (11-15px), sans body 15px. Spacing rhythm 8px. Radii: 9-12px. No shadows, no extra gradients beyond the top glow bar.

## Composition rules

- 3-5 word rows; dt max ~14 chars (it truncates ugly, shorten the term instead).
- Hero max ~12 words; the `<em>` phrase is the one thing to remember.
- One visual per card. `{{VISUAL_LABEL}}` names it plainly: "how it flows", "the tradeoff", "the trend".
- Chip text lowercase, 1-3 words.

## Visual components ({{VISUAL_JSON}})

Pick by the idea's shape, same taxonomy as in-chat mode:

**flow** (process, cause-and-effect) — 2-4 steps, optional arrow captions; `parts` colorize spans:
```json
{"type":"flow","steps":[
  {"sub":"your program prints","parts":[{"t":"\\033[31m","k":"amber"},{"t":" hi"}]},
  {"sub":"you see","parts":[{"t":"hi","k":"red"},{"t":"  (red, no command visible)","k":"dim"}]}],
 "arrows":["travels as ordinary bytes"]}
```

**bars** (magnitude comparison) — 2-6 items; `dim:true` for baseline/context rows; `display` overrides the printed value:
```json
{"type":"bars","items":[
  {"label":"0 gaps","value":2},{"label":"3-5 gaps","value":8},
  {"label":"6+ gaps","value":12,"dim":true}],"note":"median messages to learn"}
```

**compare** (tradeoff, A vs B) — 2-5 rows; `win` marks the better cell per row (omit when neither wins):
```json
{"type":"compare","a":"flat files","b":"sqlite","rows":[
  {"label":"queries","va":"model reads it","vb":"SQL needed","win":"a"},
  {"label":"10k+ rows","va":"slows down","vb":"stays fast","win":"b"}]}
```

**tree** (structure, containment) — supply box-drawing text verbatim:
```json
{"type":"tree","text":"self-attention\n├── queries-keys-values\n│   └── linear-layer\n└── softmax"}
```

**spark** (trend) — 5-12 values; number row renders automatically above the line:
```json
{"type":"spark","values":[9,7,8,6,5,4,3],"note":"messages per concept, falling = learning faster"}
```
