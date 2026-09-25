"""/check/ — the free ad copy limit checker, built on the same data as /specs/.

WHY THIS PAGE EXISTS. The searches this site already draws are limit questions
("bing ad character limit", "linkedin headline length"), and the answer a
searcher actually wants is not a table but "does MY copy fit". Every other
checker online hard-codes its own numbers and dates none of them. This one is
rendered from the app's own platform files (`backend/adkit/platforms/*.json`),
the same files the /specs/ pages and the app itself read, so the checker, the
spec pages and the product cannot disagree about a limit.

NOTHING IS SENT ANYWHERE. The counting is a few lines of JavaScript on the page;
the limits are embedded in it at build time. That is also why it works offline
once the page has loaded.

WHAT IT COUNTS. Characters as typed (Unicode code points). Two platform rules
are stated rather than modelled: X counts every link as 23 characters, and
Google counts some wide characters (Chinese, Japanese, Korean) as two. Modelling
them properly means knowing what is a link and which script a character is in,
and a checker that is confidently wrong is worse than one that says what it
does not do.

GOOGLE'S "PRIMARY TEXT". google.json carries primary_text_chars for the
responsive search ad, which is the description limit under the field name the
app uses for every platform. A search ad has no primary text, so the checker
does not show one for Google; its description row carries the 90.
"""
from __future__ import annotations

import json
from typing import Any, Callable, Dict, List

FIELDS = (("headline", "Headline"), ("primary_text", "Body text"),
          ("description", "Description"))


