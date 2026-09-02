#!/usr/bin/env python3
"""The Meta pixel is dark, and the policy describing it is current.

A CHECK THAT ONLY CONFIRMS ZERO PASSES JUST AS HAPPILY WHEN THE LOADER IS
BROKEN. Asserting "no request to facebook.net" against a page whose snippet was
mangled into a syntax error is a green tick for a tracker that would never fire
even with an id. So this asserts BOTH directions: empty id means nothing loads,
and a planted id means it DOES.

Same shape as the licence fail-open rule in the app repo — "could not ask" and
"was told no" must not be collapsed. Here it is "did not load because it is
dark" versus "did not load because it is broken".
"""
from __future__ import annotations

import pathlib
import re
import sys

SITE = pathlib.Path(__file__).resolve().parent.parent


def check_pixel(fails: list) -> None:
    html = (SITE / "index.html").read_text(errors="replace")

    m = re.search(r"var META_PIXEL_ID='([^']*)'", html)
    if not m:
        fails.append(
            "no META_PIXEL_ID in the served HTML. The id must be a top-level "
            "constant in the page, not a build-time injection, because this "
            "check and any human reading the source both need to see it.")
        return
    pixel_id = m.group(1)

    # The guard must be the FIRST statement, so the script injection itself is
    # skipped. "Loaded but uninitialised" still hands Meta the visit.
    if not re.search(r"var META_PIXEL_ID='[^']*';if\(!META_PIXEL_ID\)return;", html):
        fails.append(
            "the `if(!META_PIXEL_ID)return` guard is not the first statement "
            "after the id. Dark has to mean zero requests to facebook.net, not "
            "a loaded tracker with no id.")

    if pixel_id == "":
        # DARK — assert nothing can fire.
        if "connect.facebook.net" not in html:
            fails.append(
                "the pixel snippet is missing entirely. That is not the dark "
                "state, it is an absent feature — and the privacy page "
                "describes a pixel that exists and is switched off.")
        # And prove this check can fail: with an id planted, the same page
        # must be judged live.
        planted = html.replace("var META_PIXEL_ID=''", "var META_PIXEL_ID='123456789012345'")
        if _is_live(planted) is not True:
            fails.append(
                "planting an id into this page does NOT make it read as live, "
                "so the dark assertion proves nothing — it would pass on a "
                "broken loader too.")
        if _is_live(html) is not False:
            fails.append("the shipped page reads as LIVE while the id is empty")
    else:
        if not re.fullmatch(r"\d{15,16}", pixel_id):
            fails.append(
                f"META_PIXEL_ID is {pixel_id!r}, which is neither empty nor a "
                "15-16 digit Meta id. There are two valid states and this is "
                "neither.")
        # Live: the privacy page must not still say the id is empty.
        # Whitespace-normalised, and tags stripped, before matching.
        #
        # This is the single assertion the whole file exists for — a live pixel
        # under a policy that says it is off — and the first version MISSED IT.
        # The sentence renders as "<strong>that id is\ncurrently empty</strong>",
        # so a literal substring never matched, and planting a live id produced
        # a clean pass. Caught only because the spec insists on proving each
        # branch can fail; asserting the dark state alone would have shipped
        # this happily.
        priv = _plain((SITE / "privacy/index.html").read_text(errors="replace"))
        if "that id is currently empty" in priv:
            fails.append(
                "THE PIXEL IS LIVE AND THE PRIVACY PAGE STILL SAYS THE ID IS "
                "EMPTY. That is a false statement about tracking on a page "
                "that sells something. Fix the policy before anything else.")


def _plain(html: str) -> str:
    """Tags out, whitespace collapsed. A claim broken across a line or split by
    a <strong> is the same claim to a reader, and must be the same to a check."""
    html = re.sub(r"<[^>]+>", " ", html)
    return re.sub(r"\s+", " ", html)


