#!/usr/bin/env python3
"""Every gate must be unable to report a false clean. This checks that, by running them.

WHY THIS EXISTS, and why it is late. Four gates in this repo already carry a
minimum-scope guard, and `source_freshness_gate.py` line 27 has said

    python3 scripts/source_freshness_gate.py <root>       # aim it (meta_gate needs this)

since it was written. The gates were built to be aimed *for* a meta_gate that was
never ported over from outlier-site. A recommendation written down and never done
is a live gap, not a note: nothing was proving those four guards still worked, and
nothing would enrol a fifth gate written tomorrow. This file closes that.

WHAT IS CHECKED. Pointed at an empty tree, a gate must exit non-zero. A gate that
reports clean having examined nothing is worse than no gate, because it is read as
evidence.

THE SUBTLETY THAT IS THE WHOLE POINT. Pointing a gate at an empty tree only proves
something if the gate LOOKS at the tree you pointed it at. In outlier-site this was
found the hard way: deploy_freshness_gate "passed" the empty-tree probe because it
ignored argv and re-checked the real repo. The probe was vacuous for exactly the
reason the probe exists to catch. So reachability is established FIRST, and a gate
that cannot be pointed anywhere is exempted explicitly, with a reason, never
skipped in silence.

HOW REACHABILITY IS ESTABLISHED — behaviour, not a substring. outlier-site's
meta_gate tries `"argv[1]" in src` first and only then runs the gate. That shortcut
has a hole in each direction: it passes a gate that merely MENTIONS argv[1] in a
comment, and it fails every gate here, because all four spell the root as
`sys.argv[1:]` filtered for flags. So there is no substring test in this file.

Instead, two probes, cheapest first:

  1. Two DIFFERENT empty directories. A gate that is aimed prints the root it was
     handed, so its two outputs differ; it can only have learned that path from
     argv. A gate that ignores argv scans the same tree twice and says the same
     thing. This is hermetic and costs nothing -- and it is what settles
     source_freshness_gate, whose real-repo run makes 12 live HTTP fetches.
  2. Only if (1) is inconclusive: empty tree vs the real repo. Authoritative, but
     it runs the gate for real, so it is the fallback and not the default.
     Inconclusive is not a verdict -- a gate is condemned only by (2).

  Today (1) settles three of four and (2) is needed only by
  engine_site_limits_gate, which prints no path and whose real run is local and
  instantaneous. That ordering is the design, not a coincidence.

  KNOWN LIMIT of (2): it reads a difference between an empty tree and the repo as
  proof of aiming, so it will call a genuinely-aimed gate "unaimed" if the repo
  ALSO holds nothing that gate can see. That is a false FAIL, not a false clean --
  the safe direction -- but if you ever see one, check whether the content left
  before you go editing the gate.

AND: a gate that ADVERTISES `--self-check` must pass it. Checking a claim the file
makes about itself, not imposing a new requirement on gates that make no claim.

    python3 scripts/meta_gate.py
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

#: Gates that legitimately cannot take a root, with the reason and the guard that
#: substitutes for this check. Anything here is asserted, not trusted. Empty is the
#: correct state: every gate in this repo is aimable today.
EXEMPT: dict[str, tuple[str, str]] = {}

#: If the scan finds fewer than this, assume it broke rather than that the gates left.
MIN_GATES = 4


def says(script: Path, root: str) -> tuple[int, str]:
    """Exit code and stdout when the gate is aimed at `root`."""
    try:
        r = subprocess.run([sys.executable, str(script), root],
                           capture_output=True, text=True, timeout=300)
        return r.returncode, r.stdout
    except subprocess.TimeoutExpired:
        return -1, "<timeout>"


def proves_it_is_aimed(script: Path, empty_a: str, empty_b: str, repo: str) -> bool:
    """Cheap hermetic probe first; the real-repo comparison only if it is unclear."""
    if says(script, empty_a)[1] != says(script, empty_b)[1]:
        return True
    return says(script, empty_a)[1] != says(script, repo)[1]


def self_check_holds(script: Path) -> str | None:
    """If the file advertises --self-check, it must pass. Returns a complaint or None."""
    if "--self-check" not in script.read_text(encoding="utf-8", errors="ignore"):
        return None
    try:
        r = subprocess.run([sys.executable, str(script), "--self-check"],
                           capture_output=True, text=True, timeout=300)
    except subprocess.TimeoutExpired:
        return "advertises --self-check, which TIMED OUT"
    if r.returncode != 0:
        return f"advertises --self-check, which FAILS (exit {r.returncode})"
    return None


def main(repo: str = ".") -> int:
    root = Path(repo)
    gates = sorted((root / "scripts").glob("*_gate.py"))
    gates = [g for g in gates if g.name != "meta_gate.py"]
    print(f"gates found: {len(gates)}")
    if len(gates) < MIN_GATES:
        print(f"\nFAIL: only {len(gates)} gate(s) found, expected >= {MIN_GATES}.")
        print("      The scan is likelier broken than the repo. Not reporting clean.")
        return 1

    fails: list[str] = []
    with tempfile.TemporaryDirectory() as empty_a, tempfile.TemporaryDirectory() as empty_b:
        for g in gates:
            if g.name in EXEMPT:
                reason, needle = EXEMPT[g.name]
                if needle not in g.read_text(encoding="utf-8", errors="ignore"):
                    fails.append(f"{g.name}: exempt on the grounds of {needle}, which is NOT in the file")
                else:
                    print(f"  [exempt] {g.name:<26} {reason}")
                continue

            if not proves_it_is_aimed(g, empty_a, empty_b, repo):
                fails.append(
                    f"{g.name}: ignores its root argument, so it cannot be pointed at a "
                    f"test tree. An empty-input probe against it proves nothing — take a "
                    f"root, or add an entry to EXEMPT explaining why it cannot.")
                continue

            rc = says(g, empty_a)[0]
            if rc == 0:
                fails.append(
                    f"{g.name}: EXITS 0 ON AN EMPTY TREE. It reports clean having examined "
                    f"nothing. Add a minimum-scope guard that fails when the scan finds "
                    f"less than it should.")
                continue

            complaint = self_check_holds(g)
            if complaint:
                fails.append(f"{g.name}: {complaint}")
                continue

            print(f"  [ok]     {g.name:<26} fails correctly on an empty tree (exit {rc})")

    if fails:
        print(f"\nFAIL ({len(fails)}):")
        for f in fails:
            print(f"  {f}")
        return 1
    print(f"\nPASS — all {len(gates)} gates refuse to report clean on nothing.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else "."))
