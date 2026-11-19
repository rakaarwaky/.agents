---
name: game-arch-diagram
description: Software/game architecture diagrams as a parametric script — layered bands, rider-chip band titles, semantic tints with accent bars, update-order badges, white-halo edge labels, and the six real collision defects found by vision-judge rounds.
when-to-use: Use when drawing a software/game architecture figure with layered bands (input → state machine → core loop → meta systems → platform), scene/state machine with chips, cross-band feedback loops, and side build/CI chain that must pass an independent vision judge.
argument-hint: '<架构图描述|系统来源>'
---

# Game/software architecture diagram (parametric, design-polished)

Software/game architecture diagrams as a parametric script with layered bands, rider-chip band titles, semantic tints, update-order badges, and white-halo edge labels. All of it is flat color — no shadows, no gradients.

## When to use

Drawing a **software or game architecture figure** — layered bands (input → state machine → core loop → meta systems → platform), a scene/state machine with chips, cross-band feedback loops, and a side build/CI chain. The figure is original (no bitmap reference), expected to be revised, and must pass an independent vision judge. For generic structure figures see [`parametric-diagram`](../parametric-diagram/SKILL.md); for the end-to-end process see [`codex-figure-workflow`](../codex-figure-workflow/SKILL.md).

## Rules

| ID | Rule | Check |
|----|------|-------|
| R1 | **骑缝条带标题。** 每个虚线条带的标题是白色圆角芯片，坐在条带顶部边框上（白色填充、语义色边框 + 粗体彩色文字）。作为泳道标签，并释放条带顶行用于内容。 | 每个条带的标题芯片已在顶部边框上；白色填充、语义色边框、粗体彩色文字均存在。 |
| R2 | **语义色填充 + 左侧强调条。** 每个框获得其语义色 4% 薄色调填充，加上左边框 4px 实色条。即使在灰度缩略图中也能看出分组。 | 每个框有语义色 4% 填充和左侧 4px 实色强调条；灰度下仍能看出分组。 |
| R3 | **更新顺序徽章。** 顶部右角带有编号圆徽章 ①–⑥，匹配引擎每帧调用顺序。读者无箭头也能推断执行流。 | 徽章 ①–⑥ 已放置在核心循环框顶部右角；与引擎调用顺序一致。 |
| R4 | **白色晕染边标签。** 每个边标签带 `stroke="#fff" stroke-width="4.5" paint-order="stroke"`，因此任何标签在任何线或边框上都保持可读。 | 所有边标签都带白色晕染描边（`stroke="#fff"`、`stroke-width="4.5"`、`paint-order="stroke"`）。 |
| R5 | **条带右上角标签。** 每个条带右上角带小型灰色右对齐文本：事件驱动 / updatePlay(1/60)·60Hz / 跨局持久 / 常驻。零杂乱元数据。 | 条带右上角有小型灰色右对齐元数据文本；无额外杂乱。 |
| R6 | **三层排版节奏。** 图标题 34 / 框主文本 22 粗体 / 框次文本 15 + 条带芯片 20 / 边标签 14.5，在 1720px 画布上。可缩小而不崩溃。 | 标题/主文本/次文本/芯片/边标签尺寸与 1720px 画布匹配；缩放不崩溃。 |
| R7 | **状态机微流程。** 顺序芯片间用箭头 →；并行芯片间用点 (·)；子场景用「← 由 select 进入」注释。 | 顺序芯片间用 →；并行芯片间用 (·)；子场景注释用「← 由 select 进入」。 |
| R8 | **文本宽度预算。** 每处标签与容器相遇处都执行文本宽度预算：legend 行中 `est_w(label) + start_x + 20 < W`；框次文本行中 `est_w(sub_line) < w − 24`；拆分为两行而非缩小字体。 | 所有标签均满足 `est_w()` 预算；次文本行不超过 `w − 24`；溢出标签已拆分为两行。 |
| R9 | **配置声明块。** `make_arch.py` 结构：`GROUPS`（条带），`BOXES`（框），`BADGES`（核心框：id → 更新顺序数字），`EDGES`（`E([waypoints], label, lx, ly, color, dash, anchor)`——折线，箭头在最后一段），`STYLE`（调色板常量 + 字体尺寸 + 线宽，一处），`V_RHYTHM`（每框高度文本垂直居中），`est_w(text, size)`（文本宽度预算：CJK 1.0×size，latin 0.56×size）。 | `make_arch.py` 包含所有声明块；`GROUPS`/`BOXES`/`BADGES`/`EDGES`/`STYLE`/`V_RHYTHM`/`est_w` 均存在且可运行。 |
| R10 | **不画愿望。** 从源码（层、模块真实类/函数名、数据流、持久化、构建/CI 链）清点真实系统——永不画愿望或未实现功能。 | 图内容来自源码清点；未画未实现功能或愿望。 |
| R11 | **带间距的等距网格。** 按数据流自上而下绘制条带；每条带一种语义色；≤3 种强调色。将框置于等距间距网格上；次文本至多两行；`EDGES` 作为带方式点的折线（在指定通道中正交折拐）。 | 条带按数据流自上而下；每条带一种语义色；≤3 强调色；框在等距网格上；次文本 ≤2 行；边为带方式点折线。 |
| R12 | **视觉验收工作流。** 渲染 → 导出 → 判断，如 [`visual-acceptance`](../visual-acceptance/SKILL.md)：内联 HTML 页面、HTTP（IAB/webview 代理无法 `goto file:`）下的精确尺寸视口截图、PIL 拼接半幅、`check_tiling.py`，然后由独立视觉裁判判断。从裁判像素证据中修复根本原因，重新渲染，有针对性地重新检查。 | 已使用内联 HTTP 页面渲染；精确尺寸视口截图；PIL 拼接；`check_tiling.py`；独立视觉裁判 PASS。 |
| R13 | **缺陷目录。** 预检由视觉裁判发现的六个缺陷：(1) 长重绕箭头穿过无关框 —— 路由重绕在顶部条带上方而非行间；(2) 垂直段穿过条带标题 glyph —— 缩短标题；移动原点 x 超过标题 `est_w` 末尾；或将水平折拐放在 glyph 行下方；(3) 边标签宽于框间间隙而跨越两边框 —— 将标签移至条带标题条行；(4) 正交角在骑缝芯片内部 —— 在 `chip_bottom = band_y + 16` 下方再转向目标；(5) 水平段擦过右侧条带标签 glyph 底部 —— 将该段置于 `band_y+40` 或更低；(6) 图例行宽于画布 —— `legend_x + est_w(最长行) + 20 < W`；缩短措辞而不是缩小字体。 | 六个缺陷均已预检并修复；重绕在顶部条带上方；垂直段不穿标题；标签在标题条行；正交角在芯片下方；水平段在 `band_y+40` 或更低；图例行符合 `legend_x + est_w() + 20 < W`。 |
| R14 | **SVG 必须通过 HTTP 导出。** SVG 必须通过内联 HTML 导出 —— IAB/webview 代理无法导航 `file:`，且 `<img src="*.svg">` 渲染错误。 | SVG 已通过内联 HTTP 页面导出；未使用 `<img src="*.svg">` 或 `file:` 路径。 |

## Routing

| Step | File | Purpose |
|------|------|---------|
| 1 | `make_arch.py` | 实际被接受的图例源：字狂潮 v2.3 游戏架构，1720×1400：条带、带芯片的场景机、6 个带徽章的核心模块、带反馈环的元经济条带、平台条带、构建链、图例。 |
| 2 | `examples/arch-v2@2x.png` | 最终渲染（3440×2800，由视口半幅拼接）。 |
| 3 | `examples/arch-v2.svg` / `arch-v2@1x.png` | 矢量源与全视图预览。 |
| 4 | [visual-acceptance](../visual-acceptance/SKILL.md) | 渲染 → 导出 → 判断工作流与缺陷目录。 |
| 5 | [codex-figure-workflow](../codex-figure-workflow/SKILL.md) | 端到端图制作流程。 |
| 6 | SKILL.md | 本技能概览。 |
