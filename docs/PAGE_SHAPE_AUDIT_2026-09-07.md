# Every page against the truncation article

**Benchmark: `/learn/ad-copy-truncation-vs-hard-limits/`** — the site's highest-impression page
(297). Measurably it does two things: **3 of its 3 real headings are questions**, and it cites
**22 specific numbers** in 2,592 characters. Those are the two axes audited here, because they
are the two the Docket content-shape findings name and the only two that can be counted rather
than judged.

Measured 2026-09-07 across all 58 pages. `/`, `/contact/`, `/privacy/`, `/thank-you/` are
exempt — a contact page has no question to answer and a privacy page should not invent one.

| family | pages | median question-ratio | median numbers | verdict |
|---|---|---|---|---|
| `/vs/` | 1 | 0.00 | 11 | below on headings |
| `/strategies/` | 11 | 0.00 | 5 | **below on both** |
| `/for/` | 11 | 0.00 | 6 | **below on both** |
| `/offline/` | 1 | 0.00 | 20 | below on headings |
| `/specs/` | 10 | 0.37 | 26 | below on headings |
| `/learn/` | 15 | 1.00 | 11 | at benchmark |
| `/how-to/` | 4 | 1.00 | 8 | at benchmark |

## What the table says, including where it contradicted what I expected

`/learn/` (1.00) and `/how-to/` (1.00) are at the benchmark. Those are where five of the site's
six impression-earning pages live, so **order 4 — apply the content shape to the winners first —
is done for them.**

**`/specs/` is NOT done, at 0.37.** I wrote the opposite in a first draft of this file, from
memory of the commit that added question headings to that template (`5f29199`), and the table
I had just generated said otherwise. Ten pages, and fewer than four in ten of their headings
are questions — despite `/specs/` itself being an impression-earning page (46). It is the
highest-value gap on this list precisely because it already earns impressions.

## The metric was wrong for /specs/, and reading the headings is what showed it

Before acting on "fix `/specs/` headings" I read them. Most of its non-question headings are
**field labels in a reference table**, not prose:

    Feed: single image — Headline
    Timeline: promoted post with image — Body text
    For You feed: in-feed video (non-Spark) — Body text

Turning those into questions would vandalise a specification. The metric counted spec fields as
prose headings and produced a number that pointed at the wrong family. Excluding the 16 field
labels, `/specs/` is **0.50**, not 0.37 — borderline rather than a gap.

And its remaining statement-form headings are deliberate and good: *"A link costs you 23
characters"*, *"The description nobody reads"*, *"The comment thread is part of the ad"*. Those
are specific and quotable as they stand. **Recommendation for `/specs/` withdrawn.**

## The gap, in priority order (corrected)

Question-ratio over PROSE headings only:

| family | pages | question-ratio |
|---|---|---|
| `/strategies/` | 11 | 0.00 |
| `/for/` | 10 | 0.00 |
| `/specs/` | 10 | 0.50 |
| `/learn/` | 14 | 1.00 |
| `/how-to/` | 4 | 1.00 |

**1. `/strategies/` — 11 pages, 0.00, median 5 numbers.** Below on both axes, uniformly, and
sharing a template. Earns nothing today, so it is a bet rather than a repair.

**2. `/for/` — 10 pages, 0.00, median 6 numbers.** The thinnest pages on the site for specifics.
A page for plumbers naming no limit, no floor and no cost gives an AI engine nothing to quote.

Neither is a winner, so **order 4's "winners first" instruction is already satisfied** by
`/learn/` and `/how-to/` at 1.00. What remains is not a repair to earning pages; it is new work
on pages that earn nothing, and should be judged as such.

## What this audit does NOT claim

That question marks cause rankings. The two axes are copied from the site's best-performing
page and from Docket's audit; that is a reason to try them, not evidence they are why it wins.
The honest test is the same as everywhere else here: change one family, leave the rest, and
read the console in a fortnight. Nothing on this page should be cited as a result.
