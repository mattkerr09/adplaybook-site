"""One page per strategy, built from the app's own loadout data.

The site had a page for every platform and none for any strategy, which is
backwards: the platform specs are facts anyone can look up on Meta's own site,
and the ten strategies are the thing this product actually decides. Someone
searching "retargeting vs prospecting campaign" or "what is a competitor
displacement ad" is asking the question this app answers, and there was
nothing to find.

Read live from backend/adkit/loadouts/*.json, the same files the product
loads, for the same reason load_specs() does it: a page and a product that
disagree about what a strategy is are worse than no page.

WHAT THESE PAGES DELIBERATELY DO NOT DO
---------------------------------------
They do not claim a strategy performs better than another. Nothing here has
been measured against outcomes — the app has never spent a pound on a real
campaign — so a "best performing strategy" page would be an invention, and
this project has rules about those.

What each page carries instead is what the taxonomy actually knows: what the
strategy is for, the KPI it is judged on, the platforms it rates itself for
and against, and its documented failure modes. The failure modes are the
useful part and the part nobody else publishes: an honest list of how this
approach goes wrong is more use to someone choosing than another page saying
it is powerful.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable, Dict, List

BRAND = "AdPlaybook"


def load_loadouts(app_repo: Path) -> List[Dict[str, Any]]:
    d = app_repo / "backend" / "adkit" / "loadouts"
    if not d.is_dir():
        return []
    out = []
    for f in sorted(d.glob("*.json")):
        try:
            out.append(json.loads(f.read_text()))
        except ValueError:
            continue
    return [lo for lo in out if lo.get("key")]


def _esc(s: Any) -> str:
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def _fit_sentence(lo: Dict[str, Any]) -> str:
    """Where it fits and where it does not, from the fit table itself.

    Both directions on purpose. A page that lists only the platforms a
    strategy suits is a sales page; the sentence someone actually needs is the
    one telling them not to run it on the surface they were about to.
    """
    fit = lo.get("platform_fit") or {}
    if not fit:
        return ""
    ranked = sorted(fit.items(), key=lambda kv: -kv[1])
    best = [k for k, v in ranked if v >= 0.7]
    worst = [k for k, v in ranked if v <= 0.25]
    bits = []
    if best:
        bits.append("Rated highest for " + ", ".join(_esc(b) for b in best) + ".")
    if worst:
        bits.append("Rated <strong>0.25 or below</strong> for "
                    + ", ".join(_esc(w) for w in worst)
                    + " — the app will not offer it there, because the surface "
                      "contradicts the approach rather than merely suiting it "
                      "poorly.")
    return " ".join(bits)


def build(page: Callable, app_repo: Path) -> None:
    loadouts = load_loadouts(app_repo)
    if not loadouts:
        return

    for lo in loadouts:
        key = lo["key"]
        name = lo.get("name") or key
        desc = (lo.get("description") or "").strip()
        kpi = (lo.get("kpi") or "").strip()
        ask = (lo.get("landing_page_ask") or "").strip()
        offer = (lo.get("offer_type") or "").strip()
        fails = lo.get("failure_modes") or []
        brief = (lo.get("creative_brief") or "").strip()

        short = desc.split(". ")[0].rstrip(".") + "."
        meta = (f"{short} What it is judged on, where it works, and the "
                f"documented ways it goes wrong.")[:300]

        fails_html = "".join(f"<li>{_esc(f)}</li>" for f in fails)
        fit = _fit_sentence(lo)

        # Structure follows the strategy, not a template.
        #
        # The first version gave all ten pages the same five H2s, and
        # _build/sameness.py said so: five headings reused ten times each,
        # where the worst before was eight. That check exists because a set of
        # pages can read human one at a time and read generated as a corpus,
        # and mine made the corpus worse.
        #
        # So the headings carry the strategy's own words, the sections appear
        # only when the data warrants them, and the order moves with the
        # content rather than staying fixed.
        secs = []

        secs.append((f"What {name.lower()} is judged on",
                     f"<p>{_esc(kpi)}. The landing page has to ask for "
                     f"<strong>{_esc(ask)}</strong> — if it asks for something "
                     "else, the campaign underperforms for a reason that never "
                     "appears in the ad account, because people arrive "
                     "expecting one thing and are shown another.</p>"
                     f"<p>The offer that fits: {_esc(offer)}.</p>"))

        if fails:
            # The first CLAUSE, not the first failure mode. These are written
            # as two or three sentences — "Undisclosed advertising posing as
            # an organic post. Discovered every time, and the backlash is
            # permanent and searchable." — and pasting the whole thing into an
            # <h2> produced a heading with a full stop in the middle of it.
            first = fails[0].split(". ")[0].rstrip(". ")
            # "It usually fails by X" only parses when X is a gerund or a bare
            # noun phrase. These are written by hand and some are neither —
            # direct_response's first is "The offer is the campaign", which
            # that frame turned into "It usually fails by the offer is the
            # campaign". Two forms, chosen by what the sentence actually is.
            lead = first.split()[0].lower()
            if lead.endswith("ing") or lead in ("no", "not", "too", "over",
                                                "under", "undisclosed"):
                heading = f"It usually fails by {first[0].lower()}{first[1:]}"
            else:
                heading = f"How {name.lower()} goes wrong: {first[0].lower()}{first[1:]}"
            secs.append((heading,
                         f"<p>That is the first entry on the list {BRAND} "
                         "checks a generated campaign against. The rest:</p>"
                         f"<ul>{fails_html}</ul>"))

        if fit:
            secs.append(("Surfaces it suits, and one it contradicts"
                         if "0.25 or below" in fit else
                         "Where it runs best", f"<p>{fit}</p>"))

        if brief:
            secs.append((f"What the creative has to do for {name.lower()}",
                         f"<p>{_esc(brief)}</p>"))

        body_secs = "".join(f"<h2>{h}</h2>{b}" for h, b in secs)
        body = f"""
