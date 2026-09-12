#!/bin/bash

# After login, open a fullscreen Matrix wake-up (red / blue pill).
setsid uwsm-app -- ghostty \
  --class=org.omarchy.matrix-welcome \
  --title=Matrix \
  --config-file="$HOME/.config/omarchy/matrix/ghostty.conf" \
  --background=#000000 \
  --foreground=#00ff41 \
  --window-padding-x=0 \
  --window-padding-y=0 \
  --font-size=15 \
  --confirm-close-surface=false \
  -e "$HOME/.config/omarchy/matrix-welcome.sh" \
  >/dev/null 2>&1 &
