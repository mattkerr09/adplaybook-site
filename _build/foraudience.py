"""/for/ pages — advertising by kind of business.

The strongest commercial-intent queries in this space are "<platform> ads for
<trade>". The temptation is to generate sixty of them from one template with
the noun swapped, which is exactly what a thin-content penalty is for, and what
the sibling project's sameness.py exists to catch.

So each page here is built from three things that genuinely differ by business:

* **The legal category that applies**, pulled from the app's own
  compliance/rules.json with its statutes. An estate agent and a plumber are
  not in the same regulatory position and the pages should not pretend
  otherwise. This is the section no competitor writes at all.
* **The platform floor that actually bites them.** A B2B consultancy runs into
  LinkedIn's 300-per-ad-set minimum immediately; a restaurant never will.
* **The strategy that fits**, and what it costs them.

Where a business has no special legal category, the page says so plainly rather
than inventing a warning to fill the section. A page that manufactures risk to
look thorough is the same failure as one that hides it.
"""

from __future__ import annotations

import html
import json
import pathlib
from typing import Any, Callable, Dict, List

BRAND = "AdPlaybook"


def esc(s: Any) -> str:
    return html.escape(str(s), quote=True)


#: slug, plural noun, the sentence that opens it, compliance keys that apply,
#: the platform that fits with why, the floor that bites, the strategy note.
AUDIENCES = [
    ("plumbers-and-trades", "plumbers and emergency trades",
     "Someone with water coming through a ceiling is not browsing. They search, "
     "they call the first number that looks competent, and the whole decision "
     "takes about ninety seconds.",
     [],
     ("Google", "Emergency work is search-led. Nobody discovers a plumber on "
      "Pinterest at 11pm."),
     None,
     "Local proximity, tightened to the radius you will genuinely drive. A wider "
     "radius buys calls you have to turn down, and you pay for those the same as "
     "the ones you take."),

    ("estate-agents", "estate agents and letting agents",
     "Property advertising is the most heavily regulated thing most small "
     "businesses will ever run, and almost nobody running it knows that.",
     ["housing"],
     ("Meta", "Property is browsed rather than searched, and the imagery does "
      "most of the work."),
     None,
     "Category education early, direct response only on a specific property. The "
     "declaration removes the targeting you would reach for by instinct, so plan "
     "the campaign around what remains rather than discovering it at setup."),

    ("recruiters", "recruiters and hiring teams",
     "A job ad is not a normal ad. Targeting it the way you would target a "
     "product is unlawful, and the platform's category declaration is only part "
     "of complying.",
     ["employment"],
     ("LinkedIn", "It is where the professional facets are, and it is the only "
      "place you can target by seniority and function honestly."),
     ("LinkedIn", 300, "Role-specific targeting stacks land near the 300-member "
      "floor fast, and the floor is per ad set."),
     "Trust and authority. People do not change jobs off a single ad; they change "
     "jobs off having heard of you before a recruiter called."),

    ("brokers-and-lenders", "brokers, lenders and financial advisers",
     "Financial promotion is the one category where getting the copy wrong is a "
     "criminal matter rather than a compliance ticket.",
     ["credit"],
     ("Google", "Intent is explicit and searches are specific. Discovery "
      "advertising for credit is a much harder compliance position."),
     None,
     "Trust and authority, with every claim traceable. This is the category where "
     "an evidence receipt stops being a nice-to-have."),

    ("dentists-and-clinics", "dentists, clinics and private healthcare",
     "Health advertising is judged on whether an ordinary reader could be misled, "
     "not on whether each sentence is technically defensible.",
     ["health"],
     ("Meta", "Local, visual, and the decision is emotional before it is "
      "clinical."),
     None,
     "Problem-aware. People search for the symptom long before they search for the "
     "procedure, and meeting them at the symptom is cheaper."),

    ("gyms-and-subscriptions", "gyms and subscription businesses",
     "The rules that catch subscription businesses are not about the ad. They are "
     "about what happens between the click and the second payment.",
     ["subscription"],
     ("Meta", "Broad reach, visual proof, and a local radius that matches where "
      "people will actually travel."),
     None,
     "Launch and scarcity for intake periods, retention and expansion the rest of "
     "the year. Most gyms run the first one all year and wonder why it decays."),

    ("b2b-saas", "B2B SaaS",
     "The problem is rarely the copy. It is that the audience is small, the cycle "
     "is long, and the platform that can reach the right people charges the most "
     "to do it.",
     [],
     ("LinkedIn", "Job title, function, seniority and company size exist nowhere "
      "else. If a campaign does not use them, it is paying LinkedIn prices for "
      "targeting Meta does cheaper."),
     ("LinkedIn", 300, "A tight ICP plus a two-cell test needs 600 people, not "
      "300, and nothing warns you."),
     "Competitor displacement or problem-aware, depending on whether the category "
     "is understood. Direct response into a six-month cycle measures the wrong "
     "thing and then gets cut for it."),

    ("ecommerce", "ecommerce and DTC brands",
     "You have the one thing most advertisers do not: a conversion that happens "
     "the same day and a number you can check.",
     [],
     ("Meta", "Volume, visual formats and a purchase event that closes the loop "
      "fast enough to learn from."),
     ("Meta", 100, "Lookalikes need at least 100 people from a single country in "
      "the source, which a multi-market list can fail while looking large."),
     "Direct response, with retargeting recovery held to a control group. Without "
     "a holdout you are paying to reach people who were going to buy anyway, and "
     "the report will congratulate you for it."),

    ("restaurants-and-bars", "restaurants, bars and venues",
     "Two constraints most advertisers do not have: your catchment is walking "
     "distance, and if you serve alcohol the copy rules change.",
     ["alcohol"],
     ("Meta", "Local radius, strong imagery, and events that suit a short "
      "scarcity window."),
     None,
     "Local proximity for the everyday, launch and scarcity for events. The "
     "everyday campaign should be boring and always on."),

    ("agencies", "agencies running client campaigns",
     "Your problem is not making the ads. It is proving to a client, months "
     "later, why a claim was made and who approved it.",
     [],
     ("Google", "Whatever the client sells, search is where the reporting is "
      "least ambiguous and the account handover is cleanest."),
     None,
     "Whichever strategy fits the client, chosen explicitly and written down. The "
     "value you add is the argument, not the asset."),
]


