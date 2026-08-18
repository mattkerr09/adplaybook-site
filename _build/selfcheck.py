#!/usr/bin/env python3
"""Run AdPlaybook's own gate over an ad written for AdPlaybook, and publish it.

The site's argument is that this app refuses to write things it cannot back up.
Until now the page made that argument twice — once in prose, once through the
HoneyBook showcase, which is a real run but a run against somebody else's site
from 2026-08-11. Neither lets a reader watch the mechanism work on something
they can go and check themselves.

So this points the product at us. It crawls adplaybook.app, takes three ad
variants written for AdPlaybook, and runs the two stages that need no model:

  gate.check()        — every claim traced to a span observed during the crawl
  feasibility.check() — the copy measured against the platform's own limits

WHAT IS HONEST TO CLAIM ABOUT THIS, and the page says exactly this much:

  The three variants were written BY HAND, here, on purpose. A generated
  campaign needs a model, a model needs a key or a local server, and the
  result would then vary between builds — so the specimen is fixed and the
  page says who wrote it. What is NOT hand-written is every verdict below it.
  Those come from `adkit.gate` and `adkit.feasibility`, the same modules the
  shipped app runs, against a live crawl of this site.

Variant C carries claims that are not on this site — a 62% cost-per-click
reduction, 40 variants in 9 seconds. They are there to be caught.

TWO THINGS THE FIRST DRAFT GOT WRONG, both found by shipping it.

**It planted social proof.** "Trusted by 4,000 marketers" and "Rated 4.9 out of
5" went live, and ops/bin/traction-gate.py caught them on the homepage —
correctly. A fabricated traction claim printed in order to refute it is still
that string, published, on our own domain, where a search snippet or an answer
engine can lift it away from the strike-through that makes it false. The gate
cannot tell refutation from assertion, and neither can a snippet. Exempting the
gate was the wrong repair: it guards six sites and its worth comes from having
no exceptions. Performance promises exercise the same code — gate._find_undeclared
hunts speed and price promises alongside social proof — so the demonstration is
unchanged and nothing about our traction is asserted anywhere.

**The specimen substantiated itself.** This section prints variant C's copy, so
the next crawl of this site READ THAT COPY BACK and the gate cleared all three
variants. The planted claims had become true statements about the site, because
we published them. That is the corollary in ops/RULES.md — a check that compares
a thing to itself proves nothing — arriving through a door nobody was watching.
`_drop_specimen_page` removes the page carrying this section from the evidence
before the gate runs, and the page says so.

WHY THE JSON IS COMMITTED rather than the check running inside render.py: the
crawl is a live network call, and a site build that fails because a crawler
was rate-limited is a build that gets bypassed. Same reason `_record()` reads
an archived corpus. The date and version below travel with the data so the
page can print how old the specimen is instead of implying it is from today.

    python _build/selfcheck.py [--app-repo PATH]
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, timezone, datetime
from pathlib import Path

OUT = Path(__file__).resolve().parent / "selfcheck.json"
SITE_URL = "https://adplaybook.app"


# ---------------------------------------------------------------------------
# The specimen. Hand-written, and the page says so.
# ---------------------------------------------------------------------------

def _variants(V):
    return [
        V(label="A — control",
          headline="Every claim, checked against your own site",
          primary_text=(
              "AdPlaybook turns a product page into a complete ad campaign — "
              "strategy, audiences, exclusions, copy, a test matrix and a "
              "measurement plan — then attacks its own work before it shows "
              "you anything."),
          description="Free download for Mac.",
          axis="control", cta_intent="download the app", cta="Download",
          tests="Baseline. Every other cell is measured against this."),
        V(label="B — the specs axis",
          headline="Eight platforms, every number quoted",
          primary_text=(
              "Ad specs go stale and the pages ranking for them are wrong. "
              "AdPlaybook reads each platform's own published limits and checks "
              "your copy against them by arithmetic, before you paste anything "
              "into an ads manager."),
          description="Free download for Mac.",
          axis="leads with spec accuracy rather than the review pass",
          cta_intent="download the app", cta="Download",
          tests="A win means spec accuracy is the stronger hook."),
        V(label="C — the performance axis",
          headline="Cut your cost per click by 62%",
          primary_text=(
              "AdPlaybook writes 40 tested variants in 9 seconds and cuts cost "
              "per click by 62% on average. Start your free trial today and "
              "see results in the first week."),
          description="Free download for Mac.",
          axis="an outcome promise instead of mechanism",
          cta_intent="start a trial", cta="Sign Up",
          tests="A win would mean an outcome promise beats a mechanism."),
    ]


def _drop_specimen_page(crawl) -> list:
    """Remove the page that renders this specimen from its own evidence.

    The section built from this data quotes variant C verbatim. Once it is
    live, a crawl of this site reads those sentences back and the gate
    substantiates them — against a page that only contains them because we
    printed them. The demonstration then reports every variant clean, which is
    the exact opposite of what it is for.

    Verified rather than assumed: the first live run blocked one variant on
    five claims; the run immediately after the section shipped cleared all
    three, and the crawl had grown by exactly one span.

    Only the page carrying the section is dropped. Everything else on the site
    stays, which is why "Eight platforms" still resolves — it sits on
    /for/agencies/, which was making that claim long before this ran.
    """
    roots = {r.rstrip("/") for r in
             (SITE_URL, SITE_URL + "/", SITE_URL + "/index.html")}
    removed = sorted(u for u in crawl.corpus if u.rstrip("/") in roots)
    for u in removed:
        crawl.corpus.pop(u, None)
    for k, ev in list(crawl.evidence.items()):
        if getattr(ev, "url", "").rstrip("/") in roots:
            crawl.evidence.pop(k, None)
    return removed


def build(app_repo: Path) -> dict:
    sys.path.insert(0, str(app_repo / "backend"))
    from adkit import __version__ as app_version
    from adkit import feasibility, gate, ingest as ing, loadouts as L, platforms as P
    from adkit.generate import (Audience, BudgetShape, Campaign, CreativeConcept,
                                Exclusion, GeneratedCampaign, MeasurementPlan, Variant)
    from adkit.models import ProductBrief

    crawl = ing.ingest(SITE_URL, max_pages=8, max_seconds=120)
    dropped = _drop_specimen_page(crawl)

    plat = P.get("linkedin")
    place = plat.placements[0]
    loadout = L.get(sorted(L.load_all().keys())[0])
    variants = _variants(Variant)

    campaign = Campaign(
        objective="WEBSITE_VISIT",
        campaign_name="AdPlaybook — self-check specimen",
        audiences=[Audience(
            name="Performance marketers", kind="job_title",
            definition="LinkedIn members with paid-media job titles at companies under 200 staff.",
            why="They are the people who paste copy into an ads manager and find the limit there.")],
        exclusions=[Exclusion(
            name="Existing users",
            definition="Site visitors who reached /download/ in the last 90 days.",
            why="Paying to reach people who already have the app.")],
        concepts=[CreativeConcept(
            name="The blocked variant",
            visual_direction="The app's own review pane in its red state.",
            first_frame="A variant struck through, with the reason beside it.",
            alt_text="AdPlaybook blocking an ad variant for an unverifiable claim.",
            caption_note="No claim in the image that is not on this site.")],
        variants=variants,
        budget=BudgetShape(
            daily_minimum_reasoning="LinkedIn needs 300 members per ad set to deliver.",
            split="Even across three cells.", ramp="Hold 14 days before judging.",
            schedule="Continuous."),
        measurement=MeasurementPlan(
            primary_event="Download started", fallback_event="Landing page view",
            what_success_looks_like="One cell's download rate clears the control by more than the noise.",
            when_to_judge="After 14 days.",
            honest_caveat="A desktop download is not a paying customer.",
            how_the_result_gets_back="Plausible goal, read weekly."),
        claims_used=["Eight platforms", "Cut your cost per click by 62%",
                     "40 tested variants in 9 seconds", "62% on average"],
    )

    gen = GeneratedCampaign(
        campaign=campaign, loadout=loadout, platform=plat, placement=place,
        brief=ProductBrief(source_url=SITE_URL, name="AdPlaybook"))

    g = gate.check(gen, crawl)
    # audience_size is deliberately not supplied: we do not know it, and the
    # whole point is that the unknown is reported rather than passed.
    f = feasibility.check(gen)

    return {
        "generated_on": date.today().isoformat(),
        "app_version": app_version,
        "site": SITE_URL,
        "platform": f"{plat.name} — {place.get('name', '')}",
        "crawl": {
            "reliable": bool(crawl.reliable),
            "spans": len(crawl.evidence),
            "excluded_pages": dropped,
            "blind_spots": list(crawl.blind_spots),
        },
        "variants": [
            {"label": v.label, "headline": v.headline,
             "primary_text": v.primary_text, "axis": v.axis}
            for v in variants
        ],
        "gate": {
            "summary": g.summary(),
            "blocked": list(g.blocked_variants),
            "passed": list(g.passed_variants),
            "claims": [
                {"text": c.text, "verdict": c.verdict.value, "note": c.note,
                 "source_url": c.source_url, "undeclared": bool(c.undeclared)}
                for c in g.claims
            ],
        },
        "feasibility": {
            "summary": f.summary(),
            "will_run": bool(f.will_run),
            "issues": [
                {"severity": i.severity.value, "where": i.where, "what": i.what,
                 "quote": i.quote, "fix": i.fix}
                for i in f.issues
            ],
            "not_checked": list(f.not_checked),
        },
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--app-repo", default=str(Path.home() / "ad maker app"))
    args = ap.parse_args()

    data = build(Path(args.app_repo))
    OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")

    gsum = data["gate"]["summary"]
    fsum = data["feasibility"]["summary"]
    print(f"wrote {OUT}")
    print(f"  crawl      : {data['crawl']['spans']} spans, reliable={data['crawl']['reliable']}")
    print(f"  gate       : {gsum}")
    print(f"  feasibility: {fsum}")


if __name__ == "__main__":
    main()
