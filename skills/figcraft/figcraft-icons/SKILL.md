---
name: figcraft-icons
description: Maps interface icons to a real icon set through the Iconify API and imports them into FigCraft as editable vectors. Use whenever a reference or specification calls for interface icons instead of hand-drawn glyphs.
when-to-use: Use whenever a reference or specification calls for interface icons instead of hand-drawn glyphs.
argument-hint: '<图标概念|图标描述>'
---

# FigCraft Icons

Interface icons are a sourcing problem, not a drawing problem. Hand-built glyphs drift in weight, grid, and style; a published icon set stays consistent. Use Iconify to find the icon, then import it as native vectors.

Load the `figcraft` coordinator for intake and scope rules. Use `figcraft-svg` for illustrations and characters, which are not icons.

## Rules

| ID | Rule | Check |
|----|------|-------|
| R1 | **绝不猜测图标名。** 图标名在不同集合间不可预测。猜测的名称返回空响应，空文件导入为 nothing。先搜索： `curl -s "https://api.iconify.design/search?query=whale&limit=12"`。响应报告总数和 `prefix:name` 标识符列表。只从该列表中选择。验证失败模式：`ph:whale-duotone` 看起来合理但返回 9 字节空 body，因为该图标不存在。 | 图标名均来自 Iconify 搜索结果；未猜测名称；未导入 9 字节空 body 的图标。 |
| R2 | **导入前验证。** 导入前验证。小于约 100 字节的 SVG，或不包含 `<path`、`<circle` 或 `<rect` 的 SVG，视为未命中。用不同词再次搜索，而不是发明名称。 | 导入的 SVG 均大于约 100 字节且包含 `<path`/`<circle`/`<rect`。 |
| R3 | **选一个集合并保持。** 读参考并匹配其图标个性，然后为整个文档选择一个家族：Thin/medium outline rounded caps → `lucide`、`tabler`、`ph` (regular)；Solid filled → `ph` (fill)、`mdi`、`material-symbols`；Duotone/two-tone → `ph` (duotone)、`material-symbols` (two-tone)；Playful rounded childlike → `fluent-emoji-flat`、`noto`、`streamline-emojis`；Platform-native → Android `material-symbols`、neutral iOS `tabler` 或 `lucide`。 | 文档中只使用一个图标家族；参考外观与选择的家族匹配。 |
| R4 | **不混合集合。** 在一个屏幕中混合集合是可见缺陷。如果所选集合缺少所需图标，故意决定：从同一集合中挑选近似等价物，或用 `figcraft-svg` 编写以匹配该集合的重量和网格。说明你做了什么。 | 同一屏幕中未混合多个图标集合；任何替代均已明确报告。 |
| R5 | **按设计需求大小获取。** 请求设计所需大小，然后导入： `curl -sL "https://api.iconify.design/lucide/house.svg?height=24" -o /tmp/icons/home.svg`，然后 `{"command": "file.import", "params": {"path": "/tmp/icons/home.svg", "x": 0, "y": 0}}`。有用查询参数：`height` 或 `width` 设定大小，`color` 设定平坦颜色。 | 图标按设计所需大小获取并导入；已使用 `height`/`width`/`color` 查询参数。 |
| R6 | **验证导入结果。** `lucide` 图标的验证导入结果：一个以文件命名的框架，包含一个描边矢量层组，`currentColor` 解析为实心黑色，层名为 `Group` 和 `Vector`。 | 导入的图标包含矢量子节点（非空框架）；`currentColor` 已解析为黑色。 |
| R7 | **标准化每个导入图标。** 1) 将框架重命名为文档方案，如 `Icon/Home`，并重命名通用子层。2) 重新着色——描边图标带有 `strokes`，填充图标带有 `fills`；设置图标实际使用的那个。3) 设置描边重量，使图标看起来像兄弟。4) 在一致的框（常用 20、24 或 28）上设定大小，并按上下文保持该框恒定。5) 将图标重新父级到拥有它的控件，并为控件设置触摸目标。图标是字形，不是点击区域。6) 为多次使用的图标创建组件，以便后续交换能更新所有实例。 | 框架/子层已重命名为语义名；颜色/描边/大小已标准化；图标已重新父级到 owning 控件；重复图标已转为组件。 |
| R8 | **覆盖检查。** 交接前：每个参考显示的图标都有真实导入的图标，而非占位形状。所有图标来自一个集合（或报告的故意例外）。重量、大小框和颜色角色一致。活动和非活动状态按参考显示方式不同。没有图标框架因失败获取而为空——检查树并确认每个都有矢量子节点。 | 每个参考图标都有真实导入；全部来自一个集合；重量/大小/颜色一致；状态差异与参考一致；无空图标框架。 |
| R9 | **尊重许可。** 尊重每个集合的许可。Iconify 在各自许可下重新分发集合；报告使用的集合，以便用户检查署名。 | 已报告使用的图标集合及其许可；用户可检查署名要求。 |

## Routing

| Step | File | Purpose |
|------|------|---------|
| 1 | figcraft-icons/SKILL.md | 本技能概览与规则。 |
| 2 | figcraft/SKILL.md | FigCraft 协调器：intake、scope、完成规则。 |
| 3 | figcraft-svg/SKILL.md | SVG 子技能：插图、角色、徽标与有机 artwork（非界面图标）。 |
| 4 | figcraft-typography/SKILL.md | Typography 子技能：字体选择与安装。 |
