---
name: mathmodel-paper-gate
description: >-
  论文写前/写后门禁：PAPER_FACTS.lock、PAPER_OUTLINE、获奖风格卡、国赛六维 SCORECARD、
  init/confirm/check/score 脚本。把写作改成「填槽+打补丁」。Use when writing
  CUMCM/math-modeling papers, before 5writing Pass B, after drafting, or small-revision-only flow.
---

# 论文门禁（lock → outline → 填槽 → scorer）

本 skill **不替代** `5writing` / `mathmodel-cumcm-style` / `6verity`。它强制写前产物与写后打分卡，把「大修」压成「小改」。

## 一键命令（`SKILL_DIR` = 本 skill 目录）

```bash
# 0) 初始化模板到项目 reports/
python "$SKILL_DIR/scripts/init_paper_gate.py" --root . --style-card thematic_research

# 1) 填完 lock/outline 且用户确认后
python "$SKILL_DIR/scripts/confirm_gate.py" --root . --lock --outline --i-confirm

# 2) Pass A：只验冻结状态
python "$SKILL_DIR/scripts/check_paper_gate.py" --root . --pass a

# 3) Pass B 前/后：活跃入口 + 数值（默认只扫 main.typ，忽略 Thematic_/backup）
python "$SKILL_DIR/scripts/check_paper_gate.py" --root . --pass b

# 4) Pass C：含 AI 味定位到 file:line
python "$SKILL_DIR/scripts/check_paper_gate.py" --root . --pass c
python "$SKILL_DIR/scripts/score_paper.py" --root . --write   # 自动填 SCORECARD 检出与≤10补丁
```

可选：`--main paper_v2/main.typ`；查旧稿加 `--all-paper`。

## 强制产物

```text
reports/PAPER_FACTS.lock.md
reports/PAPER_OUTLINE.md
reports/PASS_B_BRIEF.md      # 每节扩写前短卡
reports/SCORECARD.md
```

模板：`templates/`。风格卡：`../_references/award_style_cards/`。

| 题型 | style_card |
|------|------------|
| 国赛分问 | `cumcm_problem_split` |
| 专题/自拟 | `thematic_research` |
| MCM/ICM 英文 | `mcm_english` |

## 流程

### Pass A1/A2

1. `init_paper_gate.py` → 填 lock（含 must_appear / FORBIDDEN / 图槽）与 outline。  
2. Read **一张**风格卡。  
3. **用户确认**后 `confirm_gate.py --i-confirm`。  
4. `check_paper_gate.py --pass a`。

### Pass B（调用 5writing）

1. `check --pass b` 通过。  
2. 每节先改 `PASS_B_BRIEF.md` 的 `current_section`，再扩写。  
3. 数值 ⊆ lock；不改 outline 一级结构；遵守 cumcm-style。

### Pass C

1. `check --pass c` + `score_paper.py --write`。  
2. 只按 SCORECARD ≤10 条打补丁。  
3. 再跑 `6verity`。

## 脚本能力

| 脚本 | 作用 |
|------|------|
| `init_paper_gate.py` | 复制模板 |
| `confirm_gate.py` | 写回 frozen/approved（需 `--i-confirm`） |
| `check_paper_gate.py` | 分 pass 门禁；AI 味报 `文件:行号`；默认跳过 backup 稿 |
| `score_paper.py` | 更新 SCORECARD 自动检出 + 建议补丁表 |
| `gate_lib.py` | 共享解析（勿单独跑） |

Exit ≠ 0 → 不得宣称该 Pass 完成。

## 边界

| Skill | 职责 |
|-------|------|
| 本 skill | lock/outline/风格卡/SCORECARD/脚本 |
| `5writing` | 按大纲填槽 |
| `mathmodel-cumcm-style` | 版式与评分导向 |
| `6verity` | 编译与结构硬验收 |

## 检查清单

- [ ] lock frozen + outline approved（用户确认）
- [ ] 已 Read 对应风格卡
- [ ] `check --pass a/b` 通过后再写/再交
- [ ] 正文数值 ⊆ lock；无 AI 味
- [ ] SCORECARD ≤10 补丁清零后再 `6verity`
