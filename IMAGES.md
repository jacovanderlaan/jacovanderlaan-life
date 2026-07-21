# Images — where to drop them

All images live in **`assets/`**. Each page's hero shows a dashed placeholder
until the correctly-named file exists; the moment you drop the file in, the
photo appears. No HTML edit needed.

## Hero images (one per page)

| Page | Drop this file in `assets/` |
|---|---|
| Home | `home-hero.jpg` |
| Stage | `stage-hero.jpg` |
| Film | `film-hero.jpg` |
| Music | `music-hero.jpg` |
| Practice | `practice-hero.jpg` |
| Things | `things-hero.jpg` |
| Reading | `reading-hero.jpg` |
| Rotterdam | `rotterdam-hero.jpg` |

## Rules

- **Your own photos only** — nothing copyrighted.
- **Lowercase, hyphens, no spaces** in filenames (spaces break URLs).
- **`.jpg`** for photos, `.png` only if you need transparency.
- **~1600px wide** is plenty for a hero; bigger just loads slower.
- Extra images inside a page later: `<page>-01.jpg`, `<page>-02.jpg`, etc.
  Tell Claude where each should go and it gets wired in.

## How the drop-in works

Each hero holds `<img src="…-hero.jpg" onerror="this.classList.add('missing')">`
over a dashed hint. If the file is missing the image hides itself and the hint
shows; once the file exists the photo covers the hint. That's why you only ever
touch `assets/`, never the HTML.
