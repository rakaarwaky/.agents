---
name: data-figures-rerender
description: Faithfully replicate or vectorize data figures (scatter/bar/slope charts) — re-render from the same frozen tables with encodings kept item-by-item; outputs SVG + 600 dpi PNG; full pitfall list.
when-to-use: Use when faithfully replicating or vectorizing data figures (scatter/bar/slope charts) from the same frozen tables with encodings kept item-by-item, producing SVG + 600 dpi PNG and a full pitfall list.
argument-hint: '<源图表路径|冻结数据表路径>'
---

# Data-figure re-rendering from frozen tables

Faithful replication means re-rendering from the same frozen tables with encodings kept item-by-item. Never hand-draw, restyle, or move points.

## Rules

| ID | Rule | Check |
|----|------|-------|
| R1 | **Iron rule: 每一点都是真实实验数据。** 编码即语义；忠实复刻 = 从同一批冻结表（CSV）重新渲染，保持调色板、标记形状、坐标轴、对数刻度、图例与计数标注逐项一致。禁止手画、重新着色或移动点（那是伪造，不是复刻）。合法升级仅三项：SVG 矢量版本、更高 dpi 的 PNG、修复原始图中的客观缺陷（文字溢出、标签与标记碰撞、边缘裁切）。 | 重新渲染的 SVG/PNG 与源图逐项一致；未手工调整任何点；仅包含三项合法升级。 |
| R2 | **定位真实数据。** 论文图脚本常带过期相对路径——用 `find <project-root> -name "<key>.csv"` 找到实际输出/表格目录；写代码前先验证每个 CSV 存在且行数合理。 | 所有 CSV 文件存在且行数合理；脚本使用绝对路径或相对实际目录的路径。 |
| R3 | **逐行移植数据管线。** 逐行复制原脚本的 `load()` / 聚合 / 配对函数；永不更改任何统计量。 | 复制后的 `load()`/聚合/配对函数与原脚本逐行一致；统计量未改变。 |
| R4 | **升级渲染。** `save(fig, name)` 同时输出 SVG（`svg.fonttype="path"`——文字转路径，到处渲染一致）和 PNG（600 dpi）。一个脚本驱动所有图：运行 `python make_figures_svg.py` 重新生成全部图。 | `make_figures_svg.py` 已生成全部 SVG 与 600 dpi PNG；`save()` 使用 `svg.fonttype="path"`。 |
| R5 | **验收。** 对原始 PNG 进行视觉裁判：面板结构、坐标轴、图例、标注完全一致，且点云重合（同一源数据⇒点自然重合，也交叉验证了移植的管线）。 | 独立视觉裁判已核对面板/坐标轴/图例/标注一致性与点云重合；返回 PASS。 |

## Routing

| Step | File | Purpose |
|------|------|---------|
| 1 | `make_figures_svg.py` | 完整可运行模板：全局 rcParams、双格式 `save()`、以及总览框图/点带图/对数-对数散点图/斜率图/分组柱状图/直方图的现成模式。 |
| 2 | `PITFALLS.md` | 十个现场测试过的陷阱：对数轴上的线性文字偏移（600 dpi 下栅格溢出——使用乘法偏移）、FancyBboxPatch 被裁到 axes bbox（anchored-at-edge 框悄悄丢失底边）、多行文字锚点语义、框标题宽度溢出、过期相对数据路径。 |
| 3 | SKILL.md | 本技能概览与验收标准。 |
