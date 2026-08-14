#!/usr/bin/env python3
"""Build adplaybook.app from the product's own data.

The whole SEO thesis of this site is one observation: **the pages currently
ranking for ad-spec queries are wrong.** A page ranking today for LinkedIn's
limits states the introductory text maxes at 600 characters; LinkedIn's own
help centre says 3,000, with 150 to avoid truncation. Another states TikTok
caps ad captions at 100 characters; TikTok's own in-feed specification page
states no character count at all. Both were checked against the platforms'
documentation on 2026-08-10.

Undated, uncited and incorrect is what page one looks like. So this site's
pages carry, for every number: the platform's own words, the URL they came
from, and the date they were read — plus an explicit list of what could *not*
be verified, because a spec sheet with no gaps is either complete or lying and
the reader cannot tell which.

They are generated straight from `backend/adkit/platforms/*.json` — the same
files the app itself reads. That is deliberate: the site cannot drift from the
product, and when the daily spec-diff job updates a limit, the page changes
with it. A marketing site maintained separately from the thing it describes
goes stale in a month and nobody notices.

    python _build/render.py [--app-repo PATH]
"""

from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import sys
from datetime import date
from pathlib import Path
from typing import Any, Dict, List

SITE = Path(__file__).resolve().parents[1]
BASE_URL = "https://adplaybook.app"
BUILT = date.today().isoformat()

BRAND = "AdPlaybook"
TAGLINE = "The ad maker that knows which strategy fits — and proves every claim."


# ---------------------------------------------------------------------------
# Page shell
# ---------------------------------------------------------------------------