def _rules() -> Dict[str, Any]:
    app = pathlib.Path.home() / "ad maker app"
    f = app / "backend" / "adkit" / "compliance" / "rules.json"
    if not f.is_file():
        return {}
    data = json.loads(f.read_text())
    return {c["key"]: c for c in data.get("categories", [])}


def build(page: Callable) -> None:
    rules = _rules()

    cards = "".join(
        f'<a class="card" href="/for/{slug}/"><strong>{esc(noun[0].upper() + noun[1:])}</strong>'
        f'<span>{esc(opener[:88])}…</span></a>'
        for slug, noun, opener, *_ in AUDIENCES)

    page(path="/for/",
         title=f"Advertising by kind of business | {BRAND}",
         description=("What actually changes about running ads depending on what "
                      "you sell: the legal category that applies, the platform "
                      "floor that bites, and the strategy that fits."),
         body=f'<article><p class="crumb">For</p>'
              "<h1>Advertising by kind of business</h1>"
              '<p class="lede">What changes is rarely the copy. It is which legal '
              "category you are in, which platform floor you hit first, and how "
              "long your buyer takes to decide.</p>"
              f'<div class="cards">{cards}</div></article>')

    for slug, noun, opener, cats, (plat, why), floor, strategy in AUDIENCES:
        title_noun = noun[0].upper() + noun[1:]

        if cats:
            blocks = []
            for key in cats:
                c = rules.get(key)
                if not c:
                    continue
                obs = "".join(
                    f"<li><strong>{esc(o.get('what',''))}</strong><br>"
                    f"<span class='muted'>{esc(o.get('why',''))}</span></li>"
                    for o in c.get("obligations", [])[:3])
                blocks.append(f"<h3>{esc(c['name'])}</h3><ul>{obs}</ul>")
            legal = (
                "<h2>The rules that apply to you specifically</h2>"
                "<p>These aren't platform preferences. They're law, and the "
                "platform's category declaration only covers part of it.</p>"
                + "".join(blocks) +
                '<div class="box warn"><p style="margin:0">This is a summary of '
                "why the controls exist, not legal advice. If you're running "
                "these ads, whoever signs them off should be qualified to.</p>"
                "</div>")
        else:
            legal = (
                "<h2>No special ad category applies</h2>"
                "<p>Nothing about this kind of business puts you in a restricted "
                "category, so you keep the full targeting set. That's worth "
                "knowing rather than assuming, because the businesses that do "
                "get caught by one usually don't find out until an ad is "
                "rejected. We don't invent a warning to fill this section.</p>"
                "<p>The ordinary rules still apply: every claim in the ad needs "
                "to be something you can point at on your own site. See "
                "<a href='/learn/what-an-unsubstantiated-claim-costs/'>what an "
                "unsubstantiated claim costs you</a>.</p>")

        if floor:
            fp, fn, fwhy = floor
            floor_html = (
                f"<h2>The number that will stop you first</h2>"
                f'<div class="box"><p style="margin:0"><strong>{esc(fp)}: '
                f"{fn}</strong>. {esc(fwhy)} It produces no error. The campaign "
                "goes live and simply doesn't deliver.</p></div>"
                f'<p>See the <a href="/specs/{fp.lower()}/">{esc(fp)} specs</a> '
                'and <a href="/learn/audience-floors-by-platform/">every '
                "platform's floor</a>.</p>")
        else:
            floor_html = ""

        # Headings are per-audience rather than one shared set. Five of these
        # pages shared an identical H2 skeleton on the first build, which is
        # precisely what a thin-content penalty measures — the pages differ in
        # substance, so they have to differ in shape too.
        heads = {
            "plumbers-and-trades": ("Search, not discovery", "Keep the radius honest",
                                    "What it does with a callout business"),
            "estate-agents": ("Where property actually gets browsed",
                              "Two campaigns, not one", "What it does with a listing"),
            "recruiters": ("Why LinkedIn and not the cheap option",
                           "Nobody moves job off one ad", "What it does with a role"),
            "brokers-and-lenders": ("Explicit intent beats discovery here",
                                    "Every claim has to be traceable",
                                    "What it does when the copy is regulated"),
            "dentists-and-clinics": ("Local, visual, emotional first",
                                     "Meet the symptom, not the procedure",
                                     "What it does with a private clinic"),
            "gyms-and-subscriptions": ("Reach and radius", "Intake season is not the year",
                                       "What it does with a membership"),
            "b2b-saas": ("You are paying for the facets", "Long cycles break direct response",
                         "What it does with a long sales cycle"),
            "ecommerce": ("Volume and a closing loop", "Retargeting needs a holdout",
                          "What it does with a same-day conversion"),
            "restaurants-and-bars": ("Walking distance is the targeting",
                                     "Boring and always on", "What it does with a venue"),
            "agencies": ("Cleanest reporting wins the handover",
                         "The argument is the deliverable",
                         "What it does when a client asks why"),
        }.get(slug, ("Where to run it, and why", "The strategy that fits",
                     f"What {BRAND} does for you"))
        h_where, h_strategy, h_what = heads

        body = f"""
<article>
<p class="crumb"><a href="/for/">For</a> / {esc(noun)}</p>
<h1>Advertising for {esc(noun)}</h1>
<p class="lede">{esc(opener)}</p>

<h2>{h_where}</h2>
<p><strong>{esc(plat)}.</strong> {esc(why)}</p>
<p>That's a starting point rather than a rule. {BRAND} scores all eight
platforms against the strategy you pick and opens on the best fit, so you're
changing a recommendation rather than choosing cold.</p>

<h2>{h_strategy}</h2>
<p>{esc(strategy)}</p>
<p>Every strategy in {BRAND} states how it usually fails before you choose it,
because the expensive mistakes here are strategic rather than typographical.</p>

{legal}
{floor_html}

<h2>{h_what}</h2>
<p>It reads your site, works out what you sell and to whom, recommends the
approach that fits, and writes the campaign. Then it checks the copy against
{esc(plat)}'s published character limits, traces every factual claim back to a
line on your own site, runs the compliance obligations above, and tells you what
it could not check.</p>
<p><a class="btn" href="/#get">Get {BRAND} for Mac</a>
<a class="btn ghost" href="/specs/">See the ad specs</a></p>
</article>
"""
        page(path=f"/for/{slug}/",
             title=f"Advertising for {noun} ({BRAND})",
             description=(f"What changes about running ads for {noun}: the legal "
                          f"category that applies, the {plat} numbers that matter, "
                          "and the strategy that fits."),
             body=body,
             schema={"@context": "https://schema.org", "@type": "TechArticle",
                     "headline": f"Advertising for {title_noun}",
                     "publisher": {"@type": "Organization", "name": BRAND}})
