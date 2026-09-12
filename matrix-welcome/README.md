# Matrix Welcome

Splash plein écran au login Omarchy : pluie de code, scène de Morpheus, **pilule rouge / pilule bleue**, puis changement de fond d’écran.

## Installer

```bash
git clone <url-du-repo> ~/Projects/matrix-welcome
cd ~/Projects/matrix-welcome
./install.sh
```

Puis redémarre la session (ou lance `./install.sh --test`).

## Contrôles

- Une touche pendant le texte / la pluie accélère
- Flèches, `R` / `B`, Entrée pour avaler une pilule
- **Rouge** → fond Matrix (le désert du réel)
- **Bleue** → fond ciel / ville (l’illusion)

## Fichiers

| Fichier | Rôle |
|---|---|
| `welcome.py` | Scène interactive |
| `matrix-welcome.sh` | Lanceur |
| `hooks/matrix-welcome.sh` | Hook `post-boot` Omarchy |
| `ghostty.conf` | Terminal noir, vert Matrix |
| `wallpapers/` | Fonds 4K rouge / bleu |
| `hyprland.lua.snippet` | Règles fenêtre plein écran |
