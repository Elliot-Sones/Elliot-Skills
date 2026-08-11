#!/bin/zsh
# Usage: zsh ~/.claude/skills/explain/render-card.sh <filled-card.html under /tmp> <kebab-name>
# Rasterizes the card at 2x and pushes it to the comprend display pane.
set -e
HTML="$1"; NAME="${2:-explain-card}"
B="$HOME/.claude/skills/gstack/browse/dist/browse"
case "$HTML" in /tmp/*|/private/tmp/*) ;; *) echo "FAILED: html must live under /tmp (browse sandbox)"; exit 1 ;; esac
"$B" viewport 920x900 --scale 2 >/dev/null
"$B" goto "file://$HTML" >/dev/null
python3 -c "import time; time.sleep(0.8)"
"$B" screenshot "/tmp/$NAME.png" --selector .card >/dev/null
mkdir -p "$HOME/.claude/comprend/display"
echo "RENDERED: /tmp/$NAME.png"
# Delivery must be verified, never assumed: if the display pane watcher is
# alive, push to it; otherwise open the PNG directly so something ALWAYS shows.
# Warp is the home channel. If the display pane isn't running, summon it:
# the warp:// URI launches a Warp tab that runs the watcher itself.
if ! pgrep -f "comprend/display.sh" >/dev/null 2>&1; then
  open "warp://launch/comprend-display.yaml" 2>/dev/null || open "warp://launch/comprend-display" 2>/dev/null
  for _i in {1..32}; do
    pgrep -f "comprend/display.sh" >/dev/null 2>&1 && break
    python3 -c "import time; time.sleep(0.25)"
  done
fi
if pgrep -f "comprend/display.sh" >/dev/null 2>&1; then
  cp "/tmp/$NAME.png" "$HOME/.claude/comprend/display/$NAME.png"
  echo "SHOWN: warp display pane"
else
  # Last resort only (NEVER Preview: it opens zero windows on this machine).
  cat > "/tmp/$NAME-view.html" <<VIEWEOF
<!DOCTYPE html><html><head><meta charset="utf-8"><title>$NAME</title>
<style>body{background:#0b0d10;margin:0;padding:40px;display:flex;justify-content:center}img{max-width:920px;width:100%;border-radius:12px}</style>
</head><body><img src="$NAME.png"></body></html>
VIEWEOF
  open "/tmp/$NAME-view.html"
  echo "SHOWN: browser tab (warp launch failed; investigate ~/.warp/launch_configurations/comprend-display.yaml)"
fi