CSS = """
/* Design tokens match the sibling products on purpose — same black, same
   hairlines, same pill buttons — with this app's blue in place of Crisp's
   cyan. A family of tools that look unrelated reads as three hobby projects. */
:root{
  --black:#0f0d0b;--panel:#151210;--panel-2:#1b1714;--card:#211c18;
  --hair:#2a2320;--hair-lit:#3a312c;
  --white:#f5f7fa;--grey:#8a8f98;--grey-dim:#61656e;
  /* Four of the five sites in this portfolio were near-black with a blue
     accent and -apple-system, so they read as one company shipping four
     things. docketseo.app was the only escape and the strongest of the six;
     its recipe is three things together — ground colour, typeface, structure.
     AdPlaybook's is evidence: the product exists to refuse claims it cannot
     trace back to the advertiser's own page.

     The accent was that green until 2026-08-13, when four reference sites were
     measured at 1440px: Linear #08090A / 64px w510, Raycast #07080A / 64px
     w600, Cursor #14120B / 26px w400, Warp light / 72px w400. Three of the
     four carry no chromatic accent at all, and #4ade80 had become the most
     common accent in the category — so it was the default rather than a
     choice, and it says "pass", which is backwards for a product whose value
     is refusing. Amber is what a flag looks like. --green keeps the old value
     and is now used only for the PASS chips in the product mock, where it
     means something because it is not the brand colour.

     Display type moved off the mono at the same time: not one of the four
     sets display type in a monospace, and none ships a weight above 600.
     --blue is kept as an alias rather than renamed at 40+
call sites; it no longer holds a blue and the name is legacy. */
  --accent:#f0b429;--blue:var(--accent);--ice:#a8c8ff;--violet:#9d8cff;--green:#4ade80;--amber:#f0b429;
  /* Everything below used to be a literal somewhere in the stylesheet. They are
     tokens now because of a bug I shipped to kerrandcompanyholdings.com on
     2026-08-13: a light theme whose seven contrast ratios I had measured and
     confirmed, which still rendered wrong, because the nav background, a
     heading gradient and four glow rules were hard-coded and never read the
     palette. Measuring a token set is not the same as checking what reads it.
     A colour that only exists as a literal cannot follow a theme. */
  --nav-bg:rgba(15,13,11,.72);--nav-hair:rgba(42,35,32,.9);
  --on-accent:#1a1206;                      /* text ON the green button */
  --accent-lift:#ffc94d;--accent-deep:#c2891a;
  --accent-glow:rgba(240,180,41,.85);--accent-glow-2:rgba(240,180,41,1);
  --accent-wash:rgba(240,180,41,.16);--accent-wash-2:rgba(240,180,41,.13);
  --accent-edge:rgba(240,180,41,.5);--amber-edge:rgba(217,167,43,.5);
  --row-hover:rgba(255,255,255,.02);
  --window-shadow:rgba(0,0,0,.9);--window-edge:rgba(255,255,255,.02);
  --r:18px;--r-sm:12px;
  --sans:-apple-system,BlinkMacSystemFont,"SF Pro Display","Segoe UI",Inter,system-ui,sans-serif;
  --mono:ui-monospace,SFMono-Regular,"SF Mono",Menlo,monospace;
  --w:1080px;--wr:820px;
}
/* The light palette. This site is dark-first on purpose — the product window in
   the hero is a real interface, not a screenshot, and it was designed against a
   near-black ground. So dark stays the default and light is the deliberate
   alternative, rather than the other way round.

   The token NAMES are wrong in light mode and I am keeping them. --black holds a
   near-white and --white holds a near-black, which reads badly here and reads
   correctly at all forty-plus call sites. Renaming them would touch every rule
   in the file to fix a comment; this way the risk stays in one block that is
   easy to read in full.

   The accent could not simply carry over. #4ade80 is a bright green built for a
   near-black ground; on white it measures about 1.7:1 and is unreadable as text.
   Light mode uses #15803D, which is the same hue several stops down and clears
   4.5:1 on this ground. Buttons then need light text rather than dark, which is
   what --on-accent flipping is for. */
:root[data-theme="light"]{
  --black:#faf8f5;--panel:#ffffff;--panel-2:#f2ede6;--card:#ffffff;
  --hair:#e6ded3;--hair-lit:#cfc3b3;
  --white:#14100c;--grey:#5c554c;--grey-dim:#7a7268;
  --accent:#8a5a12;--ice:#1d4ed8;--violet:#6d28d9;--green:#15803d;--amber:#8a5a12;
  --nav-bg:rgba(250,248,245,.82);--nav-hair:rgba(207,195,179,.9);
  --on-accent:#ffffff;
  --accent-lift:#a86f1c;--accent-deep:#6b450d;
  --accent-glow:rgba(138,90,18,.34);--accent-glow-2:rgba(138,90,18,.42);
  --accent-wash:rgba(138,90,18,.10);--accent-wash-2:rgba(138,90,18,.08);
  --accent-edge:rgba(138,90,18,.45);--amber-edge:rgba(138,90,18,.45);
  --row-hover:rgba(20,16,12,.035);
  --window-shadow:rgba(20,16,12,.22);--window-edge:rgba(20,16,12,.06);
}

/* The toggle. Top corner on every site, per Matthew 2026-08-13 — but inside the
   sticky nav rather than position:fixed, and that distinction cost an evening.
   
   As `position:fixed;right:.85rem` it sat 132px off the right edge of a 375px
   screen: invisible and unreachable. `right` resolves against the initial
   containing block, which is as wide as the DOCUMENT when the document
   overflows — and the button's own overflow was what widened it. The button
   pushed the page wider, the wider page pushed the button further out, and the
   loop sustained itself at 521px on a 375px screen.
   
   Living in the nav removes the dependency entirely: the nav is sticky, so the
   control still sits in the top corner and still follows the reader, but it is
   laid out in normal flow and cannot position itself off the screen. */
#themeToggle{
  flex:none;margin-left:auto;
  width:2.1rem;height:2.1rem;border-radius:999px;
  border:1px solid var(--hair-lit);background:var(--panel);color:var(--grey);
  cursor:pointer;font-size:.9rem;line-height:1;
  display:flex;align-items:center;justify-content:center;
}
#themeToggle:hover{color:var(--white);border-color:var(--grey-dim)}
#themeToggle:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
@media (prefers-reduced-motion:no-preference){
  #themeToggle{transition:color .15s,border-color .15s}
}

*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%;scroll-behavior:smooth}
body{margin:0;background:var(--black);color:var(--white);font-family:var(--sans);
  font-size:17px;line-height:1.7;-webkit-font-smoothing:antialiased;overflow-x:hidden}
img,svg{max-width:100%}
a{color:var(--ice);text-decoration:none}
a:hover{text-decoration:underline;text-underline-offset:3px}
.wrap{width:min(var(--wr),calc(100% - 2.6rem));margin:0 auto}
.wide{width:min(var(--w),calc(100% - 2.6rem));margin:0 auto}

nav{position:sticky;top:0;z-index:80;background:var(--nav-bg);
  backdrop-filter:saturate(180%) blur(20px);-webkit-backdrop-filter:saturate(180%) blur(20px);
  border-bottom:1px solid var(--nav-hair)}
.nav-inner{display:flex;align-items:center;gap:1.5rem;height:58px;
  width:min(var(--w),calc(100% - 2.6rem));margin:0 auto}
.nav-brand{display:flex;align-items:center;gap:.55rem;color:var(--white);font-weight:550;
  font-size:1.02rem;letter-spacing:-.015em}
.nav-brand:hover{text-decoration:none}
.nav-logo{width:22px;height:22px;display:block}
.nav-links{display:flex;gap:1.35rem;list-style:none;margin:0;padding:0;font-size:.9rem;
  margin-left:auto;align-items:center}
.nav-links a{color:var(--grey)}
.nav-links a:hover{color:var(--white);text-decoration:none}
.nav-links .btn{padding:.48rem 1.05rem;font-size:.87rem;color:var(--on-accent)}
/* .nav-links a sets grey; the button needs its own colour back or the label
   disappears into the gradient it sits on. */
.nav-links .btn:hover{color:var(--on-accent)}
.nav-links .btn svg{flex:none}

h1{font-family:var(--sans);font-optical-sizing:auto;text-wrap:balance;font-size:clamp(2.4rem,5.2vw,4rem);line-height:1.04;letter-spacing:-.028em;
  font-weight:520;margin:.6rem 0 1rem}
/* 560, not 690, and 3.6rem, not 4.6rem.
   Measured against the four references at 1280x800: Cursor sets its h1 at 26px
   weight 400, Warp at 64px weight 400, Linear at 64px weight 510. Ours was
   73.6px at 690 — the largest and heaviest of the set by a clear margin, which
   is not confidence, it is volume. */
h2{font-family:var(--sans);font-optical-sizing:auto;text-wrap:balance;font-size:clamp(1.6rem,3.1vw,2.4rem);line-height:1.12;letter-spacing:-.024em;
  font-weight:520;margin:3.2rem 0 .9rem}
h3{font-size:1.12rem;font-weight:550;letter-spacing:-.012em;margin:2rem 0 .5rem}
p{margin:0 0 1.05rem}

/* Measure.
   Measured in the browser, not eyeballed: section paragraphs were running 127
   characters per line at 1280px. The readable band is 45–75 and the usual
   target is about 66, so this was near double the upper bound — which is why
   the page felt tiring without anything looking obviously wrong. The hero lede
   was already at 70ch and the record intro at 76ch; only the sections were
   unbounded, because they had no max-width at all and inherited the 1080px
   container.
   Headings are left alone. A wide heading is fine — you do not read it in
   lines, you read it in one glance.

   The number is 52ch, not 68ch, and the difference matters: the CSS ch unit is
   the advance width of "0", which in this face is noticeably wider than the
   average letter. 68ch measured out at 95 REAL characters per line via canvas
   metrics — still deep into the unreadable range while looking, in the
   stylesheet, like a sensible value. Set by measuring rendered text rather
   than by trusting the unit's name. */
section > p, section > ul, section > ol{max-width:52ch}
.record .rec-intro{max-width:48ch}
ul,ol{margin:0 0 1.15rem 1.2rem;padding:0}
li{margin-bottom:.5rem}
/* .grad was a three-stop gradient across the second headline line. Screenshot
   it beside Linear and Raycast and it is the one element that dates the page:
   both set their headline in a single flat colour and spend the attention on
   space instead. A gradient also fights --blue, which is the only colour on
   this site allowed to mean "do this next".
   Kept as a class so older pages do not break; it now just sets the ink. */
.grad{color:var(--white)}
.lede{font-size:clamp(1rem,1.25vw,1.075rem);line-height:1.55;color:var(--grey);margin:0 0 1.6rem}

/* --- hero -----------------------------------------------------------------
   Measured against Raycast and Linear at 1280x800 rather than guessed at.
   Ours stacked five things — pill eyebrow, gradient headline, lede, two
   buttons, a version line, three tick chips — and began 25% down the viewport.
   Theirs carry two or three and begin near 50%. The difference does not read
   as "more minimal", it reads as more certain: a page that needs three rows of
   reassurance under the button is arguing with itself.

   So the eyebrow and the tick row are gone, and what is left gets the space
   they were using. */
.hero{padding:clamp(2.6rem,6vh,4rem) 0 clamp(.6rem,1.5vh,1.2rem);text-align:left}
.hero h1{margin:0 0 1.5rem;max-width:22ch}
.hero-sub{margin-top:1.4rem;font-family:var(--mono);font-size:.8rem;
  color:var(--grey-dim);letter-spacing:-.01em}

/* One axis for the whole page.
   Screenshotted at 1280x1500, the hero was centred and every section under it
   was left-aligned. That mismatch is the actual generic tell — it is what a
   template hero looks like with hand-written content below it. Linear is left
   throughout, Raycast is centred throughout; both are internally consistent
   and that is what reads as designed rather than assembled.
   Left, because the rest of the page is already left and because a left-set
   headline over a dense evidence table reads as an instrument. Centring is for
   pages whose hero is the whole argument. */

/* --- the measured record ------------------------------------------------
   Docket's instrument vocabulary rather than a marketing stat row: mono
   numerals, a denominator that stays visible, and a caveat under every figure.
   The numbers are large because they are the argument, not decoration — and
   three of the four are failure rates, which is the whole point of showing
   them at this size.

   tabular-nums so the columns line up; a proportional 1 next to a 7 in a
   headline number reads as sloppy at this scale. */
/* The product, then the caption.
   Measured at 1280x800: Cursor puts its screenshot at y=351, Linear 550, Warp
   593 — all inside the first screen. Ours was at 2005, three screens down,
   behind a kicker, an h2 and an intro paragraph. None of the three references
   puts a heading before the product; they go headline, buttons, product, and
   explain underneath. */
.showcase{margin:0 0 clamp(2rem,4vw,3rem)}
.win-cap{max-width:64ch;margin:1.1rem 0 0;font-size:.92rem;line-height:1.6;
  color:var(--grey-dim)}
.win-cap span{color:var(--grey);font-weight:520}

.record{border-top:1px solid var(--hair);border-bottom:1px solid var(--hair);
  padding:clamp(2.4rem,4.5vw,3.4rem) 0;margin:clamp(1.6rem,3vw,2.6rem) 0}
.rec-intro{max-width:60ch;color:var(--grey);margin:.4rem 0 2.2rem}
.recs{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));
  gap:1px;background:var(--hair);border:1px solid var(--hair);border-radius:var(--r-sm);
  overflow:hidden}
.rec{background:var(--panel);padding:1.5rem 1.35rem}
.rec-n{font-family:var(--sans);font-size:clamp(2rem,4.4vw,3rem);line-height:1;letter-spacing:-.03em;
  font-weight:540;letter-spacing:-.045em;color:var(--white);
  font-variant-numeric:tabular-nums;margin:0 0 .55rem}
.rec-n span{color:var(--grey-dim);font-size:.44em;letter-spacing:-.02em}
.rec-l{margin:0 0 .5rem;font-size:.95rem;font-weight:520;letter-spacing:-.011em;
  color:var(--white);line-height:1.35}
.rec-w{margin:0;font-size:.845rem;line-height:1.5;color:var(--grey-dim)}
.rec-src{margin:1.4rem 0 0;font-size:.83rem;color:var(--grey-dim)}
.rec-src code{font-family:var(--mono);font-size:.95em;color:var(--grey)}
@media (max-width:560px){.recs{grid-template-columns:1fr}}
.note{font-size:.92rem;line-height:1.6;color:var(--grey);border-left:2px solid var(--line);padding:.1rem 0 .1rem 1rem;margin:1.2rem 0}
.muted{color:var(--grey)}
.crumb{font-size:.85rem;color:var(--grey-dim);margin:2.2rem 0 .4rem;font-family:var(--mono)}
.crumb a{color:var(--grey)}

.btn{display:inline-flex;align-items:center;justify-content:center;gap:.55rem;
  padding:.78rem 1.4rem;border-radius:999px;font-weight:600;font-size:.96rem;
  background:linear-gradient(180deg,var(--accent-lift),var(--accent-deep));color:var(--on-accent);border:1px solid transparent;
  box-shadow:0 10px 34px -12px var(--accent-glow);
  transition:transform .2s cubic-bezier(.2,.8,.2,1),box-shadow .25s}
.btn:hover{transform:translateY(-2px);box-shadow:0 16px 44px -12px var(--accent-glow-2);
  text-decoration:none}
.btn.ghost{background:transparent;color:var(--white);border:1px solid var(--hair-lit);
  box-shadow:none}
.btn.ghost:hover{border-color:var(--blue);box-shadow:none}

.hero{position:relative}
.hero::before{content:"";position:absolute;inset:-30% -50% auto;height:120%;pointer-events:none;
  background:radial-gradient(760px 420px at 50% 0,var(--accent-wash),transparent 70%)}
.hero>*{position:relative}
.hero h1{font-size:clamp(2.2rem,4.8vw,3.7rem);margin:.9rem 0 1.2rem}
.hero .lede{max-width:56ch}
.eyebrow{display:inline-flex;align-items:center;gap:.5rem;padding:.4rem 1rem;border-radius:999px;
  border:1px solid var(--hair-lit);background:var(--panel-2);color:var(--ice);
  font-size:.86rem;font-weight:520;white-space:nowrap}
/* An inline SVG with no intrinsic size fills its flex line. Without this the
   eyebrow tick rendered about 120px tall and pushed the label onto three
   lines. Every icon in this stylesheet gets an explicit box. */
.eyebrow svg{width:14px;height:14px;flex:none;color:var(--green)}
.hero-actions{display:flex;gap:.8rem;justify-content:flex-start;flex-wrap:wrap;margin:2rem 0 1rem}
.hero-sub{font-size:.88rem;color:var(--grey-dim);font-family:var(--mono)}
.trust{display:flex;gap:1.6rem;justify-content:center;flex-wrap:wrap;margin-top:2.4rem;
  font-size:.9rem;color:var(--grey)}
.trust span{display:inline-flex;align-items:center;gap:.45rem}
.trust svg{width:15px;height:15px;color:var(--green);flex:none}

section{padding:1rem 0}
.kicker{font-family:var(--mono);font-size:.76rem;letter-spacing:.1em;text-transform:uppercase;
  color:var(--blue);margin-bottom:.5rem}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:1rem;margin:1.6rem 0}
.card{display:block;padding:1.3rem 1.4rem;border:1px solid var(--hair);border-radius:var(--r);
  background:linear-gradient(180deg,var(--card),var(--panel-2));color:var(--white);
  transition:border-color .2s,transform .2s}
.card:hover{border-color:var(--hair-lit);transform:translateY(-2px);text-decoration:none}
.card strong{display:block;margin-bottom:.3rem;font-weight:550;letter-spacing:-.01em}
.card span{font-size:.9rem;color:var(--grey);line-height:1.55}
.card .num{font-family:var(--mono);font-size:2rem;font-weight:600;color:var(--blue);
  line-height:1;display:block;margin-bottom:.5rem}

.box{margin:2rem 0;padding:1.35rem 1.5rem;border:1px solid var(--hair);border-radius:var(--r-sm);
  background:var(--panel-2);color:var(--grey)}
.box strong{color:var(--white)}
.box p:last-child{margin-bottom:0}
.box.warn{border-left:3px solid var(--amber)}
.box.ok{border-left:3px solid var(--green)}

.cta-block{margin:3.4rem 0 1rem;padding:2.4rem 2rem;border:1px solid var(--hair);
  border-radius:var(--r);text-align:center;
  background:radial-gradient(600px 300px at 20% -20%,var(--accent-wash-2),transparent 70%),
    linear-gradient(180deg,var(--card),var(--panel-2))}
.cta-block p{color:var(--grey)}

table{width:100%;border-collapse:collapse;margin:1.4rem 0;font-size:.94rem;display:block;
  overflow-x:auto;white-space:nowrap}
th,td{text-align:left;padding:.72rem .8rem;border-bottom:1px solid var(--hair);vertical-align:top;
  white-space:normal}
th{font-size:.74rem;text-transform:uppercase;letter-spacing:.07em;color:var(--grey-dim);
  font-weight:600}
td strong{font-weight:550}
tbody tr:hover{background:var(--row-hover)}
blockquote{border-left:2px solid var(--blue);padding:.1rem 0 .1rem 1.1rem;margin:1.1rem 0;
  color:var(--grey);font-style:normal}
code{font-family:var(--mono);font-size:.88em;background:var(--panel-2);padding:.14em .4em;
  border-radius:6px;border:1px solid var(--hair)}
.src{font-size:.84rem;color:var(--grey-dim);font-family:var(--mono);word-break:break-all}
.pill{display:inline-block;font-family:var(--mono);font-size:.72rem;padding:.18rem .6rem;
  border-radius:999px;border:1px solid var(--hair-lit);color:var(--grey-dim);margin-right:.35rem}
.pill.checked{border-color:var(--accent-edge);color:var(--green)}
.pill.unchecked{border-color:var(--amber-edge);color:var(--amber)}

/* The product window. A screenshot would be a flat PNG that blurs on a
   retina display and cannot follow the reader's theme; this is the real
   interface rebuilt in markup, so it stays sharp and stays honest — the
   content is verbatim from a run against HoneyBook. */
.win{border:1px solid var(--hair);border-radius:14px;overflow:hidden;
  background:linear-gradient(180deg,var(--card),var(--panel));
  box-shadow:0 40px 80px -40px var(--window-shadow),0 0 0 1px var(--window-edge);
  margin:2.4rem 0}
.win-bar{display:flex;align-items:center;gap:.5rem;padding:.7rem .9rem;
  border-bottom:1px solid var(--hair);background:var(--panel-2)}
.win-dot{width:11px;height:11px;border-radius:50%;flex:none}
.win-title{margin-left:.5rem;font-size:.82rem;color:var(--grey-dim);
  font-weight:520;letter-spacing:-.01em}
.win-body{padding:1.1rem}
.vd{display:flex;gap:.75rem;align-items:flex-start;padding:.85rem 1rem;
  border:1px solid var(--hair);border-radius:10px;margin-bottom:.7rem;
  background:var(--panel-2)}
.vd.bad{border-left:3px solid var(--bad)}
.vd.warn{border-left:3px solid var(--amber)}
.vd-ic{font-family:var(--mono);font-weight:600;flex:none;line-height:1.5}
.vd.bad .vd-ic{color:var(--bad)} .vd.warn .vd-ic{color:var(--amber)}
.vd strong{display:block;font-weight:550;letter-spacing:-.01em;margin-bottom:.15rem}
.vd span{font-size:.9rem;color:var(--grey);line-height:1.5}
/* display:block because this sits inside a <span>; without it the quote runs
   on from the sentence above and reads as one run-on line. */
.vd-quote{display:block;margin:.5rem 0 0;padding-left:.8rem;border-left:2px solid var(--hair-lit);
  font-size:.88rem;color:var(--grey)}
@media(max-width:640px){.win-body{padding:.7rem}.vd{padding:.7rem .8rem}}

footer{border-top:1px solid var(--hair);margin-top:4rem;padding:2.6rem 0 3.4rem;
  color:var(--grey-dim);font-size:.9rem}
footer a{color:var(--grey)}
footer .foot-brand{display:flex;align-items:center;gap:.5rem;color:var(--white);
  font-weight:550;margin-bottom:.7rem}
@media(max-width:640px){
  body{font-size:16px}
  .hero{padding:3.2rem 0 2.4rem}
  .nav-links{gap:.9rem;font-size:.84rem}
  .nav-links li:nth-child(3){display:none}

  /* At 375px this nav was 442px wide — six links plus the Download button, with
     nowhere to go. Shrinking the gap and hiding one item was not enough, and the
     consequence was not merely a clipped nav: the document became 521px wide, so
     the LAYOUT VIEWPORT widened, and `position:fixed; right:.85rem` on the theme
     toggle resolved against that instead of the screen. The toggle rendered
     132px off the right edge — invisible and unreachable on a phone, a control I
     added the same evening and would not have found by looking at a desktop.
     A horizontal overflow does not stay a local problem. */
  .nav-links{
    flex:1 1 auto; min-width:0;
    overflow-x:auto; -webkit-overflow-scrolling:touch;
    scrollbar-width:none;
  }
  .nav-links::-webkit-scrollbar{display:none}
  .nav-links li{flex:none}

  /* WCAG 2.2 Target Size (Minimum). Measured on the live page at 375px: nav
     links were 16-17px tall and footer links 15px, all with the hit box exactly
     the height of the text. */
  .nav-links a, footer a, .src a{display:inline-flex;align-items:center;min-height:24px}
}
"""

