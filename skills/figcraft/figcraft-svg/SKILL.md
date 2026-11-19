---
name: figcraft-svg
description: Builds illustrations, characters, logos, and decorative artwork for FigCraft by authoring SVG and importing it as editable native vectors. Use when a reference image contains artwork that primitive shapes cannot reproduce faithfully.
when-to-use: Use when a reference image contains artwork (mascots, characters, illustrations, hand-drawn doodles, logos, badges, decorative scenery, organic shapes) that primitive shapes cannot reproduce faithfully.
argument-hint: '<参考图路径|artwork 描述>'
---

# FigCraft SVG Illustration

Use this skill when a reference contains artwork rather than UI chrome: mascots, characters, illustrations, hand-drawn doodles, logos, badges, decorative scenery, or any curved form that ellipses and rectangles cannot express.

Load the `figcraft` coordinator for intake and scope rules. Pair with `figcraft-icons` for interface icons, which are a different problem.

## Rules

| ID | Rule | Check |
|----|------|-------|
| R1 | **选择合适的源。** 用户以文件提供资产 → `file.import` 导入原文件。绝不重新绘制。Boxes/bars/pills/simple discs/progress tracks → 原生基本形状在 `figcraft-builder` 中。标准界面图标 → `figcraft-icons` 通过 Iconify。曲线插图、角色、吉祥物、徽标标记、有机形状 → 在此编写 SVG 然后导入。摄影、栅格纹理、复杂绘制艺术 → 无法编写。要求用户提供资产。 | 用户提供的资产已通过 `file.import` 导入；简单形状在 Builder 中；标准图标在 Icons 中；曲线 artwork 在此编写 SVG；复杂艺术已要求用户提供资产。 |
| R2 | **验证导入行为。** `file.import` 接受 `{path}` 或 `{data (base64), name}` 并将 SVG 转为可编辑形状框架。已验证：元素上的 `id` 属性变为该图层的名称——在每个形状和组上放置 `id`。组变为组，保留嵌套。`<circle>` 变为真实椭圆图层，而非路径。线性和径向渐变以渐变填充保存。描边保存，因此描边重量在导入后仍可编辑。`currentColor` 解析为实心黑色——导入后重新着色。`<text>` 变为可编辑文本图层，但 **SVG `font-family` 会丢失**。根框架以文件或你传递的 `name` 命名。导入返回根框架 id，并可能返回 `warnings` 列出被丢弃的内容——阅读它们。 | 导入的 SVG 具有 `id` 属性、`viewBox`、正确的嵌套、渐变/描边保留、`currentColor` 已重新着色；导入的 `warnings` 已阅读；`<text>` 元素不存在或已标记。 |
| R3 | **不要在 SVG 中放置文字。** 由于 font family 不会保存，**不要在 SVG 中放置 copy**。用 `figcraft-builder` 或 `figcraft-typography` 原生编写文本。 | SVG 内无 `<text>` 元素；所有文字均为原生文本层。 |
| R4 | **编写：设置尺寸。** 将 SVG 写到临时文件，然后导入。设置 `width`、`height` 和匹配的 `viewBox`，以便 artwork 以预期大小导入。 | SVG 具有 `width`、`height` 与匹配的 `viewBox`。 |
| R5 | **编写：语义命名。** 用文档其余部分使用的相同语义方案命名 ids，如 `Whale/Body` 或 `Mascot/Head`。 | SVG 中所有 `id` 属性均使用语义命名（如 `Whale/Body`、`Mascot/Head`）。 |
| R6 | **编写：顺序与调色板。** 元素从后到前排序；最后一个元素位于顶部。使用文档的调色板——不要引入参考或批准系统中不存在的颜色。 | 元素从后到前排序；颜色均来自文档调色板；未引入新颜色。 |
| R7 | **编写：简洁路径。** 优先使用少量刻意路径而非数十个碎片。审查者必须能够编辑结果。 | artwork 由少量刻意路径组成；审查者可编辑。 |
| R8 | **编写：省略未确认效果。** 省略未确认能导入的滤镜、遮罩和效果；使用它们时检查 `warnings`。 | 未使用未确认的滤镜/遮罩/效果；或已检查 `warnings`。 |
| R9 | **手绘/马克笔外观：描边配置文件。** 参考 artwork 是蜡笔、马克笔、铅笔或墨水涂鸦时，平面填充路径看起来太干净。引擎可以直接表达描边特性：`stroke.widthProfile` 带有 `uniform`、`wedge`、`taper`、`eye`、`rounded` 或 `pinch` 沿路径改变重量。`stroke.brush` 带有 `taper`、`ink`、`ribbon` 或 `bristle` 沿路径拉伸画笔；`dots`、`stars`、`confetti`、`leaves` 沿其散布。两者都接受 `ids`，两者都在导入 SVG 的描边上工作。 | 手绘外观使用 `stroke.widthProfile` 与 `stroke.brush`；两者接受 `ids`；在导入 SVG 描边上工作。 |
| R10 | **手绘/马克笔外观：开放描边路径。** 将这些元素编写为**描边开放路径**而非填充轮廓，否则没有描边供画笔跟随。 | 手绘元素为描边开放路径；非填充轮廓。 |
| R11 | **标准化：导入后。** 1) 将根框架从文件名重命名为语义名称。2) 重命名 SVG 留下的任何通用图层，如 `Group` 或 `Vector`。3) 重新着色任何以 `currentColor` 进入的黑色。4) 将框架重新父级到拥有它的屏幕或组件中，并设置其位置和大小。5) 将跨屏幕重用的 artwork 转为组件，以便副本保持同步。6) 删除转换器产生的空组和杂散图层。 | 根框架已重命名；通用图层已重命名；`currentColor` 黑色已重新着色；框架已重新父级并设置位置/大小；复用 artwork 已转为组件；空组/杂散图层已删除。 |
| R12 | **保真度循环。** 1) 编写 SVG 并导入。2) 用 `screenshot` 渲染，或用 `figcraft-cli render` 驱动 CLI。3) 与参考比较：轮廓、比例、重量、颜色，以及 artwork 在布局中的位置。4) 修正路径并重新导入——替换先前图层而非堆叠第二个副本。5) 当 artwork 在实际查看大小下读起来像同一主题时停止。 | 已编写/导入 SVG；已渲染并比较；已修正路径并重新导入；artwork 在实际大小下读起来正确。 |
| R13 | **小尺寸判断。** 在 artwork 实际将查看的大小判断小 artwork。在 200px 下正确读出的标记在 28px 下可能崩溃成一个 blob——为大小简化而非缩小详细版本。 | 已在 artwork 实际大小下判断小 artwork；或为大小简化。 |
| R14 | **边界。** 不要发明品牌徽标、吉祥物或商标 artwork——要求资产。不要追踪或复刻用户无权使用的第三方 artwork。不要用参考或 brief 未要求的装饰插图填充设计。将编写的每件 artwork 报告为解释，并说明无法匹配的内容。 | 未发明品牌/商标 artwork；未追踪无版权 artwork；未添加 brief 未要求的插图；已报告每件 artwork 为解释。 |

## Routing

| Step | File | Purpose |
|------|------|---------|
| 1 | figcraft-svg/SKILL.md | 本技能概览与规则。 |
| 2 | figcraft/SKILL.md | FigCraft 协调器：intake、scope、完成规则。 |
| 3 | figcraft-icons/SKILL.md | Icons 子技能：界面图标映射与导入（非 artwork）。 |
| 4 | figcraft-builder/SKILL.md | Builder 子技能：原生形状与布局构建。 |
| 5 | figcraft-typography/SKILL.md | Typography 子技能：字体选择与安装（原生文本）。 |
