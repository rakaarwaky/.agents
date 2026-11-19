---
name: codex-figure-workflow
description: 使用 Codex 从项目源码或参考图完成架构图、流程图与结构图，串联 figcraft 的参数化 SVG、浏览器导出和视觉验收，并保留可重生成的源文件与案例证据。
when-to-use: 当用户要求基于真实项目源码或参考图绘制架构图、流程图、结构图，或要求用 Codex 完成 figcraft 全套结构图工作（参数化 SVG、浏览器导出、视觉验收、保留可重生成的源文件与案例证据）时使用。
argument-hint: '<目标图路径|项目源码路径|参考图路径>'
---

# Codex 制图工作流

用户要求基于真实项目画架构图，或用 Codex 完成 figcraft 整套结构图工作时使用。科研图型选型或新绘制统计图可用 [paper-figure](../paper-figure/SKILL.md) 的 65 类入口；已有数据图忠实重绘仍走 `data-figures-rerender`，不套用本案例的三列布局。

先读 [Codex 完整指南](../../CODEX.md)。需要核对成品结构、尺寸和实战时，再读 [塔罗网站案例](../../examples/pony-tarot/CASE.md)。

## Rules

| ID | Rule | Check |
|----|------|-------|
| R1 | **确认图的事实来源。** 项目图读入口、模块、存储和部署配置；复刻图读参考图。写清节点、边和未实现功能，避免把设想画成已有能力。 | 图源、节点、边与未实现功能已书面核对，无凭空发明的事实。 |
| R2 | **选路线。** 原创结构图读 [parametric-diagram](../parametric-diagram/SKILL.md)；位图复刻读 [hand-svg-structure](../hand-svg-structure/SKILL.md)；网格型大图可读 [declarative-engine](../declarative-engine/SKILL.md)。共同原则见 [METHOD.md](../../METHOD.md)。 | 已按图型选择对应路线并记录所依据的共同原则。 |
| R3 | **以脚本为图源。** 内容、拓扑、几何、样式分开声明。修改声明后重生成 SVG，避免手改导出文件。把图输出放进独立目录，不混入业务代码。 | 图源为脚本/JSON；输出目录独立；导出的 SVG 未在声明外手工编辑。 |
| R4 | **预览和导出。** SVG 内联进 HTML，先检查普通窗口下的活页面。然后用精确尺寸 viewport 普通截屏；需要分片时生成上下半页，逐页截取后拼接。浏览器具体 API 以当前工具文档为准。 | 已对活页面普通窗口截图；分片拼接尺寸与 viewport 一致；未使用 fullPage。 |
| R5 | **验收。** 使用 [visual-acceptance](../visual-acceptance/SKILL.md)：文字/箭头/边界检查、平铺检测、独立视觉裁判。此步骤需要独立评审时，委派一名具备读图能力的子代理，只读图源、成品和事实依据。无委派能力则如实记录未完成独立验收。 | 已完成平铺检测与独立视觉裁判；若无法委派子代理，验收记录明确标记为未完成。 |
| R6 | **交付。** 保存 SVG、PNG、源脚本、必要导出资源和验收记录；展示结果图并链接可编辑版本。只停止自己为此次导出启动的临时服务。 | 已交付 SVG、PNG、源脚本、导出资源与验收记录；已停止自己启动的临时服务。 |
| R7 | **Codex 适配：首次浏览器调用。** 遵守该工具的初始化要求；持久会话不要照搬"每次调用都是新内核"的旧工具假设。 | 首次浏览器调用完成初始化，未复用旧内核假设。 |
| R8 | **Codex 适配：不固定环境。** 不固定浏览器 tab ID、工具名、端口或 Python 路径。先发现运行环境和 API；中文字体需要明确且可用。 | 运行环境、API 与字体在调用前已发现并声明。 |
| R9 | **Codex 适配：导出页顺序。** 导出页必须在最新 SVG 生成之后重建。截图宽高、分片范围与合成尺寸必须一致。 | 导出页在最新 SVG 生成之后重建；截图与合成尺寸一致。 |
| R10 | **Codex 适配：PNG dpi 语义。** PNG 的 600 dpi 是打印元数据，清晰度由实际像素决定；同时报告像素尺寸。 | 已同时报告 PNG 的 600 dpi 元数据与实际像素尺寸。 |
| R11 | **Codex 适配：平铺启发式。** `check_tiling.py` 是重复平铺的启发式检查，不代替人工/独立读图。 | 已运行 `check_tiling.py`，并另行安排人工/独立读图。 |
| R12 | **Codex 适配：案例约束边界。** 不把案例中的静态部署、localStorage、三列布局或 Windows 字体当成所有项目的要求。 | 案例中的部署、localStorage、布局与字体未被套用为通用要求。 |

## Routing

| Step | File | Purpose |
|------|------|---------|
| 1 | [Codex 完整指南](../../CODEX.md) | Codex 工具的初始化、环境与 API 发现规则。 |
| 2 | [塔罗网站案例](../../examples/pony-tarot/CASE.md) | 真实案例：成品结构、尺寸与实战过程核对。 |
| 3 | [parametric-diagram](../parametric-diagram/SKILL.md) | 原创结构图（从零绘制、期望反复修订）的路线。 |
| 4 | [hand-svg-structure](../hand-svg-structure/SKILL.md) | 位图复刻（静态 SVG、程序化几何探测）的路线。 |
| 5 | [declarative-engine](../declarative-engine/SKILL.md) | 网格型大图（声明式布局引擎配置）的路线。 |
| 6 | [METHOD.md](../../METHOD.md) | 三条路线的共同原则与图型方法。 |
| 7 | [visual-acceptance](../visual-acceptance/SKILL.md) | 活页面截图、平铺检测、独立视觉裁判的验收规则。 |
| 8 | [paper-figure](../paper-figure/SKILL.md) | 科研统计图 65 类图型入口（当需求不是架构图/流程图时使用）。 |
| 9 | [data-figures-rerender](../data-figures-rerender/SKILL.md) | 已有数据图的忠实重绘（当需求是数据图复刻时使用）。 |
