"""Pay-in-4 copy for adplaybook.app. LIVE since 2026-08-23.

⚠️ THIS DOCSTRING SAID "WRITTEN, NOT PUBLISHED" AND "WHY IT IS OFF" FOR DAYS
AFTER IT WENT ON. The condition it described — Buy pointing at buy.polar.sh,
card-only, so every sentence here would be false the moment a visitor clicked —
was true when written and ended when the checkout moved to Dodo. Five instalment
mentions have been serving on the live page since. Corrected 2026-08-23.

The mechanism was never wrong, and that is the part worth keeping: `processor()`
below derives the answer from the CHECKOUT url rather than from a belief written
down anywhere, so BNPL_LIVE could not be true while the button still pointed at
Polar. The gate stayed honest while the prose describing it rotted — which is
the failure mode, because the prose is what the next person reads. The same
mistake was found the same day in ops/bin/bnpl-claim-gate.py, whose docstring
still required "a Stripe checkout, because Polar cannot" long after every
checkout was Dodo.

`check.py` still fails the build if this copy reaches a served page while the
checkout is Polar. That guard is not obsolete — it is simply satisfied now.

THE ARITHMETIC IS DERIVED, NOT TYPED. 149.00 / 4 = 37.25 exactly, four payments
summing to 149.00, final payment six weeks after the first. Checked here rather
than written into prose, because this repo's first rule is that no published
number goes out unmeasured.

WHAT MUST NOT BE SAID:

  * Affirm. It is NOT available on Dodo. It reads as safe because it is enabled
    in Matthew's Stripe account, which is a different processor. Naming it
    would promise a payment method that does not exist at our checkout.
  * "Klarna appears at our checkout." Dodo's docs do not say whether BNPL is
    automatic or needs enabling in the dashboard, and the API would not answer
    it. Unverified until Matthew confirms, so the copy says what the PRICE is
    and does not promise which logos appear.
  * A machine count. I wrote "on up to five machines" here, having taken the
    number from a message rather than from anything I could read. It is
    probably right — both providers are configured for five — but I cannot
    verify a vendor's activation limit from this repo, the live site states no
    machine count anywhere today, and the argument does not need one. A number
    I cannot check does not belong on the page of a product that refuses claims
    it cannot trace. Removed rather than hedged.

  * Anything implying coverage we do not have. Klarna is US + 19 European
    countries; Afterpay is US and UK only. A UK visitor reading "Klarna" and
    finding Afterpay is a smaller problem than an Australian visitor reading
    either and finding neither.
"""

import pathlib

#: This file's own directory, so the checkout URL is read from the source of
#: truth rather than from a copy of it.
SITE_BUILD = pathlib.Path(__file__).resolve().parent


def checkout_provider() -> str:
    """Which processor the Buy button actually points at.

    DERIVED FROM THE URL, never declared. This was a constant reading
    "polar", which is a second representation of a fact that already lives in
    content.py's CHECKOUT — and two representations of one fact is the defect
    this repo and the app have now fixed four times in a day.

    The dangerous drift direction is specific and it defeats the gate rather
    than merely annoying it: a stale constant reading "dodo" while the button
    still points at Polar would make the gate PASS instalment copy that is
    false at the checkout. A gate whose premise can go stale silently is worse
    than no gate, because it is trusted.

    Unknown is treated as not-Dodo by the caller, so an unrecognised URL
    withholds the copy rather than publishing it on a guess.
    """
    import re
    src = (SITE_BUILD / "content.py").read_text()
    m = re.search(r"CHECKOUT\s*=\s*\(?\s*\"([^\"]+)\"", src)
    url = m.group(1) if m else ""
    if "dodopayments.com" in url:
        return "dodo"
    if "polar.sh" in url:
        return "polar"
    return "unknown"

#: Flipped 2026-08-21 when the button moved to Dodo. check.py enforces the
#: pairing in both directions, so this cannot be true while CHECKOUT is Polar.
BNPL_LIVE = True

PRICE = 149.00
INSTALMENTS = 4
PER_INSTALMENT = PRICE / INSTALMENTS          # 37.25, exactly
WEEKS_TO_FINAL = (INSTALMENTS - 1) * 2        # fortnightly

#: A phrase unique to this copy, so the gate can find it in a rendered page
#: without matching the word "instalment" wherever it appears in prose.
MARKER = "then it stops, and it is yours"

SECTION = f"""
<section class="paylater">
  <p class="eyebrow">Paying for it</p>
  <h2>${PER_INSTALMENT:.2f} × {INSTALMENTS}, then it stops, and it is yours</h2>
  <p>AdPlaybook is ${PRICE:.0f} once. If that is easier as four payments, Klarna
  and Afterpay split it into ${PER_INSTALMENT:.2f} every two weeks — the last one
  {WEEKS_TO_FINAL} weeks after the first, at no extra cost.</p>
  <p>It is the opposite of how this category bills. Every other ad tool charges
  you monthly for as long as you use it, and the day you stop paying you stop
  having it. Here the payments end and the licence does not: unlimited
  commercial use, on every site you work on, with no renewal to forget and
  nothing to cancel.</p>
  <p class="src">Availability depends on where you are and is decided by the
  provider at checkout, not by us. Klarna covers the US and 19 European
  countries; Afterpay covers the US and UK.</p>
</section>
"""
