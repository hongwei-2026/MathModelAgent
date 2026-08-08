# PAPER_OUTLINE

```yaml
status: draft   # draft | approved
confirmed_by_user: false
style_card: thematic_research   # cumcm_problem_split | thematic_research
engine: typst                   # typst | latex
has_toc: false
abstract_style: thematic        # problem_split | thematic
target_body_pages: 22           # 不含附录；国赛电子版 ≤30
```

> **规则**：`status` 非 `approved` 时禁止 Pass B。Pass B **不得**增删一级章节；只许按要点扩写。

## 0. 摘要要点（独占一页）

必须写入的数字（引用 lock id，如 M1–M4）：

- 
- 

段落骨架（3–5 段）：

1. 背景与问题（无公式）
2. 数据与协议
3. 方法链条
4. 主结果数值
5. 局限与贡献边界

关键词（3–5）：

## 1. 目录（若 has_toc）

- 深度到二级；总长约 1–2 页

## 2. 正文章节预算

| section | title | pages | bullets (5–8) | tables | figures | lock_ids |
|---------|-------|-------|---------------|--------|---------|----------|
| 一 | | 2 | 1) … | | | |
| 二 | | 2 | | | | |
| 三 | | 1 | | | | |
| 四 | | 1 | | | | |
| 五 | | 6 | | | | |
| 六 | | 5 | | | | |
| 七 | | 2 | | | | |
| 八 | | 2 | | | | |

## 3. 灵敏度 / 稳健性（评分必查）

- 扰动什么：
- 看什么指标：
- 预期表/图：

## 4. 不写进正文的内容

- 大段源码、内部路径、改稿元话语、看板/CSV 为准等

## 5. 结构批准签字

- [ ] 页数预算之和 ≈ target_body_pages
- [ ] 每节有表或图或推导之一作为证据
- [ ] 用户已确认 → `status: approved`，`confirmed_by_user: true`
