"""Pay-in-4 copy for adplaybook.app. WRITTEN, NOT PUBLISHED.

WHY IT IS OFF. The Buy button points at buy.polar.sh — verified on the live
page, not assumed — and Polar is card-only through Stripe. There is no Klarna,
no Afterpay, no instalment option of any kind behind that link. So every
sentence in this file would be FALSE the moment a visitor clicked, on the page
of a product whose entire pitch is that it refuses claims it cannot trace.

It becomes true when the Buy button moves to Dodo. `check.py` fails the build
if this copy ever reaches a served page while the checkout is still Polar, so
turning it on early is not a thing anyone can do by forgetting.

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
  * Anything implying coverage we do not have. Klarna is US + 19 European
    countries; Afterpay is US and UK only. A UK visitor reading "Klarna" and
    finding Afterpay is a smaller problem than an Australian visitor reading
    either and finding neither.
"""

#: The Buy button's provider. BNPL copy is only true when this is "dodo".
CHECKOUT_PROVIDER = "polar"

#: Flip when the button moves. check.py enforces the pairing.
BNPL_LIVE = False

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
  commercial use, on every site you work on, on up to five machines, with no
  renewal to forget and nothing to cancel.</p>
  <p class="src">Availability depends on where you are and is decided by the
  provider at checkout, not by us. Klarna covers the US and 19 European
  countries; Afterpay covers the US and UK.</p>
</section>
"""