LOGO_SVG = (
    '<svg class="nav-logo" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">'
    '<rect width="100" height="100" rx="22" fill="#1b1714"/>'
    '<rect x="14" y="14" width="14" height="72" rx="4" fill="#f0b429"/>'
    '<rect x="33" y="14" width="53" height="72" rx="6" fill="#f0b429"/>'
    '<circle cx="46" cy="70" r="9.5" fill="#1b1714"/><circle cx="46" cy="70" r="4.3" fill="#f0b429"/>'
    '<circle cx="61" cy="53" r="5" fill="#1b1714"/><circle cx="75" cy="36" r="5" fill="#1b1714"/>'
    "</svg>"
)

NAV = [("/specs/", "Ad specs"), ("/learn/", "Learn"),
       ("/for/", "By business"), ("/vs/", "Compare")]
# The nav and footer Download links. Derived, not typed — this was the FOURTH
# hardcoded copy of the release URL in this repo, after the one in content.py and
# the version strings in the hero and the legal pages. Publishing 0.1.89 updated
# the #get section and left the nav button, the hero line and the footer pointing
# at a build from the previous midnight, on the same page, at the same time.
#
# One source now. If content.py cannot reach the GitHub API it falls back to the
# releases PAGE, which is always true, so this cannot invent a URL either.
from content import DMG as DOWNLOAD  # noqa: E402
# Plausible, added to the GENERATOR rather than to index.html.
#
# It was originally pasted straight into the generated index.html (e4d0020). That
# file is rebuilt from here, so the next render silently deleted it and the site
# would have gone back to having no analytics at all while looking like it had
# some. Anything that must survive a rebuild belongs in _build/.
#
# Cookieless and carries no personal data, but the privacy page discloses it by
# name regardless — it previously claimed there was no script at all, which was
# false the moment this went live.
ANALYTICS = ('<script defer data-domain="adplaybook.app" '
             'src="https://plausible.io/js/script.js"></script>'
             # Sled affiliate attribution. It sets a ta_ref cookie only when a
             # visitor arrives through an affiliate link, so an ordinary visitor
             # gets no cookie at all — which is why the privacy page describes it
             # as conditional rather than as tracking everybody.
             #
             # Added 2026-08-14 because affiliate tracking was live on
             # crispvideo.app and NOWHERE ELSE. The board read "tracker verified
             # real and serving", which was true of one site out of four, so an
             # affiliate who sent someone to AdPlaybook, Docket or Outlier earned
             # nothing and had no way to know.
             '<script async src="https://usesled.com/kerr-and-company/t.js">'
             '</script>')

