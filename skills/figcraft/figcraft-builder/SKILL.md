---
name: figcraft-builder
description: Builds native FigCraft UI designs and screens from one or more reference images or written specifications. Applies reference mapping, reusable components, auto layout, visual fidelity, and strict scope control without inventing screens or content.
when-to-use: Use when building native FigCraft UI designs and screens from one or more reference images or written specifications with reference mapping, reusable components, auto layout, visual fidelity, and strict scope control.
argument-hint: '<参考图路径|需求描述> <目标设备|视口>'
---

# FigCraft Builder

Turn supplied references or approved written requirements into editable native `.figcraft` designs. Pair with `figcraft-prototyper` for interactions and `figcraft-review` for the final quality gate.

Load the `figcraft` coordinator for intake, scope, and completion rules.

## Rules

| ID | Rule | Check |
|----|------|-------|
| R1 | **匹配源。** 仔细重建层级、布局、文字、排版、颜色、圆角、效果、图像与可见状态。不要用通用模板替换有特色的参考。 | 设计层级与参考图逐项匹配；未发现通用模板替换。 |
| R2 | **原生构建。** 在可改善可编辑性与一致性处使用 frames、auto layout、components、instances、vectors、styles 与 variables。将 artwork 委派给 `figcraft-svg`、icons 委派给 `figcraft-icons`、字体委派给 `figcraft-typography`。 | 使用了原生 FigCraft 结构；artwork/icons/字体已委派。 |
| R3 | **保持范围精确。** 只构建参考或明确批准需求所代表的 screens、states、overlays 与 responsive sizes。 | 已构建的 screens/states/overlays 均在参考或批准范围内；无额外页面。 |
| R4 | **询问关键模糊性。** 不要猜测 page mapping、导航结果、隐藏状态、产品 copy、数据含义或不受支持的行为。 | 未猜测页面映射/导航结果/隐藏状态/产品 copy/数据含义；关键模糊性已询问。 |
| R5 | **验证后保存。** 检查 layer tree 并渲染临时截图进行视觉检查。不要将预览 PNG 导出为交付物（除非用户要求）。 | 已通过 `inspect_document` 与临时 `screenshot` 验证设计；未将临时截图作为交付物。 |
| R6 | **Intake：创建参考清单。** 创建层之前，清点每个提供的参考（Ref、Document page、Screen/frame、State/overlay、Viewport、Notes）。 | 已创建参考清单；每个提供的参考已映射到 screen/state/overlay/responsive variant。 |
| R7 | **Intake：多参考。** 将每个图像映射到 screen、state、overlay 或 responsive variant。识别共享 shell 元素与可复用组件。比较参考的有意差异 vs 意外不一致。除非另有明确流程，保持用户提供顺序。如果两个参考冲突或关系不清，询问。 | 每个参考已映射；已识别共享元素与可复用组件；已比较差异；保持用户顺序或已询问冲突。 |
| R8 | **Intake：无图请求。** 先读完整提示并提取所有明确约束。如果信息足够，继续。如果信息不足，只询问决策阻塞细节：目标平台/视口、必需 screens、确切或代表性内容、视觉方向/设计系统、必需 states/interactions。 | 已从提示提取所有明确约束；信息足够时继续，不足时只询问决策阻塞细节。 |
| R9 | **Visual Decomposition：记录。** 对每个参考或批准的屏幕，记录：viewport 和 safe-area 行为；fixed、sticky、scrollable 和 overlay 区域；内容层级和阅读顺序；颜色和排版角色；间距、网格、圆角、描边和效果模式；适合组件的重复元素；可能的交互元素和所有可见状态；必须导入、重新创建或请求的资产。 | 已为每个参考记录 viewport/safe-area、区域、层级、颜色/排版、间距/网格/圆角/描边/效果、可复用组件、交互元素/状态、资产。 |
| R10 | **Visual Decomposition：使用真实预设。** 使用目标的真实设备预设。`frame.presets` 列出引擎提供的内容，`frame.create {preset}` 以该确切尺寸创建框架；协调器技能携带目录和选择规则。如果用户提供了参考的自有尺寸，使用之。当源另有说明时，不要强制使用记住的尺寸、圆角或字体。 | 已使用 `frame.presets` 中的真实预设或用户提供的尺寸；未强制使用记住的尺寸/圆角/字体。 |
| R11 | **Structure：优先使用 auto layout。** 对内容区域、控件、卡片行、列表、标签、导航和重复组件优先使用 auto layout。对 overlay、浮动控件、状态栏和装饰层使用绝对定位。 | 内容区域/控件/卡片/列表/导航使用 auto layout；overlay/浮动控件/状态栏/装饰层使用绝对定位。 |
| R12 | **Structure：语义命名。** 使用 `Screen/Home`、`Section/Recommendations`、`Card/Article`、`Button/Continue`、`Input/Email/Default`、`Overlay/ConfirmDelete` 等语义名称。 | 层名称使用语义命名（如 `Screen/Home`、`Card/Article`、`Button/Continue`）。 |
| R13 | **MCP：先 `list_commands`。** 使用不熟悉的操作前先调用 `list_commands`。直接 MCP 工具直接使用；仅在 `run_command` 或 `batch` 内使用命令信封。 | 在不熟悉操作前已调用 `list_commands`；直接工具直接调用；命令信封仅在 `run_command`/`batch` 内使用。 |
| R14 | **MCP：坐标相对父级。** 坐标相对于直接父框架。Auto-layout 子元素由布局属性而非手动 `x`/`y` 定位。 | 坐标相对于直接父级；auto-layout 子元素使用布局属性定位。 |
| R15 | **资产委派。** 将界面图标委派给 `figcraft-icons`（从真实图标集获取，而非手画字形）。将插图、吉祥物、徽标和有机 artwork 委派给 `figcraft-svg`（以 SVG 编写曲线并作为可编辑矢量导入）。字体选择与安装字体委派给 `figcraft-typography`。 | 图标/插图/字体已分别委派给 `figcraft-icons`/`figcraft-svg`/`figcraft-typography`。 |
| R16 | **导入原文件。** 当用户提供 SVG 或图像时，用 `file.import` 导入原文件而非重新绘制。SVG 变为形状的可编辑框架，图像变为图像层。 | 用户提供的 SVG/图像已通过 `file.import` 导入；未重新绘制。 |
| R17 | **简单一次性字形可以是原生矢量。** 例如：chevron、checkmark、close 图标——使用 `vector` 类型与 `path`。不要堆叠基本形状模拟详细 artwork。不要发明从未提供的资产。 | 简单一次性字形为 `vector` 类型；未堆叠基本形状模拟详细 artwork；未发明未提供资产。 |
| R18 | **验证与交接。** 每个有意义的屏幕或参考组后：用 `get_node` 或 `inspect_document` 检查相关子树；渲染临时 `screenshot` 并比较构图、间距、裁切、排版和可见状态与源；在原型化前修正不匹配；记录交互候选和预期结果——如果结果未显示或指定，询问而非发明。 | 已检查子树、比较截图与源、修正不匹配、记录交互候选与预期结果。 |
| R19 | **保存后检查。** 通过 `save_file` 保存，然后再次检查以确认活动文档路径、页/屏覆盖范围和最终结构。`save_file` 在目标文件夹不存在时失败——先创建文件夹。报告构建内容、覆盖的参考、假设、缺失资产或限制，以及目标文件路径。 | 已通过 `save_file` 保存并再次检查；报告了构建内容、参考覆盖、假设、缺失资产/限制、目标路径。 |

## Routing

| Step | File | Purpose |
|------|------|---------|
| 1 | figcraft-builder/SKILL.md | 本技能概览与核心规则。 |
| 2 | figcraft/SKILL.md | FigCraft 协调器：intake、scope、完成规则。 |
| 3 | figcraft-icons/SKILL.md | Icons 子技能：界面图标映射与导入。 |
| 4 | figcraft-svg/SKILL.md | SVG 子技能：插图、角色、徽标与有机 artwork。 |
| 5 | figcraft-typography/SKILL.md | Typography 子技能：字体选择与安装。 |
| 6 | figcraft-prototyper/SKILL.md | Prototyper 子技能：交互接线与验证。 |
| 7 | figcraft-review/SKILL.md | Review 子技能：质量门禁与评分卡。 |
