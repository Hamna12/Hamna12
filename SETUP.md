# How this profile is built

Everything here is self-generated SVG. No third-party widgets. All of it animates
inline in the GitHub README because GitHub runs SMIL/CSS animations inside `<img>`
tags (it strips JavaScript, so nothing here relies on JS).

## Files

| File | What it is | Animated by |
| --- | --- | --- |
| `hero.svg` | Dev-console (types line by line, starfield + orbiting-planet accent) | SMIL |
| `wordmark.svg` | HAMNA extruded to 3D ASCII, wipes in then rocks | SMIL flipbook |
| `contrib-heatmap.svg` | Contribution calendar in a pink/magenta ramp, cascade reveal + real stats | CSS keyframes |

## One-time setup

1. Create a repo named exactly `Hamna12` (same as your username). GitHub shows its
   README on your profile.
2. Drop these files in at the repo root: `README.md`, `hero.svg`, `wordmark.svg`,
   `contrib-heatmap.svg`, the `scripts/` folder, the `data/` folder, and
   `.github/workflows/update-profile-art.yml`.
3. Push to `main`. The Action runs on push and then daily, so the heatmap stays
   current. No secrets or tokens needed (it scrapes your public calendar).

## Regenerating the static art

Only needed if you change text, colors, or layout.

```bash
pip install -r scripts/requirements.txt

# hero (edit the `lines` list inside the script to change the boot text)
python scripts/make_hero_svg.py hero.svg

# wordmark (change the word or spacing)
WORDMARK_TEXT=HAMNA python scripts/make_wordmark_svg.py wordmark.svg

# heatmap (usually the Action does this for you)
python scripts/fetch_contributions.py Hamna12
python scripts/render_heatmap_svg.py
```

## Palette (so everything stays consistent)

- Background: `#0b0e1a` / `#141024`
- Pink accent: `#ff5fa2` and `#ff8fc7`
- Cyan: `#22d3ee`
- Gold: `#f2cc60`
- Ink (text): `#e9d8ee`

Change these in the three scripts and the whole profile re-themes together.
