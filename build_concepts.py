#!/usr/bin/env python3
"""Build the Life concept pages -> concepts/*.html.

Third brand spoke (ADR-093). The concept SOURCE is shared with Structure Beats
Magic: W:/systems/concepts/. Each concept carries a `sites:` frontmatter list;
this builder publishes only concepts whose list contains "life". A concept in
both (sites: [sbm, life]) renders on both sites from the one source -- no
duplication, no drift.

Deliberately lighter than the SBM concept builder: no cross-cutting groups, no
graph/map. A life concept is a short living principle, not a node in a thesis
web. Same folder-per-concept format and hero-image support, the life site's own
warm chrome (terracotta accent, not SBM blue).

Usage:
    python build_concepts.py
    JVDL_LIFE_CONCEPTS="W:/systems/concepts" python build_concepts.py
"""
from __future__ import annotations

import html
import os
import re
import shutil
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

HERE = Path(__file__).parent
SRC = Path(os.environ.get("JVDL_LIFE_CONCEPTS", "W:/systems/concepts"))
OUT = HERE / "concepts"
BASE_URL = os.environ.get("JVDL_LIFE_BASE", "https://life.jacovanderlaan.com").rstrip("/")

# Category order for the index. Any category found but not listed is appended,
# so a new category can't silently drop a concept.
CATEGORY_ORDER = ["Living principles", "Life design"]

# Testphase: the whole life site is noindex until go-live. Match the other
# sections (they carry the TESTPHASE-NOINDEX meta); flip with JVDL_LIFE_INDEX=1.
NOINDEX = os.environ.get("JVDL_LIFE_INDEX", "") != "1"

PRIVATE_SECTIONS = {"notes", "actions", "comments", "briefs"}
_known_slugs: set = set()


def split_frontmatter(text: str):
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            meta = {}
            if yaml:
                try:
                    meta = yaml.safe_load(text[3:end].strip()) or {}
                except Exception as exc:
                    print(f"  ! FRONTMATTER PARSE ERROR: {exc}")
            return meta, text[end + 4:].lstrip("\n")
    return {}, text


def esc(s: str) -> str:
    return html.escape(str(s), quote=False)


def inline(s: str) -> str:
    """[[wikilinks]] -> links (only to concepts that exist on THIS site), plus
    **bold**, *italic*, [text](url), `code`. A wikilink to a concept not on the
    life site renders as plain text, so it can't 404."""
    spans: list[str] = []

    def _stash(m):
        spans.append(html.escape(m.group(1), quote=False))
        return f"\x00{len(spans) - 1}\x00"

    links: list[str] = []

    def _wiki(m):
        target = m.group(1).strip().rstrip("\\").strip()
        label = (m.group(2) or "").strip()
        bare = target[len("concept-"):] if target.startswith("concept-") else target
        if not label:
            label = bare.replace("-", " ")
            label = label[:1].upper() + label[1:]
        if bare not in _known_slugs:
            return html.escape(label, quote=False)   # not on this site -> plain text
        links.append(f'<a href="{html.escape(bare, quote=True)}.html">{html.escape(label, quote=False)}</a>')
        return f"\x01{len(links) - 1}\x01"

    s = re.sub(r"\[\[([^\]|]+?)(?:\\?\|([^\]]+))?\]\]", _wiki, s)
    s = re.sub(r"`([^`]+)`", _stash, s)
    s = html.escape(s, quote=False)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", s)
    s = re.sub(r"\x00(\d+)\x00", lambda m: f"<code>{spans[int(m.group(1))]}</code>", s)
    s = re.sub(r"\x01(\d+)\x01", lambda m: links[int(m.group(1))], s)
    return s


class Concept:
    def __init__(self, slug, name, tag, category, body_md, related, hero_image, hero_caption):
        self.slug, self.name, self.tag, self.category = slug, name, tag, category
        self.body_md, self.related = body_md, related
        self.hero_image, self.hero_caption = hero_image, hero_caption


def parse() -> list:
    concepts = []
    for folder in sorted(SRC.iterdir()):
        if not folder.is_dir():
            continue
        note = folder / f"{folder.name}.md"
        if not note.is_file():
            continue
        meta, body = split_frontmatter(note.read_text(encoding="utf-8"))
        sites = [str(x).strip().lower() for x in (meta.get("sites") or ["sbm"])]
        if "life" not in sites:
            continue
        md = meta.get("metadata", {}) if isinstance(meta.get("metadata"), dict) else {}
        slug = folder.name
        m = re.search(r"(?m)^#\s+(.+)$", body)
        name = m.group(1).strip() if m else slug.replace("-", " ").title()
        tag = str(meta.get("description", "")).strip().strip('"')
        cat = str(md.get("category", "")).strip() or "Living principles"
        related = [str(x).strip() for x in (md.get("related_concepts") or [])]
        # body minus the "Related concepts" / "Where it lives" / back-link tail
        body_clean = re.split(r"\n##+\s*Related concepts", body)[0]
        body_clean = re.sub(r"(?m)^\*\*Category:\*\*.*$", "", body_clean)
        body_clean = re.sub(r"(?m)^>\s.*$", "", body_clean)      # drop the blockquote tagline
        body_clean = re.sub(r"(?m)^#\s+.*$", "", body_clean, count=1)  # drop H1 (in chrome)
        concepts.append(Concept(
            slug, name, tag, cat, body_clean.strip(), related,
            str(meta.get("hero_image", "")).strip().strip('"'),
            str(meta.get("hero_caption", "")).strip().strip('"'),
        ))
    _known_slugs.clear()
    _known_slugs.update(c.slug for c in concepts)
    return concepts


HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
{noindex}<title>{title} — Life · Jaco van der Laan</title>
<meta name="description" content="{desc}" />
<meta property="og:title" content="{title}" />
<meta property="og:description" content="{desc}" />
<meta property="og:type" content="article" />
<meta property="og:url" content="{canonical}" />
<meta property="og:image" content="{ogimg}" />
<meta name="author" content="Jaco van der Laan" />
<meta name="twitter:card" content="summary_large_image" />
<link rel="canonical" href="{canonical}" />
<link rel="icon" type="image/svg+xml" href="{up}assets/favicon.svg" />
<link rel="stylesheet" href="{up}assets/site.css" />
<style>
  .c-hero {{ margin:0 0 2rem; }}
  .c-hero img {{ width:100%; height:auto; display:block; border-radius:12px;
    border:1px solid var(--line,#e7e5e4); box-shadow:0 10px 30px rgba(28,25,23,.08); }}
  .c-hero figcaption {{ font-size:.85rem; color:var(--ink-faint,#a8a29e); margin-top:.7rem;
    text-align:center; line-height:1.5; }}
  .c-cat {{ font-size:13px; font-weight:600; color:var(--accent,#b4541e);
    text-transform:uppercase; letter-spacing:1px; margin-bottom:10px; }}
  .c-body {{ font-size:17px; line-height:1.75; color:var(--ink-soft,#57534e); max-width:720px; }}
  .c-related {{ margin-top:2.2rem; font-size:.95rem; }}
  .c-related a {{ color:var(--accent,#b4541e); }}
  .c-back {{ display:inline-block; margin-top:2.4rem; font-weight:600; color:var(--accent,#b4541e); text-decoration:none; }}
  .concept-grid {{ display:grid; gap:1rem; grid-template-columns:repeat(auto-fill,minmax(260px,1fr)); margin:1rem 0 2.5rem; }}
  .concept {{ display:block; border:1px solid var(--line,#e7e5e4); border-radius:12px; padding:1.1rem 1.3rem;
    text-decoration:none; color:inherit; background:#fff; }}
  .concept:hover {{ border-color:var(--accent,#b4541e); }}
  .c-name {{ font-weight:700; margin-bottom:.3rem; }}
  .c-tag {{ font-size:.9rem; color:var(--ink-soft,#57534e); line-height:1.5; }}
  .cat-title {{ margin:2rem 0 .3rem; }}
</style>
</head>
<body>

<header class="site">
  <div class="wrap">
    <div class="brand"><a href="{up}" style="color:inherit">Jaco van der Laan · <span>Life</span></a></div>
    <nav class="site">
      <a href="{up}stage/">Stage</a>
      <a href="{up}film/">Film</a>
      <a href="{up}music/">Music</a>
      <a href="{up}things/">Things</a>
      <a href="{up}practice/">Practice</a>
      <a href="{up}reading/">Reading</a>
      <a href="{up}rotterdam/">Rotterdam</a>
      <a href="{up}concepts/"{concepts_active}>Principles</a>
      <a href="https://structurebeatsmagic.com" class="nav-sys">Systems</a>
    </nav>
  </div>
</header>
"""

FOOT = """
<footer class="site">
  <div class="wrap">
    <div>© Jaco van der Laan · <a href="{up}">Life</a></div>
    <div class="fam">
      <a href="https://jacovanderlaan.com">Work</a>
      <a href="https://structurebeatsmagic.com">Systems</a>
      <a href="https://structuredwandering.com">Travel</a>
    </div>
  </div>
</footer>
</body>
</html>
"""

NOINDEX_META = '<meta name="robots" content="noindex, nofollow" /><!-- TESTPHASE-NOINDEX: remove at go-live -->\n'


def render_index(concepts) -> str:
    by_cat: dict = {}
    for c in concepts:
        by_cat.setdefault(c.category, []).append(c)
    blocks = []
    order = CATEGORY_ORDER + [c for c in by_cat if c not in CATEGORY_ORDER]
    for cat in order:
        items = by_cat.get(cat)
        if not items:
            continue
        cards = "\n".join(
            f'      <a class="concept" href="{esc(c.slug)}.html">'
            f'<div class="c-name">{esc(c.name)}</div>'
            f'<div class="c-tag">{esc(c.tag)}</div></a>' for c in items)
        blocks.append(f'    <h2 class="cat-title">{esc(cat)}</h2>\n'
                      f'    <div class="concept-grid">\n{cards}\n    </div>')
    head = HEAD.format(
        noindex=NOINDEX_META if NOINDEX else "", up="../", concepts_active=' class="active"',
        title="Principles", desc="Living principles and mantras — the few rules I actually try to live by.",
        canonical=f"{BASE_URL}/concepts/", ogimg=f"{BASE_URL}/assets/life-og-card.svg")
    lede = ('<p class="c-body" style="margin-bottom:2rem">The few rules I actually try to live by — '
            'living principles and mantras, kept short on purpose. Some overlap with the '
            '<a href="https://structurebeatsmagic.com/concepts/">Systems</a> library; the difference is that '
            'these are about how to live, not how to build.</p>')
    body = ('<section class="hero"><div class="wrap" style="max-width:820px">\n'
            '    <p class="c-cat">Life</p>\n    <h1>Principles</h1>\n    ' + lede + "\n"
            + "\n".join(blocks) + "\n  </div></section>")
    return head + body + FOOT.format(up="")


def render_detail(c) -> str:
    head = HEAD.format(
        noindex=NOINDEX_META if NOINDEX else "", up="../", concepts_active="",
        title=esc(c.name), desc=html.escape(c.tag, quote=True),
        canonical=f"{BASE_URL}/concepts/{c.slug}.html",
        ogimg=(f"{BASE_URL}/assets/{c.hero_image}" if c.hero_image else f"{BASE_URL}/assets/life-og-card.svg"))
    hero = ""
    if c.hero_image and (SRC / c.slug / "assets" / c.hero_image).is_file():
        cap = f"<figcaption>{esc(c.hero_caption)}</figcaption>" if c.hero_caption else ""
        hero = (f'<figure class="c-hero"><img src="../assets/{esc(c.hero_image)}" '
                f'alt="{esc(c.name)}" loading="eager"/>{cap}</figure>')
    paras = "\n".join(f"<p>{inline(p.strip())}</p>"
                      for p in re.split(r"\n\s*\n", c.body_md) if p.strip())
    rel = ""
    live_related = [r[len("concept-"):] if r.startswith("concept-") else r for r in c.related]
    live_related = [r for r in live_related if r in _known_slugs]
    if live_related:
        links = " · ".join(f'<a href="{esc(r)}.html">{esc(r.replace("-", " ").title())}</a>'
                           for r in live_related)
        rel = f'<div class="c-related"><strong>Related:</strong> {links}</div>'
    body = (f'<section class="hero"><div class="wrap" style="max-width:820px">\n'
            f'    <p class="c-cat">{esc(c.category)}</p>\n    <h1>{esc(c.name)}</h1>\n'
            f'    <p class="c-body" style="font-weight:600;color:var(--ink,#1c1917)">{esc(c.tag)}</p>\n'
            f'  </div></section>\n'
            f'  <section class="tight"><div class="wrap" style="max-width:820px">\n'
            f'    {hero}<div class="c-body">{paras}</div>\n    {rel}\n'
            f'    <a class="c-back" href="../concepts/">← All principles</a>\n'
            f'  </div></section>')
    return head + body + FOOT.format(up="../")


def copy_assets(concepts) -> int:
    site_assets = HERE / "assets"
    site_assets.mkdir(parents=True, exist_ok=True)
    n = 0
    for c in concepts:
        if not c.hero_image:
            continue
        src = SRC / c.slug / "assets" / c.hero_image
        if src.is_file():
            shutil.copy2(src, site_assets / c.hero_image)
            n += 1
        else:
            print(f"  ! hero missing on disk: {c.slug} -> {c.hero_image}")
    return n


def main():
    concepts = parse()
    if not concepts:
        raise SystemExit("no life concepts found (sites: [life]) in " + str(SRC))
    OUT.mkdir(parents=True, exist_ok=True)
    n = copy_assets(concepts)
    if n:
        print(f"  copied {n} hero image(s) -> assets/")
    (OUT / "index.html").write_text(render_index(concepts), encoding="utf-8")
    for c in concepts:
        (OUT / f"{c.slug}.html").write_text(render_detail(c), encoding="utf-8")
    # orphan cleanup: a <slug>.html with no live life-concept behind it
    keep = {f"{c.slug}.html" for c in concepts} | {"index.html"}
    for f in OUT.glob("*.html"):
        if f.name not in keep:
            f.unlink()
            print(f"  - removed orphan page: {f.name}")
    print(f"  concepts/index.html + {len(concepts)} detail pages -> {OUT}")


if __name__ == "__main__":
    main()