def _is_live(html: str) -> bool:
    """Would this page's loader actually run? Read the guard, not the snippet."""
    m = re.search(r"var META_PIXEL_ID='([^']*)';if\(!META_PIXEL_ID\)return;", html)
    if not m:
        return False
    return bool(m.group(1)) and "connect.facebook.net" in html


def check_conversion_events_carry_value(fails: list) -> None:
    """A conversion event without `value` and `currency` cannot produce ROAS.

    Reported across the portfolio as "AdPlaybook fires Purchase bare". Measured
    here: AdPlaybook fires NO Purchase event at all — only PageView — so the
    report does not apply to this repo. There is nowhere for it to fire yet
    either; checkout is hosted by the payment vendor and there is no return
    page.

    This is therefore a guard against a bug that does not exist, which is the
    cheapest moment to write one. When the event is added, Meta needs `value`
    and `currency` to compute return on ad spend. Without them the account
    shows "3 purchases" and no revenue, permanently — and every optimisation
    decision after that is made on missing data. The damage is silent and
    retroactive: the numbers cannot be backfilled once the ads have run.

    `eventID` is required too. It costs nothing now and adding the Conversions
    API later without it means a stretch of double-counted conversions in
    exactly the figures used to judge the ads.
    """
    import glob

    # Events that represent money changing hands. PageView, ViewContent and
    # Lead legitimately carry no value.
    MONETARY = ("Purchase", "Subscribe", "StartTrial", "AddPaymentInfo")

    for path in glob.glob(str(SITE / "**/*.html"), recursive=True):
        html = pathlib.Path(path).read_text(errors="replace")
        for event in MONETARY:
            for m in re.finditer(
                    r"fbq\(\s*['\"]track['\"]\s*,\s*['\"]" + event + r"['\"]([^;]*)",
                    html):
                args = m.group(1)
                rel = pathlib.Path(path).relative_to(SITE)
                if "value" not in args or "currency" not in args:
                    fails.append(
                        f"{rel}: fbq track {event} carries no value/currency. "
                        f"Meta cannot compute ROAS from it — the account will "
                        f"show a purchase count and no revenue, and the figures "
                        f"cannot be backfilled once ads have run.")
                if "eventID" not in args:
                    fails.append(
                        f"{rel}: fbq track {event} has no eventID. Adding the "
                        f"Conversions API later without one double-counts "
                        f"conversions in the numbers used to judge the ads.")


def check_policy_mentions_it(fails: list) -> None:
    priv = _plain((SITE / "privacy/index.html").read_text(errors="replace"))
    if "connect.facebook.net" in (SITE / "index.html").read_text(errors="replace"):
        for phrase in ("Meta (Facebook) advertising pixel", "META_PIXEL_ID"):
            if phrase not in priv:
                fails.append(
                    f"the pixel snippet ships but the privacy page never says "
                    f"{phrase!r}. The policy and the tracker are one change.")
    # The old ABSOLUTE DENIAL must be gone — not the two words.
    #
    # This first read `if "no pixel" in priv`, and flagged the page within a
    # minute of being written. The match was my own new sentence: "find
    # META_PIXEL_ID ... if it is empty, no pixel is running on the page you are
    # reading." That is TRUE, and it is the reassurance the section exists to
    # give.
    #
    # A bare substring does not bind a claim to its subject. What must not
    # survive is the unconditional list — "no tag manager, no pixel, no
    # embedded fonts" — which denies the pixel exists at all. A conditional
    # sentence saying it is not running RIGHT NOW is the opposite of that, and
    # deleting it to satisfy a grep would remove the honest half.
    for denial in ("no tag manager, no pixel", "no pixel, no embedded"):
        if denial in priv:
            fails.append(
                f'the privacy page still carries the unconditional denial '
                f'"{denial}", which says the pixel does not exist rather than '
                f'that it is switched off')


def main() -> None:
    fails: list = []
    check_pixel(fails)
    check_conversion_events_carry_value(fails)
    check_policy_mentions_it(fails)
    for f in fails:
        print(f"  FAIL  {f}")
    print(f"\n{len(fails)} failure(s).")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
