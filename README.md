# life.jacovanderlaan.com

The fourth property under the `jacovanderlaan` name-brand (**PDR-075**, 19 Jul 2026):
everything that is not work, not the system, and not travel — films, books,
psychology, mental models, GTD, contemporary dance, opera, communication, interiors.

## The rule that decides what goes here

The line between **Structure Beats Magic** and **Life** is *not thematic*. It runs
along **system vs. content**:

- A learning system or a publishing system is **SBM** — even when it runs on life material.
- The flashcards about opera are **life**; the system that brings them back is **SBM**.
- The film notes are **life**; the machinery that publishes them is **SBM**.

> **Life runs on SBM.** This site is the shop window; the engine is next door.

## Family

| Property | What |
|---|---|
| jacovanderlaan.com | Work — data modelling and architecture (WordPress) |
| structurebeatsmagic.com | The systems (GitHub Pages) |
| structuredwandering.com | Travel (GitHub Pages) |
| **life.jacovanderlaan.com** | **Everything else (this repo, GitHub Pages)** |

## Design

Same family palette as the sister sites — shared neutrals, navy and the gold
payoff colour. The accent is a warm terracotta (`#b4541e`): this is the human,
off-duty property, so it reads warmer than SBM's blue (systems) and SW's teal
(sea/horizon) while staying visibly in the family.

## Status

**Skeleton, deliberately.** PDR-075 is explicit that the life site earns work when
there is content for it, not before. This scaffold exists so material has somewhere
to land. Sections are marked `soon` until they hold something real.

## Deploy

Static, no build step yet. GitHub Pages from `main`, custom domain via `CNAME`
(`life.jacovanderlaan.com`) — needs a DNS `CNAME` record pointing to
`jacovanderlaan.github.io`. Once content arrives, expect a `build_*.py` generator
in the sibling style (`build_articles.py` on the other two sites) that renders from
the vault rather than hand-written HTML.
