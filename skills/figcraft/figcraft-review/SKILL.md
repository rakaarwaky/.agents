---
name: figcraft-review
description: Reviews native FigCraft files for structure, auto layout, visual consistency, accessibility, reference coverage, and prototype correctness. Produces a concise scorecard plus a pass/fail interaction gate grounded in inspected layers and preview evidence.
when-to-use: Use when reviewing native FigCraft files for structure, auto layout, visual consistency, accessibility, reference coverage, and prototype correctness, producing a concise scorecard plus a pass/fail interaction gate.
argument-hint: '<.figcraft 文件路径>'
---

# FigCraft Review

Audit the actual `.figcraft` document, not screenshots alone. Inspect every in-scope page, screen, state, overlay, and prototype path. Use `list_commands` before remediation so fixes follow the current FigCraft schema.

Load the `figcraft` coordinator for the shared terms and completion rules.

## Rules

| ID | Rule | Check |
|----|------|-------|
| R1 | **Design Quality Score: Structure & Auto Layout (40).** Auto-layout adoption 15：重复区域、控件、卡片、标签和列表使用稳定布局而非脆弱绝对定位。Semantic naming 15：图层使用 `Screen/Home`、`Card/Article`、`Button/Continue` 等名称，而非默认如 `Frame 45`。Hierarchy & clipping 10：嵌套、父子关系、尺寸、约束、裁剪和滚动是刻意的。 | 已计算 Structure & Auto Layout 得分；每个扣分项有 layer name/id 与具体修复。 |
| R2 | **Design Quality Score: Tokens & Visual Consistency (30).** Color roles 10：表面、文本、强调、边框和状态与参考或批准系统一致。Spacing & sizing 10：等价元素使用一致间距和尺寸比例——不要强制与参考冲突的网格。Typography, radius, & effects 10：等价层级和组件状态保持一致。 | 已计算 Tokens & Visual Consistency 得分；每个扣分项有 layer name/id 与具体修复。 |
| R3 | **Design Quality Score: Accessibility & Usability (30).** Target size 15：使用目标平台标准。Apple 接口至少 44×44 pt。如果审查 WCAG 2.2 AA，评估 2.5.8 的 24×24 CSS px 最小值及其例外；44×44 CSS px 属于增强 AAA 标准 2.5.5。Contrast & readability 10：目标至少 4.5:1 普通文本和 3:1 大字文本，除非批准标准不同。Text resizing & overflow 5：换行、自动调整大小、最大行数、裁剪和截断是刻意的。 | 已计算 Accessibility & Usability 得分；每个扣分项有 layer name/id 与具体修复。 |
| R4 | **Reference Coverage Gate.** 当提供参考时，验证：每个参考映射到实现的 screen/state/overlay/responsive size；层级、copy、关键资产和构图匹配；与源差异已批准、必需或明确报告；多个参考未折叠成一个 screen 或扩展成未请求页面。结果：`PASS`、`FAIL` 或 `NOT APPLICABLE`。 | 每个参考映射到实现的 screen/state/overlay；层级/copy/资产/构图匹配；差异已批准或报告；未折叠或扩展。 |
| R5 | **Asset, Type & Size Gate.** 检查：screens 使用真实设备预设（来自 `frame.presets`）或用户指定尺寸；响应式变体（当请求时）各自来自自己的预设并保持图层名称对齐；插图和角色是真实矢量 artwork，而非堆叠模拟曲线的原始形状，且编写 artwork 被报告为解释而非复刻；界面图标来自一个图标集，具有一致重量、大小框和颜色角色，且无图标框架因失败获取而为空；携带状态的图标（如选中 vs 未选中）按参考显示方式不同；提供的资产已导入而非重绘；导入 SVG 图层已从 `Group` 和 `Vector` 重命名，且 `currentColor` 黑色已重新着色；`text.missingFonts` 为空，或每个剩余条目都有原因报告；无字体被静默替换，意味着字体 `warnings` 已解决或报告；文本角色遵循一个比例而非每层临时尺寸。结果：`PASS`、`FAIL` 或 `NOT APPLICABLE`。 | screens 使用真实预设；响应式变体对齐；插图/角色为真实矢量；图标来自一个集合并一致；资产已导入；SVG 已重命名/重新着色；`text.missingFonts` 为空或已报告；字体未静默替换；文本角色一致。 |
| R6 | **Prototype Correctness Gate.** 保持为 100 分视觉分数之外的 pass/fail 门禁。一个光鲜但行为破碎的设计不得获得无条件批准。检查：预期流程有有效起始框架；每个必需按钮/CTA 有预期 action；所有导航目的地存在且必需屏幕可达；滑块 viewport、轨道大小、overflow 方向、裁剪和拖动行为正确（通过比较轨道和 viewport 尺寸检查，因为 `overflow` 不被检查报告）；overlay 在预期位置打开且有必需关闭/关闭路径；back action 返回预期状态；警报有正确触发器、action、关闭和终止状态；组件变体、变量和条件到达预期状态，且每个 `changeTo` 目的地是同一组件集的真实变体而非普通框架；热区与最终可见控件对齐、满足目标大小且不重叠无关控件；无过期 ID、孤儿目的地、重复交互或不可达必需状态；当实现仅模拟输入状态时，不声称可编辑输入；运动按旅程一致，退出不比进入慢，常规不超过约 400ms，且 `smartAnimate` 配对跨帧名称和嵌套相同；交互判定引用检查结果——成功的 `proto.preview` 调用不作为运行时证据接受，剩余点击检查列给用户。结果：`PASS`、`FAIL` 或 `NOT APPLICABLE`。 | 起始框架有效；CTA 有 action；目的地可达；滑块尺寸比较正确；overlay 位置/关闭正确；back 返回正确；警报完整；组件/变量/条件正确；热区对齐；无过期/孤儿/重复/不可达；未声称模拟输入；运动一致；`proto.preview` 未作为运行时证据。 |
| R7 | **工作流：检查与报告。** 1) 用 `inspect_document` 检查文档（当多页在范围内时使用 `allPages: true`）；2) 用 `get_node` 检查截断或交互重的子树；3) 渲染临时截图用于所有相关 screen 和 overlay；4) 将结果与参考清单或批准需求比较；5) 检查交互数组、组件、变量、目的地和流程起始点——`overflow` 不被检查报告，因此通过比较轨道和 viewport 尺寸或读取保存的文档判断滚动；6) 检查资产和类型：确认屏幕尺寸与 `frame.presets` 对比，运行 `text.missingFonts`，并检查图标和插图框架是否有真实矢量子节点而非空或占位层；7) 手动跟踪报告的交互图——播放不可从该工具集观察：在无头会话中 `proto.preview` 和 `proto.present` 成功但不产生窗口，且 `pointer` 驱动画布而非播放器——列出用户必须运行的点击检查而非称之为已验证；8) 仅在批准修复后保存。保存后再次检查。当修复改变视觉方向、信息架构、导航、内容或产品行为时，不要未经用户批准应用修复。安全机械修复可单独提供。 | 已用 `inspect_document`/`get_node` 检查；已渲染临时截图；已与参考比较；已检查交互/组件/变量/目的地/起始点；已比较轨道/viewport；已运行 `text.missingFonts`；已手动跟踪交互图；仅在批准修复后保存并再次检查。 |
| R8 | **报告格式。** 使用以下格式报告：`# FigCraft Review`、**File:** `ui.figcraft`、**Design score:** 88 / 100、**Reference coverage:** PASS、**Assets, type & size:** FAIL、**Prototype correctness:** FAIL；Design Quality Score 表（Dimension、Score、Main issue）；Blocking findings（编号列表，每条有 layer name/id 与具体修复）；Other findings；Verification limits。当 `proto.preview` 交互不可自动化时，说明手动检查而非称门禁完全验证。 | 报告包含：File、Design score、Reference coverage、Assets/type/size、Prototype correctness、Design Quality Score 表、Blocking findings、Other findings、Verification limits；手动检查已列出。 |

## Routing

| Step | File | Purpose |
|------|------|---------|
| 1 | figcraft-review/SKILL.md | 本技能概览与规则。 |
| 2 | figcraft/SKILL.md | FigCraft 协调器：intake、scope、完成规则。 |
| 3 | figcraft-builder/SKILL.md | Builder 子技能：屏幕、组件与布局构建。 |
| 4 | figcraft-icons/SKILL.md | Icons 子技能：界面图标映射与导入。 |
| 5 | figcraft-svg/SKILL.md | SVG 子技能：插图、角色、徽标与有机 artwork。 |
| 6 | figcraft-typography/SKILL.md | Typography 子技能：字体选择与安装。 |
| 7 | figcraft-prototyper/SKILL.md | Prototyper 子技能：交互接线与验证。 |
| 8 | figcraft-motion/SKILL.md | Motion 子技能：在原型正确后添加过渡与动画。 |
