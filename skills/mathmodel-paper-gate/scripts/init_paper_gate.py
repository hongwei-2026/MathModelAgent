#!/usr/bin/env python3
"""Bootstrap reports/PAPER_FACTS.lock.md + PAPER_OUTLINE.md from templates."""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=Path("."))
    ap.add_argument("--force", action="store_true", help="Overwrite existing reports")
    ap.add_argument(
        "--style-card",
        default="thematic_research",
        choices=["thematic_research", "cumcm_problem_split", "mcm_english"],
    )
    args = ap.parse_args()
    root = args.root.resolve()
    skill_dir = Path(__file__).resolve().parents[1]
    tpl = skill_dir / "templates"
    reports = root / "reports"
    reports.mkdir(parents=True, exist_ok=True)

    mapping = {
        "PAPER_FACTS.lock.md": tpl / "PAPER_FACTS.lock.md",
        "PAPER_OUTLINE.md": tpl / "PAPER_OUTLINE.md",
        "SCORECARD.md": tpl / "SCORECARD.md",
        "PASS_B_BRIEF.md": tpl / "PASS_B_BRIEF.md",
    }
    for name, src in mapping.items():
        dst = reports / name
        if dst.exists() and not args.force:
            print(f"skip exists: {dst}")
            continue
        if not src.exists():
            print(f"missing template: {src}", file=sys.stderr)
            return 1
        text = src.read_text(encoding="utf-8")
        if name == "PAPER_OUTLINE.md":
            text = text.replace(
                "style_card: thematic_research",
                f"style_card: {args.style_card}",
            )
        dst.write_text(text, encoding="utf-8")
        print(f"wrote {dst}")

    cards = skill_dir.parent / "_references" / "award_style_cards" / f"{args.style_card}.md"
    print(f"Next: fill lock/outline, Read style card:\n  {cards}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
