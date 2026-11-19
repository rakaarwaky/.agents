---
name: parametric-diagram
description: Draw editable structure diagrams from scratch as a parametric Python script — geometry/topology/style declared in three blocks; re-run to regenerate the SVG. The script is the single source of truth.
when-to-use: Use when drawing an editable structure diagram from scratch (not replicating a bitmap) that you expect to revise — add nodes, recolor, reword, reuse in the next paper — using a parametric Python script with geometry/topology/style declared in three blocks.
argument-hint: '<图型描述|主题>'
---

# Parametric diagram scripts (script = source of truth)

Draw editable structure diagrams from scratch as a parametric Python script — geometry/topology/style declared in three blocks; re-run to regenerate the SVG. For one-shot figures, hand-svg-structure is fine.

## Rules

| ID | Rule | Check |
|----|------|-------|
| R1 | **声明块：几何。** `COLS = {...}` — 列/中心/半径/行 ys（或框 x,y,w,h）。 | `COLS` 声明了列/中心/半径/行 ys（或框 x,y,w,h）。 |
| R2 | **声明块：内容。** `NODE_TEXT = {...}` — 每节点文本（主字母、下标、下斜体？）。 | `NODE_TEXT` 声明了每节点文本（主字母、下标、下斜体？）。 |
| R3 | **声明块：样式。** `STYLE = {...}` — 调色板/线宽/字体大小/家族，一处。 | `STYLE` 声明了调色板/线宽/字体大小/家族。 |
| R4 | **拓扑函数。** `def mesh(): ...` — 循环生成边（全连接/拉链链/树）。 | `mesh()` 函数生成边（全连接/拉链链/树）。 |
| R5 | **构建函数。** `def build(): ...` — 组装 SVG 字符串并写入磁盘。 | `build()` 组装 SVG 并写入磁盘。 |
| R6 | **添加节点。** 添加节点 = `COLS["ys"]` 中一条条目 + `NODE_TEXT` 中一行。 | 添加节点只需 `COLS["ys"]` 一条目 + `NODE_TEXT` 一行。 |
| R7 | **重新着色。** 重新着色 = `STYLE`。然后 `python make_fig.py` 重新生成 SVG；通过 `hand-svg-structure` 导出页导出 PNG。 | 重新着色只需修改 `STYLE`；`make_fig.py` 重新生成 SVG；PNG 通过 `hand-svg-structure` 导出页导出。 |
| R8 | **连接器端点。** 从声明的常量计算连接器端点（中心 ± 半径）——不要散落的魔法数字。 | 连接器端点从 `COLS` 声明常量计算；无散落魔法数字。 |
| R9 | **箭头标记。** `markerUnits="userSpaceOnUse"` + `orient="auto"`，线端回拉 1.5–2 px，使尖端触及目标边缘。 | 箭头标记使用 `markerUnits="userSpaceOnUse"` 和 `orient="auto"`；线端回拉 1.5–2 px。 |
| R10 | **收敛/全连接图的落地。** 将所有进入边结束在目标的**左极** `(cx-(r+2), cy)`，使箭头以簇状堆叠（径向落地读起来与经典参考"错误"）。 | 进入边结束在目标圆的左极 `(cx-(r+2), cy)`；箭头以簇状堆叠。 |
| R11 | **下标状态。** 主字母为斜体衬线；数字下标显式正体（tspan 继承斜体）；字母下标斜体。 | 主字母斜体衬线；数字下标显式 `font-style="normal"`；字母下标斜体。 |
| R12 | **字体分配。** 中文层/区域标签使用黑体（hei-ti）字体；节点内数学使用 Times。 | 中文层/区域标签使用 hei-ti；节点内数学使用 Times。 |

## Routing

| Step | File | Purpose |
|------|------|---------|
| 1 | `make_fig.py` | 完整模式（三层全连接网络图）：三个声明块 + `mesh()` + `build()`。 |
| 2 | `examples/fig-mlp.svg` / `.png` | 三层全连接网络（x_d —W1→ h_N —W2→ f_C）：隐藏层带、堆叠箭头簇、省略号点。 |
| 3 | `examples/mlp_reference.png` | 它复刻的参考图（首次重新检查时通过视觉裁判）。 |
| 4 | SKILL.md | 本技能概览。 |
