# adplaybook.app

The website for [AdPlaybook](https://adplaybook.app) — a Mac app that turns a
product page into a complete, buildable ad campaign and then attacks its own
work before showing you anything.

## Build

```sh
python _build/render.py --app-repo "../ad maker app"
python _build/check.py
```

`render.py` generates the eight `/specs/` pages **directly from the product's
own `backend/adkit/platforms/*.json`** — the same files the application reads
when it builds a campaign. The site therefore cannot drift from the product,
and when a platform changes a limit and the spec is re-verified, the page
changes with it. A marketing site maintained separately from the thing it
describes goes stale in a month and nobody notices.

`check.py` must pass before publishing. It gates the two ways programmatic SEO
fails: a corpus that reads as machine-made even when each page reads fine
alone, and assertions about named third parties that nobody verified.

## The SEO thesis

The pages currently ranking for ad-spec queries are frequently wrong, and none
of them show their working. Two examples, both checked against the platforms'
own documentation on 2026-08-10:

- A widely-ranked page states LinkedIn's introductory text maxes at 600
  characters. LinkedIn's own help centre says **3,000**, with 150 to avoid
  truncation.
- Several pages state TikTok caps ad captions at 100 characters. TikTok's own
  in-feed specification page states **no character count at all**.

So every figure here carries the platform's own words, the URL it came from,
and the date it was read — plus an explicit list of what could not be verified.
That is also exactly what an AI answer engine needs in order to cite a source,
which is why `robots.txt` welcomes them by name and `llms.txt` states the two
corrections above directly.

## Deployment

Static. `CNAME` points at `adplaybook.app`; `.nojekyll` stops GitHub Pages
processing the `_build` directory.
