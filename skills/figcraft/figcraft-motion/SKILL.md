---
name: figcraft-motion
description: Adds transition and animation polish to a FigCraft prototype after its flows already work, using verified transition types, easings, springs, and delayed triggers. Use as the final pass, never as a substitute for correct wiring.
when-to-use: Use as the final pass on a FigCraft prototype whose flows already work, to add transition and animation polish using verified transition types, easings, springs, and delayed triggers.
argument-hint: '<原型文件路径|交互描述>'
---

# FigCraft Motion

Run this last. Motion polish on a broken flow hides the breakage. `figcraft-prototyper` must already have every required path wired and inspected before anything here is tuned.

Load the `figcraft` coordinator for completion rules.

## Rules

| ID | Rule | Check |
|----|------|-------|
| R1 | **最后运行。** 在流尚未正确之前不要调整过渡。Prototyper 必须已接线并检查所有路径，然后才能在此处调整任何内容。 | `figcraft-prototyper` 已完成所有必需路径的接线与检查；Motion 在之后运行。 |
| R2 | **引擎提供：transition 类型。** `transition` 类型：`instant`、`dissolve`、`smartAnimate`、`moveIn`、`moveOut`、`push`、`slideIn`、`slideOut`，带有 `direction` 为 `left`、`right`、`top`、`bottom`。 | 过渡类型与方向均为引擎支持的值；未发明类型/方向。 |
| R3 | **引擎提供：时长与缓动。** `durationMs` 在交互上。`easing`：`linear`、`easeIn`、`easeOut`、`easeInOut`、`easeInBack`、`easeOutBack`、`easeInOutBack`、`gentle`、`quick`、`bouncy`、`slow`，或自定义 `{customBezier {x1, y1, x2, y2}}` 或 `{customSpring {mass, stiffness, damping}}`。 | `durationMs` 与 `easing` 均为引擎支持的值；未发明缓动。 |
| R4 | **引擎提供：延迟与保留滚动。** `delayMs` 用于 mouse enter、leave、down、up，以便 hover 稳定后再触发。`afterDelay {ms}` 触发器用于定时序列（如 splash、自动关闭的 toast、分阶段显示）。`navigate` 接受 `preserveScroll`，在过渡期间保持长页面的滚动位置。 | `delayMs`、`afterDelay`、`preserveScroll` 按引擎规范使用。 |
| R5 | **从交互选择运动。** tab 或 segment 原地切换 → `instant` 或 `dissolve` 0–120ms `easeOut`；前进到详情屏幕 → `slideIn` 或 `push` 方向 `left` 260–320ms `easeInOut`；返回上一屏幕 → `back` 或镜像方向 240–300ms `easeInOut`；底部 sheet 或 modal 打开 → `moveIn` 方向 `bottom` 220–280ms `easeOut`；sheet 或 modal 关闭 → `moveOut` 方向 `bottom` 180–240ms `easeIn`；元素在状态间形变 → `smartAnimate` 240–320ms `easeInOut` 或 `gentle`；俏皮儿童确认 → `smartAnimate` 300–420ms `bouncy` 或 `easeOutBack`；toast 或 alert 自动关闭 → `dissolve` on `afterDelay` 160–240ms `easeOut`。 | 运动选择符合交互类型；持续时间/缓动符合指导；非常规运动 ≤ ~400ms。 |
| R6 | **默认不使用 `smartAnimate`。** `smartAnimate` 只在某物真正跨两帧持续时才值得其成本。 | `smartAnimate` 仅在图层名称/层级/类型一致且有内容跨帧持续时使用。 |
| R7 | **Smart Animate 配对。** `smartAnimate` 跨源和目标帧配对图层并动画差异。要使配对被找到，保持图层在两帧中相同：同名、层级中同位置、同类型。只改变应移动的（位置、大小、填充、不透明度、圆角）。配对行为在无头会话中不可观察——将其视为手动检查并告知用户要观看哪些过渡。 | 源/目标帧图层名称/层级/类型一致；配对检查列为手动检查项。 |
| R8 | **分阶段序列。** 对于庆祝或入门节拍，在过渡帧间链接 `afterDelay` 交互，而不是试图在一个过渡中错开多个元素。保持链条简短，给用户即时退出方式，不要将用户困在无控定时序列中。 | 分阶段序列使用 `afterDelay` 链条；链条简短；用户提供即时退出方式。 |
| R9 | **克制。** 动画传达：层级、来源、方向、状态变化、进度。每个交互一个主要运动——竞争性动画读起来像噪音。保持同一旅程一致——如果前进向左滑，到处都向左滑。尊重设计的性情——俏皮儿童应用可以弹跳；银行确认不应弹跳。需要减少运动的用户存在——如果产品有该要求，询问是否提供 instant 或 dissolve 变体而非发明。不要添加 brief 从未提及的运动。 | 运动传达层级/来源/方向/状态变化/进度；每个交互一个主要运动；旅程一致；尊重设计性情；未添加 brief 未提及的运动。 |
| R10 | **验证。** 1) 检查交互并确认 `transition`、`durationMs`、`easing` 和任何 `delayMs` 按预期存储——这些字段由 `inspect_document` 和 `get_node` 报告。2) 走图并确认前进和返回运动相互镜像，每个 overlay 的打开和关闭对互补。3) 确认在重新定时期间没有必需交互丢失其 action。4) 播放不能从该工具集自动化——列出用户应在预览中运行的移动检查，命名每个过渡，不要称之为已验证。报告应用的移动模型、选择的持续时间和缓动、任何不寻常的推理，以及仍需人眼的配对检查。 | 交互字段已通过 `inspect_document`/`get_node` 验证；前进/返回镜像；overlay 打开/关闭互补；无必需交互丢失；已列出预览手动检查项。 |

## Routing

| Step | File | Purpose |
|------|------|---------|
| 1 | figcraft-motion/SKILL.md | 本技能概览与规则。 |
| 2 | figcraft/SKILL.md | FigCraft 协调器：intake、scope、完成规则。 |
| 3 | figcraft-prototyper/SKILL.md | Prototyper 子技能：交互接线与验证（Motion 的前置条件）。 |