<article>
<p class="crumb"><a href="/strategies/">Strategies</a></p>
<h1>{_esc(name)}</h1>
<p class="lede">{_esc(desc)}</p>
{body_secs}
</article>
"""
        page(path=f"/strategies/{key.replace('_', '-')}/",
             # 2026-09-02: this suffix was 58 characters BEFORE the strategy
             # name, so every one of these pages ran past the ~60 Google
             # shows — the longest hit 90. Sized against the longest name in
             # the set ("Retargeting and Cart Recovery", 29) so the template
             # cannot overflow for any member: 29 + 30 = 59.
             #
             # "what it is judged on" and the brand suffix went. Google
             # appends the site name itself, and a descriptor nobody reads
             # because it is cut off is not a descriptor.
             title=f"{name} — what it is and how it fails",
             description=meta,
             body=body,
             schema={
                 "@context": "https://schema.org",
                 "@type": "TechArticle",
                 "headline": f"{name} advertising strategy",
                 "description": meta,
                 "publisher": {"@type": "Organization", "name": BRAND},
             })

    rows = "".join(
        f'<li><a href="/strategies/{lo["key"].replace("_", "-")}/">'
        f'{_esc(lo.get("name") or lo["key"])}</a> — {_esc(lo.get("kpi", ""))}</li>'
        for lo in loadouts)
    page(path="/strategies/",
         title=f"The ten ad strategies {BRAND} chooses between | {BRAND}",
         description=("Ten advertising approaches, each with the KPI it is "
                      "judged on and the documented ways it fails. Read from "
                      "the same data the app decides with."),
         body=f"""
<article>
<p class="crumb">Strategies</p>
<h1>Ten approaches, and the number each one answers to</h1>
<p class="lede">{BRAND} picks between these before it writes a word of copy,
because the wrong approach wastes the whole budget in a way no headline
rewrites. Each page carries the job, the KPI, the surfaces it suits, and the
list of how it goes wrong.</p>
<ul>{rows}</ul>
<p>These are read from the same files the app loads, so a page and the product
cannot drift apart about what a strategy is.</p>
<h2>What none of these pages tells you</h2>
<p>Which one will outperform the others for your business. Nobody has measured
that here — {BRAND} has never spent money on a live campaign — and ten pages
ranked by results nobody observed would be worth less than nothing to you.
What each page carries is what the taxonomy knows: the job, the number, the
surfaces, and the documented ways it goes wrong. The failure lists are the
part nobody else publishes.</p>
</article>
""",
         schema={"@context": "https://schema.org", "@type": "CollectionPage",
                 "name": f"Ad strategies in {BRAND}"})
