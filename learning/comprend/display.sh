#!/bin/zsh
# Comprend display pane. Run this once in a Warp split pane:
#   zsh ~/.claude/skills/comprend/display.sh
# Any PNG dropped into ~/.claude/comprend/display/ renders inline here
# within ~1s, using the iTerm2 inline-image protocol (Warp supports it
# at a live prompt; it's only Claude Code's transcript that strips it).
DIR="$HOME/.claude/comprend/display"
mkdir -p "$DIR/shown"
printf "\033[1mcomprend display pane\033[0m watching %s\n" "$DIR"
printf "drop a PNG there (or let /explain rich do it) and it appears here.\n\n"
while true; do
  for f in "$DIR"/*.png(N.om); do
    size=$(stat -f%z "$f")
    b64=$(base64 < "$f" | tr -d '\n')
    printf "\n\033[2m%s  %s\033[0m\n" "$(date +%H:%M:%S)" "$(basename "$f")"
    printf '\033]1337;File=inline=1;size=%d;width=90%%;preserveAspectRatio=1:%s\a\n' "$size" "$b64"
    mv "$f" "$DIR/shown/$(basename "$f")"
  done
  sleep 1
done