DL_ICON = ('<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" '
           'width="15" height="15" aria-hidden="true"><path d="M8 1.5v9m0 0L4.5 7M8 10.5 11.5 7"/>'
           '<path d="M2 11.5v2A1.5 1.5 0 0 0 3.5 15h9a1.5 1.5 0 0 0 1.5-1.5v-2"/></svg>')
TICK = ('<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2" '
        'aria-hidden="true"><path d="M2.5 8.5l3.5 3.5 7.5-8"/></svg>')


def esc(s: Any) -> str:
    return html.escape(str(s), quote=True)


def page(*, path: str, title: str, description: str, body: str,
         schema: Dict[str, Any] | None = None, modified: str = BUILT,
         wide: bool = False) -> None:
    """Write one page. `path` is the URL path, e.g. /specs/linkedin/."""
    url = BASE_URL + path
    wrapcls = "wide" if wide else "wrap"
    nav = "".join(f'<li><a href="{h}">{esc(t)}</a></li>' for h, t in NAV)
    nav += f'<li><a class="btn" href="{DOWNLOAD}">{DL_ICON}Download</a></li>'
    ld = ""
    if schema:
        ld = ('<script type="application/ld+json">'
              + json.dumps(schema, separators=(",", ":")) + "</script>")

    doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<meta name="theme-color" content="#0d1017">
