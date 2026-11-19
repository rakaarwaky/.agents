---
name: figcraft-prototyper
description: Wires and verifies native FigCraft prototypes for sliders, navigation, buttons, overlays, alerts, component states, variables, and conditional flows. Keeps interactions synchronized with the final design and never claims unsupported editable input.
when-to-use: Use when wiring and verifying native FigCraft prototypes for sliders, navigation, buttons, overlays, alerts, component states, variables, and conditional flows, keeping interactions synchronized with the final design.
argument-hint: '<原型文件路径|交互需求>'
---

# FigCraft Prototyper

Add interactions only after required screens, overlays, and states exist. Use current FigCraft commands discovered with `list_commands`; do not rely on remembered schemas.

Load the `figcraft` coordinator for intake, scope, and completion rules. This skill covers wiring and verification.

## Rules

| ID | Rule | Check |
|----|------|-------|
| R1 | **交互合同：先检查再接线。** 接线前，检查所有相关页面并写紧凑交互清单：| Source layer | Trigger | Action(s) | Destination/state | Transition | Close/back path | Expected result |。每个必需交互元素必须出现在清单中。可见控件只有在用户未请求行为或清单标记为故意静态时才可保持非交互。 | 已写交互清单；每个必需交互元素在清单中；可见控件已标记为交互或静态。 |
| R2 | **交互合同：询问关键模糊性。** 在预期目的地、状态变化、关闭行为、验证规则或最终结果不清时询问。如果必需目的地不存在，询问是否构建它并请求参考或规范。永不生成未请求的占位屏幕。 | 未猜测目的地/状态变化/关闭行为/验证规则/最终结果；必需目的地存在或已询问；未生成占位屏幕。 |
| R3 | **运行时能力检查：`list_commands`。** 使用原型特性前，用窄过滤如 `proto`、`overflow`、`variable`、`component` 和预期 action 名调用 `list_commands`。严格遵循返回的 schema。 | 在使用原型特性前已调用 `list_commands`；严格遵循返回的 schema。 |
| R4 | **运行时能力：当前原生 action。** 当前原生 action 可能包括：`navigate`、`back`、`scrollTo`；`openOverlay`、`swapOverlay`、`closeOverlay`；`openUrl`；`changeTo`（组件变体）；`setVariable`、`setVariableMode`、`conditional`；一个交互上的多个 action。不要声称能力除非它出现在当前命令合同中。 | 只使用当前 `list_commands` 合同中确认的原生 action；未声称未确认的能力。 |
| R5 | **引擎检查 vs 你的责任。** 引擎会拒绝：未知 trigger、action、transition 或 easing 名；`overflow` 值在 `none|horizontal|vertical|both` 之外；overlay `position` 在 `center|topLeft|topCenter|topRight|bottomLeft|bottomCenter|bottomRight|manual` 之外；不存在的 `dest` id。引擎不会检查：`changeTo` 目的地是否为变体；overlay 有关闭路径；滚动轨道大于其 viewport；必需屏幕可达。这些是你的责任。 | 已读错误文本；已验证 `changeTo` 目的地为变体、overlay 有关闭路径、滚动轨道大于 viewport、必需屏幕可达。 |
| R6 | **滑块与滚动内容。** 滑块是滚动 viewport 加超大内容轨道：外层框架：固定 viewport 尺寸、预期 `overflow` 方向、刻意裁剪；内层框架：水平或垂直 auto layout、一致 gap/padding、内容大于 viewport；卡片/项目：一致尺寸除非参考明确变化。仅当预期交互需要显式 action 时使用 `onDrag`。原生 overflow 不需要伪造点击导航交互。 | 外层框架有固定 viewport/overflow/clipping；内层框架有 auto layout/gap/padding 且内容大于 viewport；`onDrag` 仅用于需要显式 action 的交互。 |
| R7 | **滑块验证：overflow 是只写不读的。** `overflow` 对检查是只写不读的：`inspect_document`、`get_node`、`inspect.properties`、`inspect.code` 即使设置并保存后也不报告它。用三种方式验证：1) `set_properties` 调用成功——由于引擎拒绝其他值，成功意味着方向已应用；2) 检查两个框架并比较尺寸——轨道的报告宽度/高度必须超过 viewport 的，适配在 viewport 内的轨道无法滚动；3) 如果需要文件中证据，在保存的 `.figcraft` 文档（zip 包含 `document.json`）中读取该节点上的 `overflow`。不要写"overflow confirmed via inspect_document." 该字段不会出现。 | 已通过 `set_properties` 成功、尺寸比较、或保存的 `.figcraft` 文档中的 `overflow` 字段验证滑块；未在 `inspect_document` 中声称 overflow 已确认。 |
| R8 | **导航与按钮。** 将交互附加到最终可见按钮/容器而非子标签/图标。交互边界应覆盖完整控件并满足所选触摸目标标准。使用显式流程起始点。确保必需目的地可达，并在预期处提供返回行为。不要习惯性使用 Smart Animate——根据设计和导航模型选择 instant、dissolve、smart animate、move、push 或 slide。 | 交互附加到最终可见按钮/容器；交互边界覆盖完整控件并满足触摸目标标准；已设置流程起始点；必需目的地可达；未习惯性使用 Smart Animate。 |
| R9 | **覆盖层、弹出和警报。** 用覆盖层表示对话框、菜单、弹出、toast、警报和底部 sheet（当符合设计时）。每个 overlay 必须有设计要求的关闭行为：用 `closeOverlay` 或约定 action 接线可见 Close/Cancel/backdrop 控件；仅在适当时使用 outside-click 关闭；当指定时防止 destructive confirmation 或必需决策的 outside 关闭；验证 success、error、confirmation、timeout 和 follow-up 状态（当在范围内时）。警报不是画出来就完成了——其触发器、消息状态、主/次 action、关闭和最终结局必须与批准流程匹配。 | overlay 有关闭路径（`closeOverlay` 或 outside-click）；destructive confirmation 防止 outside 关闭；success/error/confirmation/timeout/follow-up 状态已验证。 |
| R10 | **组件状态、变量与条件。** 对直接视觉状态使用组件变体加 `changeTo`。对结果依赖先前 action 或进入/模拟值的流程使用变量和 `conditional`。只支持源或批准规范要求的状态，如：default、hover、pressed、focused、selected、disabled；empty、filled、invalid、loading、success、error；open 和 closed；destructive confirmation 和 completion。保持状态变化附加到它们视觉影响的组件或控件。验证变体名称和目的地在设计编辑后仍存在。不要画重复框架并称它们为交互式除非必需过渡已接线。`changeTo` 接受任何现有图层 id 而不报错，包括根本不是变体的普通顶级框架—— such a wire 干净保存但在播放中什么也不做。在接线 `changeTo` 前后，通过检查确认源是实例且目的地是同一组件集的变体。 | 视觉状态用组件变体+`changeTo`；条件流程用变量+`conditional`；只支持批准的状态；状态变化附加到影响组件；变体/目的地在编辑后仍存在；`changeTo` 源是实例且目的地是变体。 |
| R11 | **表单与打字边界。** 文本层（agent 用 `type_text` 编辑）不是可编辑的原型输入。当前 FigCraft 命令合同不暴露匹配原生自由文本运行时输入的命令。当用户要求可打字表单时：1) 重新检查 `list_commands` 是否有当前输入能力；2) 如果没有，在实现前说明限制；3) 询问是否可接受模拟流程；4) 如果批准，仅对约定情况使用组件状态、文本属性、变量、key trigger 和条件模拟，并标记为模拟输入；5) 如果需要真实任意文本输入，不要声称 `.figcraft` 原型提供。输入状态、点击/聚焦字段、验证代表性值和提交表单可以模拟。任意文本输入不能假设。 | 未声称任意文本输入；已询问是否接受模拟流程；模拟结果已标记为模拟输入；或已说明不支持任意文本输入。 |
| R12 | **热区与同步。** 优先使用可见控件框架作为热区。如果必须使用单独热区：命名为 `Hotspot/<purpose>`；放在对应控件所在的同一 screen/component 层级中；边界匹配完整目标；不覆盖无关控件；在任何布局或组件更改后再次检查。保存前，检测缺失目的地、过期图层 ID、重复或重叠热区、通过子文本/图标层接线的控件、无关闭路径的覆盖层和不可达的必需状态。 | 优先使用可见控件框架；单独热区命名为 `Hotspot/<purpose>` 并匹配目标边界；未覆盖无关控件；保存前检测缺失/过期/重复/不可达。 |
| R13 | **验证：结构。** 用 `inspect_document` 检查相关页面，用 `get_node` 检查深子树。它报告每层 `interactions` 和每页 `flows`，因此 trigger、action 类型、`dest`、transition、duration 和 easing 均可检查。确认源 id、目的地 id、边界、组件、变体和变量。记住 `overflow` 不被报告——用第 3 节的尺寸比较验证滑块。 | 已用 `inspect_document`/`get_node` 检查结构与 interactions；已确认源/目的地/边界/组件/变体/变量；滑块用尺寸比较验证。 |
| R14 | **验证：图。** 走报告的交互并确认每个必需路径可达且有预期的返回、关闭、成功、错误或终止路由。查找缺失关闭路径、`changeTo` 接线指向非变体、通过子文本或图标层接线的控件、以及不可达的必需状态。 | 已走交互图并确认必需路径可达；已查找缺失关闭/非变体 changeTo/子层接线/不可达状态。 |
| R15 | **验证：持久化与报告。** 保存文档，然后再次检查。`save_file` 不创建缺失文件夹——确保目标目录存在。**运行时播放不可从该工具集自动化**——在无头会话中 `proto.preview` 和 `proto.present` 返回成功但不产生窗口，且 `pointer` 驱动画布而非原型播放器。成功的 `proto.preview` 调用不是任何可工作的证据——不要将其转化为运行时验证声明。报告验证的结构、你跟踪的路径、以及用户必须执行的点击检查（命名每个），例如：从卡片打开 overlay，通过点击外部关闭，水平拖动卡片行。报告实现的交互、模拟行为、不受支持的行为、手动检查和保存的 `.figcraft` 路径。 | 已保存并再次检查；目标目录存在；未将 `proto.preview` 成功视为运行时验证；已报告结构/路径/手动检查/模拟行为/不支持行为/保存路径。 |

## Routing

| Step | File | Purpose |
|------|------|---------|
| 1 | figcraft-prototyper/SKILL.md | 本技能概览与规则。 |
| 2 | figcraft/SKILL.md | FigCraft 协调器：intake、scope、完成规则。 |
| 3 | figcraft-builder/SKILL.md | Builder 子技能：屏幕、组件与布局构建（原型的前置条件）。 |
| 4 | figcraft-icons/SKILL.md | Icons 子技能：界面图标映射与导入。 |
| 5 | figcraft-svg/SKILL.md | SVG 子技能：插图、角色、徽标与有机 artwork。 |
| 6 | figcraft-typography/SKILL.md | Typography 子技能：字体选择与安装。 |
| 7 | figcraft-motion/SKILL.md | Motion 子技能：在原型正确后添加过渡与动画。 |
| 8 | figcraft-review/SKILL.md | Review 子技能：原型正确性与质量门禁。 |
