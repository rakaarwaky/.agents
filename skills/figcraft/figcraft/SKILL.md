---
name: figcraft
description: Coordinates end-to-end FigCraft work from one or more visual references or written requirements through native design construction, interactive prototyping, verification, review, and save. Use for any request to create, reconstruct, prototype, or audit a .figcraft interface.
when-to-use: Use for any request to create, reconstruct, prototype, or audit a .figcraft interface.
argument-hint: '<新建|复刻|原型|审查|设计> <参考图|需求描述|项目路径>'
---

# FigCraft Coordinator

Use FigCraft as a Figma-class design and prototyping tool. All sub-workflows below live in this one skill; load no separate skill for FigCraft work.

## Rules

| ID | Rule | Check |
|----|------|-------|
| R1 | **Builder：匹配源。** 仔细重建层级、布局、文字、排版、颜色、圆角、效果、图像与可见状态。不要用通用模板替换有特色的参考。 | 设计层级与参考图逐项匹配；未发现通用模板替换。 |
| R2 | **Builder：原生构建。** 在可改善可编辑性与一致性处使用 frames、auto layout、components、instances、vectors、styles 与 variables。将 artwork 委派给 `figcraft-svg`、icons 委派给 `figcraft-icons`、字体委派给 `figcraft-typography`。 | 使用了原生 FigCraft 结构（auto layout/components/styles/variables）；artwork/icons/字体已委派。 |
| R3 | **Builder：保持范围精确。** 只构建参考或明确批准需求所代表的 screens、states、overlays 与 responsive sizes。 | 已构建的 screens/states/overlays 均在参考或批准范围内；无额外页面。 |
| R4 | **Builder：询问关键模糊性。** 不要猜测 page mapping、导航结果、隐藏状态、产品 copy、数据含义或不受支持的行为。 | 未猜测页面映射/导航结果/隐藏状态/产品 copy/数据含义；关键模糊性已询问。 |
| R5 | **Builder：验证后保存。** 检查 layer tree 并渲染临时截图进行视觉检查。不要将预览 PNG 导出为交付物（除非用户要求）。 | 已通过 `inspect_document` 与临时 `screenshot` 验证设计；未将临时截图作为交付物。 |
| R6 | **Icons：绝不猜测图标名。** 先搜索 Iconify（`curl -s "https://api.iconify.design/search?query=...&limit=12"`），只从返回的 `prefix:name` 列表中选择。 | 图标名均来自 Iconify 搜索结果；未使用猜测名称。 |
| R7 | **Icons：一个文档一个集合。** 从同一参考外观匹配一个图标家族；不要混合不同集合（混合是可见缺陷）。 | 全图使用同一图标集合；无混合（或有明确报告）。 |
| R8 | **SVG：文件导入优先。** 若用户以文件提供资产，用 `file.import` 导入原文件——绝不重新绘制。 | 用户提供的 SVG/图片资产已通过 `file.import` 导入；未重新绘制。 |
| R9 | **SVG：正确声明尺寸。** 设置 `width`、`height` 和匹配的 `viewBox`。 | SVG 具有 `width`、`height` 与匹配的 `viewBox`。 |
| R10 | **SVG：避免文本。** SVG 导入后 `font-family` 会丢失——不要在 SVG 内放置文字。 | SVG 内无 `<text>` 元素；所有文字均为原生文本层。 |
| R11 | **Typography：观察而非识别。** 不要声称能从图片确定字体。提供两三个候选并说明理由，除非用户另行指定。 | 提供了 2-3 个候选字体及理由；未声称从图片确定确切字体。 |
| R12 | **Typography：检查 `text.missingFonts`。** 下载前先搜索 `text.fonts`。`font.downloads` 返回 `allowed`——如果为 false，告知用户确切的开关或同意使用已安装字体；不要反复重试。 | 已检查 `text.fonts`；已检查 `font.downloads` 的 `allowed` 状态；未反复重试。 |
| R13 | **Typography：构建小型字体系。** 定义参考实际使用的角色（display/title、section heading、card/list title、body、caption/metadata/pill），每个角色记录 size、face、line height、letter spacing。 | 已构建字体系（5 个角色）；每个角色记录了 size/face/line height/letter spacing。 |
| R14 | **Prototyper：先有屏幕/覆盖/状态，再接线。** 只在必需 screens、overlays、states 存在后才添加交互。 | 在添加交互前所有必需 screens/overlays/states 已存在；接线在验证之后。 |
| R15 | **Prototyper：写交互清单。** 接线前写交互清单（Source layer、Trigger、Action(s)、Destination/state、Transition、Close/back path、Expected result）。 | 已写交互清单；每个必需交互元素出现在清单中。 |
| R16 | **Prototyper：每个 overlay 有关闭路径。** 每个 overlay 必须有可见 Close/Cancel/backdrop 控件（带 `closeOverlay`），或在适当情况下支持 outside-click 关闭。 | 每个 overlay 都有 `closeOverlay` 或 outside-click 关闭路径。 |
| R17 | **Motion：最后运行。** 在流尚未正确之前不要调整过渡。Prototyper 必须已接线并检查所有路径，然后才能在此处调整任何内容。 | `figcraft-prototyper` 已完成所有必需路径的接线与检查；Motion 在之后运行。 |
| R18 | **Motion：从交互选择运动。** tab switch → instant/dissolve 0–120ms easeOut；forward detail → slideIn/push left 260–320ms easeInOut；back → 镜像 240–300ms；bottom sheet open → moveIn bottom 220–280ms easeOut；close → moveOut bottom 180–240ms easeIn；smartAnimate morph → 240–320ms easeInOut/gentle；toast dismiss → dissolve on afterDelay 160–240ms。 | 运动选择符合交互类型；持续时间/缓动符合指导；非常规运动 ≤ ~400ms。 |
| R19 | **Review：审计实际文档，不仅看截图。** 使用 `inspect_document`/`get_node` 检查每一页、screen、state、overlay 和原型路径。 | 已使用 `inspect_document`/`get_node` 检查实际 `.figcraft` 文档；不仅依赖截图。 |
| R20 | **Review：Design Quality Score（100 pts）。** Structure & Auto Layout 40（auto-layout adoption 15, semantic naming 15, hierarchy/clipping 10）；Tokens & Visual Consistency 30（color roles 10, spacing/sizing 10, typography/radius/effects 10）；Accessibility & Usability 30（target size 15, contrast/readability 10, text resizing/overflow 5）。 | 已计算 Design Quality Score；每个扣分项有 layer name/id 与具体修复。 |
| R21 | **Source of Truth：`list_commands`。** FigCraft 命令和 schema 会变化。使用不熟悉的特性前，先用窄过滤（如 `page`、`proto`、`overflow`、`component`、`variable` 或预期 action 名）调用 `list_commands`。 | 在使用不熟悉特性前已调用 `list_commands`；使用了返回的命令 id 与参数 schema。 |
| R22 | **Source of Truth：区分表单。** 直接 MCP 工具（如 `create_node`、`set_properties`、`inspect_document`、`get_node`、`screenshot`、`save_file`）直接接收自己的参数；`run_command` 接收 `{ "command": "<id>", "params": {...} }`；`batch` 接收 `commands` 数组，可在步骤间使用 `as` 和 `$ref`。 | 已正确区分直接 MCP 工具、`run_command` 和 `batch` 的用法。 |
| R23 | **Source of Truth：永不发明。** 永不发明命令、属性、触发器、action 或运行时能力。 | 未使用任何未在 `list_commands` 或当前 FigCraft schema 中确认的命令/属性/触发器/action/能力。 |

## Routing

| Step | File | Purpose |
|------|------|---------|
| 1 | figcraft/SKILL.md | FigCraft 协调器：intake、scope、完成规则与子工作流概览。 |
| 2 | figcraft-builder/SKILL.md | Builder 子技能：从参考或书面需求构建原生 `.figcraft` 设计。 |
| 3 | figcraft-icons/SKILL.md | Icons 子技能：通过 Iconify API 将 interface icons 映射为可编辑矢量。 |
| 4 | figcraft-svg/SKILL.md | SVG 子技能：构建 illustrations、characters、logos 与 decorative artwork。 |
| 5 | figcraft-typography/SKILL.md | Typography 子技能：选择并安装字体，验证无静默回退。 |
| 6 | figcraft-prototyper/SKILL.md | Prototyper 子技能：接线并验证原生 FigCraft 原型（sliders、navigation、buttons、overlays、alerts、component states、variables、conditional flows）。 |
| 7 | figcraft-motion/SKILL.md | Motion 子技能：在流程已正确后添加 transition 与 animation polish。 |
| 8 | figcraft-review/SKILL.md | Review 子技能：审查原生 FigCraft 文件的结构、auto layout、visual consistency、accessibility、reference coverage 与 prototype correctness。 |