<meta name="last-modified" content="{modified}">
<link rel="canonical" href="{url}">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<script>/* Before first paint, or the page flashes the wrong theme and the flash
tells every visitor the site is cheap. Must stay INLINE and stay in <head>.
Braces are doubled because this template is an f-string. */
(function(){{try{{var t=localStorage.getItem("adplaybook-theme");
if(t){{document.documentElement.setAttribute("data-theme",t);}}}}catch(e){{}}}})();</script>
<meta property="og:type" content="{'website' if path == '/' else 'article'}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:url" content="{url}">
<meta property="og:site_name" content="{BRAND}">
<meta property="og:image" content="{BASE_URL}/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="AdPlaybook - it writes the ad, then it tries to prove you wrong.">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{BASE_URL}/og.png">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(description)}">
<style>{CSS}</style>
{ld}
{ANALYTICS}
</head>
<body>
<nav><div class="wrap nav-inner">
<a class="nav-brand" href="/">{LOGO_SVG}{BRAND}</a>
<ul class="nav-links">{nav}</ul>
<button id="themeToggle" type="button" aria-label="Switch between light and dark">&#9686;</button>
</div></nav>
<div class="{wrapcls}">{body}</div>
<footer><div class="wide">
<div class="foot-brand">{LOGO_SVG}{BRAND}</div>
<p>{esc(TAGLINE)}</p>
<p>Every figure on this site is quoted from the platform's own documentation with
the date it was read. Where something could not be verified, the page says so
rather than leaving a gap you cannot see.</p>
<p><a href="/specs/">Ad specs</a> · <a href="/learn/">Learn</a> ·
<a href="/vs/">Compare</a> · <a href="{DOWNLOAD}">Download</a> ·
<a href="/llms.txt">llms.txt</a></p>
<p><a href="/privacy/">Privacy</a> · <a href="/terms/">Terms</a> ·
<a href="/contact/">Contact</a></p>
<p>Published by Kerr &amp; Company LLC, Grand Rapids, Michigan. Free to
download and free forever on one website. $149 once for unlimited websites.</p>
</div></footer>
<script>/* THIS MUST STAY IN THE BODY. On 2026-08-13 the identical handler was
placed inside the pre-paint <head> script on kerrandcompanyholdings.com, where it
ran before <body> existed, so getElementById returned null and no listener was
ever attached. The button rendered perfectly and did nothing — and a dead toggle
is indistinguishable from a live one in a screenshot. ~/ops/bin/theme-toggle-gate.py
checks this position specifically. */
(function(){{
  var b=document.getElementById("themeToggle");
  if(!b)return;
  b.addEventListener("click",function(){{
    var c=document.documentElement.getAttribute("data-theme");
    if(!c){{c="dark";}}  /* dark is this site's default, not the OS preference */
    var n=c==="dark"?"light":"dark";
    document.documentElement.setAttribute("data-theme",n);
    try{{localStorage.setItem("adplaybook-theme",n);}}catch(e){{}}
  }});
}})();</script>
</body>
</html>
"""
    out = SITE / path.strip("/") / "index.html" if path != "/" else SITE / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc)
    PAGES.append((path, modified))


PAGES: List[tuple] = []


# ---------------------------------------------------------------------------
# Platform spec pages — the reason this site can win
# ---------------------------------------------------------------------------

def _fmt_limit(pl: Dict[str, Any], stem: str) -> str:
    safe, hard = pl.get(f"{stem}_chars"), pl.get(f"{stem}_max_chars")
    if safe and hard and safe != hard:
        return f"<strong>{safe}</strong> to stay visible · {hard} hard cap"
    if safe:
        return f"<strong>{safe}</strong>"
    if hard:
        return f"<strong>{hard}</strong>"
    return '<span class="pill unchecked">not stated</span>'


def spec_page(spec: Dict[str, Any]) -> None:
    key, name = spec["key"], spec["name"]
    manager = spec.get("manager_name", name)
    placements = spec.get("placements", [])
    checked = [p for p in placements if p.get("verified_on")]
    read_on = max((p["verified_on"] for p in checked), default=None)

    rows = []
    for p in placements:
        rows.append(
            f"<tr><td><strong>{esc(p.get('name', p['key']))}</strong><br>"
            f"<span class='src'>{esc(p.get('aspect_ratio', ''))} "
            f"{esc(p.get('recommended_resolution', ''))}</span></td>"
            f"<td>{_fmt_limit(p, 'headline')}</td>"
            f"<td>{_fmt_limit(p, 'primary_text')}</td>"
            f"<td>{esc(p.get('max_file_size_mb', '—'))}"
            f"{' MB' if p.get('max_file_size_mb') else ''}</td></tr>"
        )

    notes = []
    for p in placements:
        for stem, label in (("headline", "Headline"), ("primary_text", "Body text"),
                            ("description", "Description")):
            n = p.get(f"{stem}_note")
            if n and '"' in n:
                notes.append(f"<h3>{esc(p.get('name', p['key']))} — {label}</h3>"
                             f"<blockquote>{esc(n)}</blockquote>")

    unverified = spec.get("_unverified", [])
    unv_html = ""
    if unverified:
        items = "".join(f"<li>{esc(u)}</li>" for u in unverified)
        unv_html = (
            '<div class="box warn"><strong>What we could not verify</strong>'
            f"<ul>{items}</ul>"
            "<p>Listed rather than omitted. A spec sheet with no gaps is either "
            "complete or hiding something, and from the outside those look "
            "identical.</p></div>"
        )

    caveat = spec.get("_experiment_caveat", "")
    # The heading is derived from the platform's own numbers rather than being
    # one shared string. Seven spec pages with an identical H2 skeleton is what
    # a thin-content penalty is actually measuring — the pages differ in
    # substance, so they should differ in shape.
    caveat_head = {
        "linkedin": "Small audiences and the cost of splitting them",
        "tiktok":   "Why an ad group here refuses to spend",
        "youtube":  "Decide the video length before anything else",
        "pinterest": "The description nobody reads",
        "x":        "A link costs you 23 characters",
        "reddit":   "The comment thread is part of the ad",
        "google":   "Responsive ads recombine before anyone sees them",
        "meta":     "What the learning phase does to a test",
    }.get(key, "What breaks a campaign here")
    caveat_html = (f"<h2>{esc(caveat_head)}</h2><p>{esc(caveat)}</p>"
                   if caveat else "")

    targeting = spec.get("targeting_capabilities", {}) or {}
    floors = []
    for k, v in targeting.items():
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            note = targeting.get(f"{k}_note", "")
            floors.append(f"<li><strong>{esc(k.replace('_', ' '))}: {v}</strong> — {esc(note)}</li>")
    floor_label = {
        "linkedin": "The 300-account floor, per ad set",
        "tiktok": "The 1,000 matched-user floor",
        "youtube": "The 10 and 12 second thresholds",
    }.get(key, "Hard floors")
    floor_html = (f'<div class="box"><strong>{esc(floor_label)}</strong><ul>{"".join(floors)}</ul>'
                  "<p>These are the numbers that decide whether a campaign delivers "
                  "at all, and none of them produces an error message when you "
                  "cross it.</p></div>" if floors else "")

    src = spec.get("source_url", "")
    check_head = ("Count these before you paste" if placements and any(
        p.get("headline_chars") or p.get("primary_text_chars") for p in placements)
        else "Check a campaign against this spec")
    title = f"{name} ad specs and character limits ({BUILT[:4]}) | {BRAND}"
    desc = (f"{name} ad character limits, image sizes and hard floors. Every "
            f"figure quoted from {name}'s own documentation with the date it was read"
            + (f", {read_on}." if read_on else "."))

    body = f"""
