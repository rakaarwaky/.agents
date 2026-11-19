---
name: hand-svg-structure
description: Replicate a bitmap/screenshot structure diagram (block diagram, flowchart, network, schematic) as a hand-authored static SVG — programmatic geometry/color probing, live-page export, full pitfall list.
when-to-use: Use when replicating a bitmap/screenshot structure diagram (block diagram, flowchart, network, schematic) as a hand-authored static SVG with programmatic geometry/color probing, live-page export, and a full pitfall list.
argument-hint: '<参考位图路径|图表描述>'
---

# Hand-authored SVG structure-figure replication

Replicate a bitmap/screenshot structure diagram as a hand-authored static SVG using programmatic geometry/color probing, live-page export, and full pitfall list. Do not use this route for data plots.

## When to use

The reference is a **bitmap** (paper screenshot, scan, slide export) showing a *structure* figure — block diagram / flowchart / network / schematic — and you need an editable, print-quality vector replica. Do **not** use this route for data plots (see `data-figures-rerender`).

## Rules

| ID | Rule | Check |
|----|------|-------|
| R1 | **探测，不要目测。** 使用 `probe_geometry.py`（本文件夹）从参考位图提取精确像素值：通过填充色连通分量提取框边界，通过环形扫描提取圆心/直径，文本行基线，连接器端点，虚线/填充/边框颜色。在参考的坐标系中构建第一稿——零猜测地落地约 80% 正确。 | 已使用 `probe_geometry.py` 提取精确像素值；第一稿在参考坐标系中构建；约 80% 正确。 |
| R2 | **逐字复制文本。** 每个字符串与参考核对。上标/下标通过 `tspan dy`（数学字母使用斜体衬线；**正体数字下标需要显式 `font-style="normal"`**——tspan 继承斜体）。 | 每个字符串与参考逐字核对；上标/下标使用 `tspan dy`；正体数字下标显式设置 `font-style="normal"`。 |
| R3 | **手写 SVG。** 样式集中在 `<style>` 块 + 语义颜色常量（见 repo-root `METHOD.md`）；每个区域有结构注释；默认墨色继承自包裹的 `<g fill="...">`。 | SVG 样式集中在 `<style>` 块 + 语义颜色常量；每区域有结构注释；默认墨色继承自 `<g fill>`。 |
| R4 | **导出 PNG。** `prepare_export_pages.py` 构建内联 HTML 页面 → 将浏览器视口设置为*精确*内容尺寸 → 普通截图（**绝不用 fullPage**——它触发平铺 bug）；对于高于约 2160px 的内容，捕获顶部/底部半幅并用 PIL 拼接。 | 已使用 `prepare_export_pages.py` 构建内联 HTML 页面；视口设置为精确内容尺寸；普通截图（无 fullPage）；高于 2160px 时顶部/底部拼接。 |
| R5 | **验收。** 活页面截图 + 独立视觉模型裁判比较复制品 vs 参考（标准：每个字符串、箭头源→目标拓扑、无溢出/重叠；有意的样式升级不是缺陷）。在 FAIL 时，使用裁判的像素证据修复根本原因。 | 已完成活页面截图与独立视觉裁判比较；FAIL 时已使用像素证据修复根本原因；返回 PASS。 |
| R6 | **陷阱：`<style>` 覆盖表示属性。** SVG `<style>` 覆盖表示属性：`text{fill:…}` 在元素上胜过 `fill=""` → 彩色标题渲染为近黑色。将 `fill` 移出 CSS；从包裹的 `<g fill>` 继承默认值并逐元素设置颜色。 | `fill` 不在 CSS 中；颜色从包裹的 `<g fill>` 继承或逐元素设置；彩色标题未渲染为近黑色。 |
| R7 | **陷阱：永远不要通过 `<img src="*.svg">` 导出。** 渲染错误（斜体泄漏、级联异常）；独立 SVG 文档截图为缩放块。内联 HTML 是唯一可靠通道。 | SVG 通过内联 HTML 导出；未使用 `<img src="*.svg">` 或独立 SVG 文档截图。 |
| R8 | **陷阱：全连接网络图的签名风格。** 进入边在目标圆的**左极**收敛，箭头以簇状堆叠——径向边缘分布读起来"错误"。 | 进入边在目标圆的左极收敛；箭头以簇状堆叠。 |
| R9 | **陷阱：在结构-语义层面判断"相似性"。** 参考是语义目标，而非像素模板。 | 已在结构-语义层面判断相似性；参考被当作语义目标而非像素模板。 |

## Routing

| Step | File | Purpose |
|------|------|---------|
| 1 | `probe_geometry.py` | 从参考位图提取精确像素值：框边界、圆心/直径、文本行基线、连接器端点、虚线/填充/边框颜色。 |
| 2 | `prepare_export_pages.py` | 构建内联 HTML 页面用于普通截图导出（精确尺寸视口、无 fullPage）。 |
| 3 | `examples/fig-prefix-classifier` | 两节流水线图（蓝色/橙色虚线组、反馈环），从位图在参考坐标系中复刻（`ecg_reference.png` 是源位图）。 |
| 4 | `examples/fig1-1_roadmap` | 四阶段研究路线图，从 matplotlib 源脚本重绘（坐标 1:1 映射）。 |
| 5 | SKILL.md | 本技能概览与工作流。 |
