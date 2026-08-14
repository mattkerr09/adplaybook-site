"""The page for the thing that runs with no account, no key and no network.

Shipped in 0.2.23 and had no page at all, which is the largest gap on the
site: it is the only claim here that most competitors cannot make, and someone
searching for an ad tool that does not want an API key was finding nothing.

Every figure is read from the app's own catalogue at build time — the same
file the picker reads, written by scripts/refresh_local_models.py from the
Hugging Face API. A download size a person waits on is not a place to guess,
and a page that quotes one from memory goes stale the first time a model is
requantised.

WHAT THIS PAGE REFUSES TO SAY
-----------------------------
That the built-in models are as good as the cloud ones. Nobody has measured
that — no model in the catalogue has been run against the corpus and judged —
and the one honest data point available is unflattering and is printed anyway:
the smallest model produced one ad variant where three were asked for.

That is the sentence a reader needs in order to choose, and leaving it out to
make the feature sound better would be the exact failure this product exists
to avoid.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable, Dict

BRAND = "AdPlaybook"


def _esc(s: Any) -> str:
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def _catalogue(app_repo: Path) -> Dict[str, Any]:
    p = app_repo / "backend" / "adkit" / "models_local" / "catalogue.json"
    try:
        return json.loads(p.read_text())
    except (OSError, ValueError):
        return {}


def build(page: Callable, app_repo: Path) -> None:
    cat = _catalogue(app_repo)
    models = cat.get("models") or []
    if not models:
        return

    rows = "".join(
        f"<tr><td>{_esc(m['name'])}</td><td>{m['download_gb']} GB</td>"
        f"<td>{m['min_ram_gb']} GB</td></tr>"
        for m in models)

    smallest = min(models, key=lambda m: m["download_bytes"])
    largest = max(models, key=lambda m: m["download_bytes"])

    body = f"""
<article>
<p class="crumb">Offline</p>
<h1>Write ad campaigns with no account, no API key and no network</h1>
<p class="lede">{BRAND} can download a language model and run it on your Mac.
Nothing about your product is sent anywhere, there is no per-use cost, and it
keeps working on a train.</p>

<h2>How it works</h2>
<p>Pick a model on the first screen and it downloads once, into your own
Application Support folder. After that the app generates campaigns using your
Mac's GPU. The cloud providers and Outlier stay exactly where they were — this
is one more option, not a replacement, and the app will not quietly switch
between them.</p>

<h2>Which model your Mac can run</h2>
<p>Unified memory decides it. The app reads how much this machine has and says
which models fit, including the ones that do not and why.</p>
<table>
<thead><tr><th>Model</th><th>Download</th><th>Memory needed</th></tr></thead>
<tbody>{rows}</tbody>
</table>
<p class="muted">{_esc(cat.get('_ram_rule', ''))}</p>
<p class="muted">Download sizes read from the Hugging Face API on
{_esc(cat.get('_verified_on', ''))}, not estimated.</p>

<h2>What it costs you in quality</h2>
<p>This is the part most pages leave out. None of these models has been run
across our test corpus and judged, so we will not tell you they match a
frontier model — we have not measured it and neither has anyone else for this
particular job.</p>
<p>The measurements we have are unflattering, and they got worse rather than
better. Running the smallest model, {_esc(smallest['name'])}:</p>
<ul>
<li>Two early attempts produced a complete campaign document, one of them with
<strong>a single ad variant where three were asked for</strong> — a usable
draft, not a usable test.</li>
<li><strong>Four later attempts produced nothing usable at all.</strong> The
campaign schema has since gained three required fields, and this model now
runs out of retries without filling them.</li>
</ul>
<p>That is two of six attempts, and none of the four most recent. We are
publishing it because it is what we measured, and because a page that quoted
only the first success would be selling you a download that fails on your
machine. The larger models in the table have more room; how much more, we have
not measured yet, and we will not guess.</p>
<p>If you have an API key or Outlier running, use those. The built-in model is
a floor, and on this evidence the smallest one is currently below it.</p>

<h2>What it will not do</h2>
<ul>
<li><strong>Run on an Intel Mac.</strong> {_esc(cat.get('_requires', ''))}</li>
<li><strong>Ship the weights inside the installer.</strong> The app itself is
a 127 MB download. Bundling even the largest model in the table would add
{largest['download_gb']}GB to that for everyone, including the people who will
never use it, so the weights come down only when you pick one.</li>
<li><strong>Check for updates on its own.</strong> Nothing here contacts
anything unless you press something.</li>
</ul>
</article>
"""
    desc = ("Run AdPlaybook's ad campaign generation entirely on your Mac — no "
            f"account, no API key, no network. {len(models)} models from "
            f"{smallest['download_gb']}GB to {largest['download_gb']}GB, "
            "picked by how much memory you have.")
    page(path="/offline/",
         title=f"Offline ad copy generation on a Mac — no API key | {BRAND}",
         description=desc,
         body=body,
         schema={"@context": "https://schema.org", "@type": "TechArticle",
                 "headline": "Offline ad generation with a built-in model",
                 "description": desc,
                 "publisher": {"@type": "Organization", "name": BRAND}})