<article>
<p class="crumb"><a href="/specs/">Ad specs</a> / {esc(name)}</p>
<h1>{esc(name)} ad specs and character limits</h1>
<p class="lede">{esc(desc)}</p>

<div class="box ok">
<p style="margin:0"><span class="pill checked">read {esc(read_on or 'unverified')}</span>
Source: <a class="src" href="{esc(src)}" rel="nofollow noopener">{esc(src)}</a></p>
</div>

<h2>Character limits and sizes</h2>
<table><thead><tr><th>Placement</th><th>Headline</th><th>Body text</th><th>Max file</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table>
<p>Where two numbers are given, the first is what stays visible and the second
is what the field accepts. They're different questions. Copy over the cap gets
rejected at upload. Copy over the visible limit runs, and gets cut off. Most
guides publish only one of the two.</p>

{floor_html}
{''.join(notes[:6])}
{caveat_html}
{unv_html}

<h2>{check_head}</h2>
<p>{BRAND} holds this spec as dated data and checks a finished campaign against
it — character counts, audience floors, forbidden exclusions — before you paste
anything into {esc(manager)}. It is arithmetic, not a judgement call, so it runs
on every campaign and costs nothing.</p>
<p><a class="btn" href="/#get">Get {BRAND}</a>
<a class="btn ghost" href="/specs/">All eight platforms</a></p>
</article>
"""
    page(path=f"/specs/{key}/", title=title, description=desc, body=body,
         modified=read_on or BUILT,
         schema={
             "@context": "https://schema.org", "@type": "TechArticle",
             "headline": f"{name} ad specs and character limits",
             "description": desc, "datePublished": read_on or BUILT,
             "dateModified": read_on or BUILT,
             "publisher": {"@type": "Organization", "name": BRAND},
             "isBasedOn": src,
         })


def load_specs(app_repo: Path) -> List[Dict[str, Any]]:
    d = app_repo / "backend" / "adkit" / "platforms"
    if not d.is_dir():
        sys.exit(f"platform specs not found at {d} — pass --app-repo")
    out = []
    for f in sorted(d.glob("*.json")):
        spec = json.loads(f.read_text())
        # Recompute the unverified list the same way the app does, so the page
        # and the product can never disagree about what was checked.
        unv = []
        for p in spec.get("placements", []):
            if not p.get("verified_on"):
                unv.append(f"The limits for {p.get('name', p['key'])} were never "
                           "checked against the platform's own documentation.")
        if not spec.get("cta_buttons_verified_on"):
            unv.append("Which call-to-action buttons this platform offers.")
        if not (spec.get("special_ad_categories") or {}).get("verified_on"):
            unv.append("Which ad categories are restricted here, and what "
                       "declaring one does to your targeting.")
        if not (spec.get("measurement") or {}).get("verified_on"):
            unv.append("How this platform tracks conversions, and its default "
                       "attribution window.")
        spec["_unverified"] = unv
        out.append(spec)
    return out


def specs_hub(specs: List[Dict[str, Any]]) -> None:
    cards = "".join(
        f'<a class="card" href="/specs/{s["key"]}/"><strong>{esc(s["name"])}</strong>'
        f'<span>{len(s.get("placements", []))} placement(s) · '
        f'{len(s["_unverified"])} thing(s) unverified</span></a>'
        for s in specs
    )
    body = f"""
