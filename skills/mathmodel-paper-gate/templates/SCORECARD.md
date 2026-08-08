# SCORECARD

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
（运行 `python skills/mathmodel-paper-gate/scripts/score_paper.py --root . --write` 生成）
<!-- AUTO_FINDINGS_END -->

## 3. 必改清单（≤10，按优先级）

<!-- AUTO_PATCHES_START -->
| # | 位置（节/段） | 问题 | 具体改法 | 关联 lock/规范 |
|---|---------------|------|----------|----------------|
| 1 | | | | |
<!-- AUTO_PATCHES_END -->

## 4. 明确不改（防止范围膨胀）

- 不改 outline 一级标题与页数预算
- 不引入 lock 外新数值

## 5. 补丁完成后

- [ ] 再跑 `check_paper_gate.py`
- [ ] 再跑 `6verity` / `writing_check`
- [ ] 若仍有硬错误，新开一轮 SCORECARD（仍 ≤10 条），禁止推翻大纲
