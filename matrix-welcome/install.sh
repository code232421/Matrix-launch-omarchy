#!/bin/bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
OMARCHY="$HOME/.config/omarchy"
HYPR="$HOME/.config/hypr/hyprland.lua"

mkdir -p "$OMARCHY/matrix/wallpapers" \
  "$OMARCHY/hooks/post-boot.d" \
  "$OMARCHY/backgrounds/harbordark"

install -m 755 "$ROOT/welcome.py" "$OMARCHY/matrix/welcome.py"
install -m 644 "$ROOT/ghostty.conf" "$OMARCHY/matrix/ghostty.conf"
install -m 755 "$ROOT/matrix-welcome.sh" "$OMARCHY/matrix-welcome.sh"
install -m 755 "$ROOT/hooks/matrix-welcome.sh" "$OMARCHY/hooks/post-boot.d/matrix-welcome.sh"
install -m 644 "$ROOT/wallpapers/red-pill.png" "$OMARCHY/matrix/wallpapers/red-pill.png"
install -m 644 "$ROOT/wallpapers/blue-pill.png" "$OMARCHY/matrix/wallpapers/blue-pill.png"
install -m 644 "$ROOT/wallpapers/red-pill.png" "$OMARCHY/backgrounds/harbordark/10-matrix-red-pill.png"
install -m 644 "$ROOT/wallpapers/blue-pill.png" "$OMARCHY/backgrounds/harbordark/11-matrix-blue-pill.png"

MARKER="org.omarchy.matrix-welcome"
if [[ -f $HYPR ]] && ! grep -q "$MARKER" "$HYPR"; then
  printf '\n%s\n' "$(cat "$ROOT/hyprland.lua.snippet")" >> "$HYPR"
  hyprctl reload >/dev/null 2>&1 || true
fi

echo "Installé. Au prochain login, la scène Matrix se lance."

if [[ ${1:-} == --test ]]; then
  "$OMARCHY/hooks/post-boot.d/matrix-welcome.sh"
fi