<article>
<p class="crumb">Ad specs</p>
<h1>Ad specs and character limits, with sources</h1>
<p class="lede">Eight platforms. Every number quoted from the platform's own
documentation, with the URL it came from and the date it was read.</p>

<div class="box warn">
<strong>Why this page exists</strong>
<p>The guides ranking for these queries are frequently wrong, and none of them
show their working. Two examples found while building this, both checked
against the platforms' own help centres on 2026-08-10:</p>
<ul>
<li>A widely-ranked page states LinkedIn's introductory text maxes out at 600
characters. LinkedIn's own help centre says <strong>3,000</strong>, with 150 to
avoid truncation.</li>
<li>Several pages state TikTok caps ad captions at 100 characters. TikTok's own
in-feed specification page states <strong>no character count at all</strong>.
The figure appears nowhere in their documentation.</li>
</ul>
<p>Undated and uncited is the norm. So every figure here carries its source and
its date, and anything that could not be read is listed as unverified rather
than quietly skipped.</p>
</div>

<div class="cards">{cards}</div>

<h2>Where these come from</h2>
<p>These pages are generated from the same files {BRAND} itself reads when it
builds a campaign, so the site cannot drift from the product. When a platform
changes a limit and the spec is re-checked, the page changes with it.</p>
<p><a class="btn" href="/#get">Get {BRAND}</a></p>
</article>
"""
    page(path="/specs/", title=f"Ad specs and character limits for 8 platforms | {BRAND}",
         description=("Ad character limits, image sizes and hard floors for Meta, Google, "
                      "LinkedIn, TikTok, X, Pinterest, Reddit and YouTube — every figure "
                      "quoted from the platform's own documentation with the date read."),
         body=body)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--app-repo", default=str(Path.home() / "ad maker app"))
    args = ap.parse_args()

    specs = load_specs(Path(args.app_repo))
    specs_hub(specs)
    for s in specs:
        spec_page(s)

    from content import build_rest  # noqa: E402
    build_rest(page, specs, PAGES)

    # Inside the build, not after it. The sitemap is written from PAGES, which
    # page() appends to — a hub built by a separate script produces four live
    # pages that no crawler is told about, which the gate caught.
    from howto import build as build_howto  # noqa: E402
    build_howto(page)

    # sitemap
    urls = "".join(
        f"<url><loc>{BASE_URL}{p}</loc><lastmod>{m}</lastmod></url>"
        for p, m in sorted(set(PAGES))
    )
    (SITE / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        f"{urls}</urlset>\n")

    print(f"built {len(PAGES)} pages")
    for p, _ in sorted(set(PAGES)):
        print(f"  {p}")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    raise SystemExit(main())
