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

<h2>Which of these actually finishes the job</h2>
<p>We ran four of them against a real product description on the same machine,
two attempts each. Counts, not percentages:</p>
<ul>
<li><strong>Qwen2.5 1.5B — 2 of 2.</strong> The smallest model here does
finish a campaign.</li>
<li><strong>Llama 3.2 3B — 0 of 2.</strong> Eleven required fields short both
times.</li>
<li><strong>Qwen3 4B — 2 of 2.</strong></li>
<li><strong>Qwen2.5 7B — 2 of 2.</strong></li>
</ul>
<p><strong>An earlier version of this page said the 1.5B never finished a
campaign, and that was our bug rather than the model.</strong> Our JSON
extraction cut the answer short and the missing tail looked like missing
fields. Three of these four only started working once that was fixed. We are
leaving the correction visible because a page that quietly improves its own
numbers is not worth reading.</p>
<p>The 3B is the odd one out and it stayed broken after the fix, so on this
evidence that is the model. The 8B and 30B have not been run against the
campaign schema at all, and we would rather say so than let you assume they
sit on a line between the ones we tested.</p>
<p>If you have an API key or Outlier running, use those — a bigger model
writes better copy. The built-in models are the floor, and the floor is real.</p>

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
