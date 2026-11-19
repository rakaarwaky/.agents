---
name: declarative-engine
description: Grid-based block diagrams, network overview figures and deployment/phase flowcharts via a declarative layout engine — config syntax with real manuscript configs, and a no-download SVG extraction path.
when-to-use: Use when the figure fits a row×column grid: network overview figures, deployment/phase flowcharts, or method framework diagrams that benefit from a declarative layout engine with config syntax and no-download SVG extraction.
argument-hint: '<网格配置内容|目标图主题>'
---

# Declarative layout-engine figures

Use a declarative layout engine for row×column grid figures: network overviews, deployment/phase flowcharts, and method framework diagrams. Write only the config; the engine handles layout, alignment, and routing.

## Rules

| ID | Rule | Check |
|----|------|-------|
| R1 | **配置节点语法。** 节点写为 `name: main text \| sub text @rRowcCol !blue` — 跨度用 `@r1-3c1`（行）、`@r2c3-4`（列）；`nat` = 自然宽度窄节点；同一单元格中两个 `nat` 节点并排。 | 节点声明包含正确的 `@rRowcCol` 跨度；`nat` 节点行为符合描述。 |
| R2 | **列标题、图例、分组、标题。** 列标题 `@head 1: Backbone`；底部图例 `@legend blue: P2 branch, orange: ACR`；虚线阶段组 `@group Training only : dashed … @end`；底部说明 `@caption …`。 | 配置中列标题/图例/分组/说明语法正确且位置符合预期。 |
| R3 | **边与子文本。** 边 `A -> B`，彩色 `A -> B !orange`；子文本支持 `_{sub}` `^{sup}`（可叠加：`z^{T}_{c}`）和 `\n` 强制换行。 | 边声明使用 `->`；子/上标使用 `_{}`/`^{}`；换行使用 `\n`。 |
| R4 | **文本箭头消歧。** 节点文本中类似 `(32→64)` 的文本箭头不会被误判为边（基于位置的消歧）。 | 节点文本中的箭头符号未被当作边；位置消歧机制有效。 |
| R5 | **无下载 SVG 提取：配置编码。** 写配置；base64url 编码进 hash：`engine.html#c=<b64url>`；成功 = `window.__archState.ok === true`。 | 页面加载后 `window.__archState.ok === true`；配置在 URL hash 中正确解码。 |
| R6 | **无下载 SVG 提取：控制台评估。** 在页面控制台求值 `buildSVG(lastScene)` — 返回完整 SVG 字符串（无需浏览器下载处理）。 | `buildSVG(lastScene)` 返回包含完整 SVG 的字符串；已捕获为输出。 |
| R7 | **无下载 SVG 提取：尺寸解析。** 导出的 width/height 是**浮点字符串**——后续正则必须接受 `[\d.]+`。 | 后续解析 width/height 的正则接受 `[\d.]+`；未将浮点字符串误解析为整数。 |
| R8 | **无下载 SVG 提取：PNG 导出。** 通过 `hand-svg-structure` 内联页面管线导出 PNG。 | PNG 已通过内联页面管线导出；未使用 `<img src>` 方式。 |

## Routing

| Step | File | Purpose |
|------|------|---------|
| 1 | `configs/fig4-1.config.txt` | 网络总览配置：列标题 + 图例 + 紧凑窄节点对。 |
| 2 | `configs/fig5-2.config.txt` | 师生蒸馏训练框架配置。 |
| 3 | `configs/fig6-2_convert.config.md` | TensorRT 部署流程配置：两个堆叠虚线阶段帧。 |
| 4 | SKILL.md | 本技能概览：配置语法与无下载 SVG 提取工作流。 |
