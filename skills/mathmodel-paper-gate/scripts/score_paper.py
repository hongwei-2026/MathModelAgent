#!/usr/bin/env python3
"""Generate / refresh SCORECARD auto-findings and suggest ≤10 patches."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from gate_lib import (  # noqa: E402
    collect_paper_files,
    extract_must_appear,
    find_ai_taste_hits,
    find_lock_outline,
    find_reports_dir,
    paper_blob_with_index,
    read_text,
    value_in_paper,
)

SCORECARD_TEMPLATE = """# SCORECARD

```yaml
pass: C
max_patches: 10
paper_entry: paper/main.typ
```

> Scorer **只打分、列补丁**；Patcher 只改「必改清单」。禁止借机重写全文或改 outline 结构。

## 1. 国赛六维估分（总分 100）

| 维度 | 满分 | 得分 | 一句话依据 |
|------|------|------|------------|
| 摘要 | 20 | | |
| 问题分析与模型建立 | 25 | | |
| 模型求解与算法实现 | 20 | | |
| 结果分析、检验与灵敏度 | 15 | | |
| 模型评价、改进与推广 | 10 | | |
| 论文规范、创新 | 10 | | |
| **合计** | **100** | | |

档次：一等 85–100 / 二等 70–84 / 三等 55–69 / 未成功 ＜55

## 2. 自动检出（由 score_paper.py 填充，可手工增补）

<!-- AUTO_FINDINGS_START -->
{findings}
<!-- AUTO_FINDINGS_END -->

## 3. 必改清单（≤10，按优先级）

<!-- AUTO_PATCHES_START -->
{patches}
<!-- AUTO_PATCHES_END -->

## 4. 明确不改（防止范围膨胀）

- 不改 outline 一级标题与页数预算
- 不引入 lock 外新数值

## 5. 补丁完成后

- [ ] 再跑 `check_paper_gate.py`
- [ ] 再跑 `6verity` / `writing_check`
- [ ] 若仍有硬错误，新开一轮 SCORECARD（仍 ≤10 条），禁止推翻大纲
"""


def build_findings(root: Path, main: Path | None, all_paper: bool) -> tuple[list[str], list[str]]:
    findings: list[str] = []
    patches: list[str] = []
    lock_path, outline_path = find_lock_outline(root)
    files = collect_paper_files(root, main, all_paper)
    paper, index = paper_blob_with_index(files) if files else ("", [])

    if not lock_path:
        findings.append("- FAIL: 缺少 PAPER_FACTS.lock.md")
    if not outline_path:
        findings.append("- FAIL: 缺少 PAPER_OUTLINE.md")
    if not files:
        findings.append("- WARN: 未找到活跃论文入口（paper/main.typ 或 paper_v2/main.typ）")

    for hit in find_ai_taste_hits(paper, index):
        findings.append(f"- FAIL: AI味 {hit}")
        if len(patches) < 10:
            loc = hit.split(": /")[0]
            patches.append(
                f"| {len(patches)+1} | `{loc}` | AI味/元话语 | 改成学术表述或删除该段 | cumcm-style 去AI味 |"
            )

    if lock_path:
        for rid, val in extract_must_appear(read_text(lock_path)):
            if files and not value_in_paper(val, paper):
                findings.append(f"- FAIL: lock `{rid}={val}` 未在活跃正文出现")
                if len(patches) < 10:
                    patches.append(
                        f"| {len(patches)+1} | 摘要或结果章 | 缺 lock {rid} | 写入数值 `{val}` | PAPER_FACTS.lock |"
                    )

    if paper and len(re.findall(r"\d+\.\d+", paper)) < 8:
        findings.append("- WARN: 全文小数数值偏少，摘要/结果可能缺量化")

    if not findings:
        findings.append("- OK: 自动项未发现硬问题（仍需人工填六维分）")
    if not patches:
        patches.append("| 1 | | | | |")

    header = "| # | 位置（节/段） | 问题 | 具体改法 | 关联 lock/规范 |\n|---|---------------|------|----------|----------------|"
    patches_md = header + "\n" + "\n".join(patches)
    return findings, [patches_md]


def upsert_region(text: str, start: str, end: str, body: str) -> str:
    block = f"{start}\n{body}\n{end}"
    if start in text and end in text:
        return re.sub(
            re.escape(start) + r".*?" + re.escape(end),
            block,
            text,
            count=1,
            flags=re.S,
        )
    return text


def upsert_scorecard(path: Path, findings_md: str, patches_md: str) -> None:
    marker_fs, marker_fe = "<!-- AUTO_FINDINGS_START -->", "<!-- AUTO_FINDINGS_END -->"
    marker_ps, marker_pe = "<!-- AUTO_PATCHES_START -->", "<!-- AUTO_PATCHES_END -->"
    if path.exists():
        text = read_text(path)
        if marker_fs not in text:
            text = SCORECARD_TEMPLATE.format(findings=findings_md, patches=patches_md)
        else:
            text = upsert_region(text, marker_fs, marker_fe, findings_md)
            if marker_ps in text:
                text = upsert_region(text, marker_ps, marker_pe, patches_md)
            else:
                # inject patches markers after findings
                text = text.replace(
                    marker_fe,
                    marker_fe
                    + "\n\n## 3. 必改清单（≤10，按优先级）\n\n"
                    + marker_ps
                    + "\n"
                    + patches_md
                    + "\n"
                    + marker_pe
                    + "\n",
                )
        path.write_text(text, encoding="utf-8")
        return
    path.write_text(
        SCORECARD_TEMPLATE.format(findings=findings_md, patches=patches_md),
        encoding="utf-8",
    )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=Path("."))
    ap.add_argument("--main", type=Path, default=None)
    ap.add_argument("--all-paper", action="store_true")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()
    root = args.root.resolve()

    findings, patches_list = build_findings(root, args.main, args.all_paper)
    findings_md = "\n".join(findings)
    patches_md = patches_list[0]
    print(findings_md)
    print("\nSuggested patches:\n" + patches_md)

    if args.write:
        reports = find_reports_dir(root) or (root / "reports")
        reports.mkdir(parents=True, exist_ok=True)
        out = reports / "SCORECARD.md"
        upsert_scorecard(out, findings_md, patches_md)
        print(f"\nWrote {out}")

    hard = sum(1 for f in findings if f.startswith("- FAIL"))
    return 1 if hard else 0


if __name__ == "__main__":
    sys.exit(main())