def _limits(specs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """The checker's data: every placement's counted fields, nothing else."""
    out = []
    for s in specs:
        key = s["key"]
        rows = []
        for p in s.get("placements", []):
            fields = {}
            for stem, _label in FIELDS:
                if key == "google" and stem == "primary_text":
                    continue
                work, hard = p.get(f"{stem}_chars"), p.get(f"{stem}_max_chars")
                if not work and not hard:
                    continue
                fields[stem] = {"work": work or hard, "hard": hard}
            if fields:
                rows.append({"name": p.get("name", p["key"]), "fields": fields,
                             "read": p.get("verified_on") or ""})
        if rows:
            out.append({"key": key, "name": s["name"], "rows": rows,
                        # Google's single numbers are refusals; elsewhere a single
                        # number is the platform's stated limit, and the page says
                        # only that.
                        "single_is_hard": key == "google",
                        "x_link": key == "x"})
    return out


SCRIPT = r"""
<script>
(function () {
  var data = JSON.parse(document.getElementById('lim-data').textContent);
  var boxes = {headline: document.getElementById('in-headline'),
               primary_text: document.getElementById('in-body'),
               description: document.getElementById('in-desc')};
  var out = document.getElementById('lim-out');
  var LABEL = {headline: 'Headline', primary_text: 'Body text', description: 'Description'};
  function len(s) { return Array.from(s || '').length; }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) {
    return {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c]; }); }
  function verdict(n, f, plat) {
    if (!n) return ['', ''];
    if (f.hard && n > f.hard) return ['bad', 'Over the ' + f.hard + ' cap: refused at upload'];
    if (!f.hard && plat.single_is_hard && n > f.work) return ['bad', 'Over the ' + f.work + ' limit: refused at upload'];
    if (n > f.work) {
      if (plat.x_link) return ['warn', 'Fits only with no link: a link takes 23 of the 280'];
      if (f.hard) return ['warn', 'Accepted, but cut off after ' + f.work];
      return ['warn', 'Over the stated ' + f.work];
    }
    return ['ok', 'Fits'];
  }
  function draw() {
    var counts = {};
    Object.keys(boxes).forEach(function (k) {
      counts[k] = len(boxes[k].value);
      var c = document.getElementById('cnt-' + k);
      if (c) c.textContent = counts[k] + ' characters';
    });
    var any = counts.headline || counts.primary_text || counts.description;
    if (!any) { out.innerHTML = '<p class="note">Type or paste copy above and every placement below is checked as you go.</p>'; return; }
    var html = '';
    data.forEach(function (plat) {
      html += '<h3><a href="/specs/' + plat.key + '/">' + esc(plat.name) + '</a></h3>';
      html += '<div class="tbl-wrap"><table><thead><tr><th>Placement</th><th>Field</th><th>Yours</th><th>Limit</th><th>Result</th></tr></thead><tbody>';
      plat.rows.forEach(function (row) {
        Object.keys(row.fields).forEach(function (k) {
          var f = row.fields[k], n = counts[k];
          if (!n) return;
          var v = verdict(n, f, plat);
          var lim = f.hard && f.hard !== f.work ? f.work + ' / ' + f.hard : String(f.work);
          html += '<tr><td>' + esc(row.name) + '</td><td>' + LABEL[k] + '</td><td>' + n +
                  '</td><td>' + lim + '</td><td class="lim-' + v[0] + '">' + v[1] + '</td></tr>';
        });
      });
      html += '</tbody></table></div>';
    });
    out.innerHTML = html;
  }
  Object.keys(boxes).forEach(function (k) { boxes[k].addEventListener('input', draw); });
  draw();
})();
</script>
"""


def build(page: Callable, specs: List[Dict[str, Any]]) -> None:
    data = _limits(specs)
    dates = sorted({r["read"] for p in data for r in p["rows"] if r["read"]})
    read = (f"between {dates[0]} and {dates[-1]}" if len(dates) > 1 else
            f"on {dates[0]}" if dates else "on the dates their pages show")
    names = ", ".join(p["name"] for p in data[:-1]) + " and " + data[-1]["name"]
    body = f"""
<article>
<p class="crumb"><a href="/specs/">Ad specs</a> / Checker</p>
<h1>Ad copy character limit checker</h1>
<p class="lede">Paste a headline, body text or description and see it counted
against every placement's published limit on {len(data)} platforms at once:
{names}. It runs in your browser; nothing you type is sent anywhere.</p>

<div class="box">
<label class="lim-in"><strong>Headline</strong> <span id="cnt-headline" class="note"></span>
<textarea id="in-headline" rows="2" spellcheck="true"></textarea></label>
<label class="lim-in"><strong>Body text</strong> (primary text, post copy) <span id="cnt-primary_text" class="note"></span>
<textarea id="in-body" rows="5" spellcheck="true"></textarea></label>
<label class="lim-in"><strong>Description</strong> <span id="cnt-description" class="note"></span>
<textarea id="in-desc" rows="3" spellcheck="true"></textarea></label>
</div>

<div id="lim-out" aria-live="polite"></div>

<h2>How does the checker count?</h2>
<p>Characters as you typed them, the way most platforms count. Two rules are
stated here rather than modelled: X counts every link as 23 characters however
long it is, and Google counts some wide characters, such as Chinese, Japanese
and Korean, as two. Where a platform gives two numbers, the first is where the
copy is cut off or, on X, what fits beside a link, and the second is the hard
cap that refuses the upload.</p>
<p>The limits come from each platform's own documentation, read {read}, the
same files the <a href="/specs/">ad specs pages</a> and the app itself use.
Each platform's heading links to its page, with the source and the date for
every number.</p>
</article>
<script type="application/json" id="lim-data">{json.dumps(data, separators=(",", ":"))}</script>
{SCRIPT}
"""
    # Counted from the data, not typed: TikTok's placements carry no text limit
    # the app has verified, so it is not in the checker, and a title saying
    # "8 platforms" would be the kind of number this site does not print.
    page(path="/check/",
         title=f"Ad copy character limit checker, {len(data)} platforms | AdPlaybook",
         description=(f"Paste ad copy and check it against every placement's published "
                      f"character limit on {len(data)} ad platforms at once. Free, and "
                      "nothing leaves your browser."),
         body=body)
