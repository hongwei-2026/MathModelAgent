---
name: mathmodel-figure-templates
description: >-
  科研绘图模板：复刻/生成期刊感统计图（SHAP蜂群柱状、配对云雨、交叉验证ROC、泰勒图、
  相关矩阵组合、预测真实值边缘分布、TPE 3D曲面、半边小提琴、分组环形热图、城市公园降温组合、
  Nature和弦图）。与 mathmodel-cumcm-style / 3coding-visual / 5writing 配合：模板出风格，
  真实结果替换模拟数据后入论文 figures/。Use when $mathmodel-figure-templates, 科研绘图模板,
  or the figure titles above are requested.
allowed-tools: Bash(*), Read, Write, Edit, Grep, Glob
---

# MathModel Figure Templates（科研绘图模板）

Bundled Python/matplotlib templates for the MathModel Improve tab. Path in sandbox:
`/home/user/.claude/skills/mathmodel-figure-templates`. Local clone: this skill directory.

## 与论文写作 skill 的配合（推荐）

写建模论文时不要孤立用本 skill 堆图，按下面分工：

1. **版式与插图纪律**：先读 `../mathmodel-cumcm-style/SKILL.md` §4.1–4.2  
   （同节少堆图、图题在下、图后解读、摘要禁止插图）
2. **建模流水线数据图**：优先 `../3coding-visual/SKILL.md` 用真实结果画到 `figures/`
3. **需要期刊感复杂图**：本 skill 选最近模板 → 改工作区脚本换**真实数据** → 导出 PDF → 由 `../5writing/SKILL.md` 按章节插入
4. **流程/架构示意图**：交给 `../4drawio/SKILL.md`，不要用本目录统计图模板硬凑

硬约束：捆绑脚本默认是**确定性模拟数据**，仅作版式复刻；写入摘要/正文数值前必须换成任务真实结果，并在 `RESULTS_REPORT.md` 可追溯。

## Fast Path

1. Match the requested chart in `references/figure-catalog.md`.
2. From workspace root, run the renderer with the template id (sandbox path shown; locally use this skill’s `scripts/render_template.py`):

```bash
python3 /home/user/.claude/skills/mathmodel-figure-templates/scripts/render_template.py paired-raincloud
```

3. The renderer copies the bundled template into `绘图复刻/scripts/`, runs it, writes `绘图复刻/outputs/`.
4. Return PNG/PDF/SVG paths and the copied script path.
5. If the figure is for a paper: edit the copied script to load real arrays/CSV, re-run, copy PDF into project `figures/`, then cite under cumcm-style caption rules.

Use `--list` to show supported ids:

```bash
python3 /home/user/.claude/skills/mathmodel-figure-templates/scripts/render_template.py --list
```

## Output Contract

- Work under the current workspace unless the user gives another path.
- Default project folder: `绘图复刻`.
- Script path: `绘图复刻/scripts/make_<template>.py`.
- Outputs: `绘图复刻/outputs/<template>_replica.png`, `.pdf`, `.svg`.
- Prefer bundled scripts first; edit the **copied** workspace script for customization / real data.
- Do not claim simulated values reproduce a source study or contest result.

## Template Ids

- `multiclass-shap-combo`
- `paired-raincloud`
- `cv-roc-ci`
- `taylor-diagram`
- `correlation-pairgrid`
- `prediction-marginal-grid`
- `rf-tpe-surface`
- `grouped-corr-split-violin`
- `grouped-circular-heatmap`
- `urban-park-cooling-combo`
- `nature-chord-diagram`

## When Customizing

Copy/run the nearest template first, then edit `绘图复刻/scripts/`. Preserve:

- `MPLCONFIGDIR` before importing matplotlib.
- seeds when still using simulated demo data; for paper figures, load real data explicitly.
- PNG/PDF/SVG export (paper prefers PDF).
- readable labels, legends, and high-DPI output.
- no in-figure big title (caption belongs in Typst/LaTeX).

Use `references/plot-recipes.md` for implementation patterns.
