#!/usr/bin/env python3
"""No page of the built site contains Meta pixel code.

The Meta (Facebook) advertising pixel was removed on 2026-11-06. This check
ensures the removal is complete: no built HTML file may contain the loader URL,
a fbq() call, or the fbevents endpoint. If any does, the build failed to
remove it — or reintroduced it.

This replaced the old check that verified the pixel was dark (empty id) or live
(real id). That check is no longer relevant: the pixel is gone, not toggled.
"""
from __future__ import annotations

import glob
import pathlib
import re
import sys

SITE = pathlib.Path(__file__).resolve().parent.parent

#: Strings that must not appear in any built HTML after the pixel removal.
FORBIDDEN = (
    "fbevents",           # the loader endpoint
    "fbq(",               # any fbq call (init, track, etc.)
    "facebook.com/tr",    # the pixel tracking endpoint
)

#: Files that are exempt because they are build tooling, not served pages.
EXEMPT = frozenset(("_build/", ".git/", "scripts/"))


def _is_exempt(path: pathlib.Path) -> bool:
    rel = str(path.relative_to(SITE))
    return any(rel.startswith(ex) for ex in EXEMPT)


def check_no_pixel(fails: list) -> None:
    """Every built HTML file must be free of Meta pixel code."""
    for path in glob.glob(str(SITE / "**/*.html"), recursive=True):
        html = pathlib.Path(path)
        if _is_exempt(html):
            continue
        text = html.read_text(errors="replace")
        rel = str(html.relative_to(SITE))
        for phrase in FORBIDDEN:
            if phrase in text:
                fails.append(
                    f"{rel} contains {phrase!r}. The Meta pixel was removed "
                    f"on 2026-11-06 and no page may carry it.")


def check_privacy_says_removed(fails: list) -> None:
    """The privacy page must state the pixel was removed, not that it is running."""
    priv = _plain((SITE / "privacy/index.html").read_text(errors="replace"))
    if "removed" not in priv.lower():
        fails.append(
            "the privacy page does not say the Meta pixel was removed. "
            "It must state the removal date.")
    # The old live-state language must be gone.
    for phrase in (
        "that id is now set, and the pixel is running",
        "it reads 1983109892356693",
    ):
        if phrase in priv:
            fails.append(
                f"the privacy page still says {phrase!r}. The pixel is gone; "
                f"the policy must not describe it as active.")


def _plain(html: str) -> str:
    """Tags out, whitespace collapsed."""
    html = re.sub(r"<[^>]+>", " ", html)
    return re.sub(r"\s+", " ", html)


def main() -> None:
    fails: list = []
    check_no_pixel(fails)
    check_privacy_says_removed(fails)
    for f in fails:
        print(f"  FAIL  {f}")
    print(f"\n{len(fails)} failure(s).")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
