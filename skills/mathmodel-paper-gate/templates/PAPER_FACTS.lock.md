# PAPER_FACTS.lock

```yaml
status: draft   # draft | frozen
confirmed_by_user: false
source_reports:
  - reports/RESULTS_REPORT.md
protocol: ""    # e.g. N=1500, 40 epochs, seeds 0/1/2
```

> **规则**：正文关键数值与结论只能来自本文件。`status` 非 `frozen` 或 `confirmed_by_user` 非 true 时，禁止扩写论文正文（Pass B）。

## 1. 协议（写进摘要/方法的硬事实）

- 数据：
- 划分：
- 训练：
- 种子：
- 软硬件：

## 2. 主结果表（必须可追溯到 CSV/报告）

| id | metric | model | value | std_or_ci | source_file | must_appear |
|----|--------|-------|-------|-----------|-------------|-------------|
| M1 | Energy MAE | mlp | | | | yes |
| M2 | Energy MAE | gnn | | | | yes |
| M3 | Energy MAE | vae | | | | yes |
| M4 | Energy MAE | qvae | | | | yes |
| M5 | Energy R² | … | | | | yes |

在 `must_appear: yes` 的行中，`value`（及需要时的 ±std）必须在摘要或结果章出现至少一次。

## 3. 可说结论（ALLOWED）

- （例）在相同协议下，GNN 的 Energy MAE 低于 MLP。
-

## 4. 不可说结论（FORBIDDEN）

- （例）不得声称 QVAE 在 IID Energy MAE 上最优，除非表中确实如此。
-

## 5. 图表槽

| fig_id | path | caption_zh | section | notes |
|--------|------|------------|---------|-------|
| F1 | figures/xxx.pdf | | 五、… | |

## 6. 参考文献（已核实）

| n | citation_short | verified |
|---|----------------|----------|
| 1 | | yes/no |

## 7. 冻结签字

- [ ] 数字已与 CSV/报告逐项核对
- [ ] FORBIDDEN 列表完整
- [ ] 用户已口头/书面确认 → 将上文 `status` 改为 `frozen`，`confirmed_by_user: true`
