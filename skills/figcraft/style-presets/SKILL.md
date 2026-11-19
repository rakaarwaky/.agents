---
name: style-presets
description: Style presets for structure figures — three token dictionaries (academic default / web / tech). Same geometry and content declaration, swap skins with zero figure-code changes. Includes a worked GPU-pipeline example that regenerates all three finishes.
when-to-use: Use when the same structural figure must ship in several looks (paper, slide deck, promo screen) and you do not want to re-draw it per style — using three token dictionaries (academic default / web / tech) with zero figure-code changes.
argument-hint: '<图型描述|主题>'
---

# Style presets (academic / web / tech)

One figure, multiple finishes: a paper-grade default, a screen-friendly web look, and a dark "tech" skin — all from the same declared geometry and content. Style lives in token dictionaries; the figure script never hardcodes a color.

## Rules

| ID | Rule | Check |
|----|------|-------|
| R1 | **三预设。** Academic (default)：White ground、restrained three-color accents、no shadows or gradients、thin strokes、small radii、Times + CJK serif/hei pairing——用于 papers、theses、formal documents。Web：Dark header band、white rounded cards、soft shadows、pill chips、YaHei/Segoe——用于 work reports、projected decks。Tech：Deep-space ground with dot grid、cyan neon accents、glow on accent elements、mono labels——用于 demos、large screens、product pages。 | 已选择 `academic`/`web`/`tech` 预设；预设视觉语言与用途匹配。 |
| R2 | **用法：导入。** `import sys; sys.path.insert(0, str(Path(__file__).resolve().parent.parent))`（包含 `style_presets.py` 的文件夹）；`from style_presets import get_style, names`。`S = get_style("academic")`（无参数调用时默认为 academic；返回你可调整的副本）；图中每个颜色/字体/圆角/效果读取 `S["..."]`——无 hex 字面量。 | 已导入 `style_presets`；`S = get_style(...)` 返回副本；图中无 hex 字面量。 |
| R3 | **CLI。** `--style academic|web|tech|all`（默认 `academic`；`all` 在一次运行中输出每个完成面）。参见 `examples/make_gpu_flow_fig.py`，它从一次声明重新生成 `examples/fig-gpu-flow-*.svg` 中的三个 GPU-pipeline 图。 | 已使用 `--style` 参数；或运行 `make_gpu_flow_fig.py` 重新生成三个 GPU-pipeline 图。 |
| R4 | **令牌合同。** `get_style()` 断言固定键集（见 `style_presets.py` 中的 `REQUIRED_KEYS`）：canvas/header（`page_bg`、`head`、`head_bg`、`head_rule`、`head_bar`、`date_style`、…），text/line（`ink`、`muted`、`faint`、`line`、`text_mid`），cards（`card`、`card_edge`、`card_r`、`fx` = none|soft|glow、`badge_bg`/`badge_fg`），accent semantics（`gpu_*`——图的主强调色），neutral semantics（`cpu_*`），fittings（`off_fill`/`off_dash`、`env_fill`/`env_fg`、`table_head`、`arrow`、`note_*`），以及 typography/radius（`font_title`、`font_body`、`font_mono`、`chip_r`）。添加预设 = 添加一个字典；图脚本永不改变。 | `style_presets.py` 中 `REQUIRED_KEYS` 固定；图中所有颜色/字体/圆角/效果均读取 `S[...]`；添加预设不改图脚本。 |
| R5 | **字体回退。** 字体使用 Latin/CJK 分裂的回退列表：academic 配对 `Times New Roman, SimHei`（标题）与 `Times New Roman, SimSun`（小注）。 | 字体回退列表用于 Latin/CJK 分裂；academic 配对 Times + SimHei/SimSun。 |
| R6 | **纪律 1：样式与几何/内容分离。** 更改皮肤不得触及坐标或文本；hex 字面量从图脚本中禁止。 | 更改皮肤不影响坐标/文本；图脚本中无 hex 字面量。 |
| R7 | **纪律 2：≤3 强调 + 中性色。** 在每个预设内保持 ≤3 强调色 + 中性色——橙色仅在 `academic` 中标记强调语义，青色仅在 `tech` 中。 | 每个预设内 ≤3 强调色 + 中性色；`academic` 中橙色标记强调；`tech` 中青色标记强调。 |
| R8 | **纪律 3：效果分级。** `academic` = `fx: none`；`web` = `soft`（低不透明度深色阴影）；`tech` = `glow`（强调色，仅强调元素）。 | 效果按预设分级：`academic` none；`web` soft；`tech` glow（仅强调元素）。 |
| R9 | **纪律 4：暗色皮肤在渲染上验证对比度。** 1.2 px 细线因抗锯齿失去约 60% 理论对比度——选择 `line`/`note_line`/文本令牌，使导出 PNG 在实际背景上显示 ≥40 灰度级差异（见 [`visual-acceptance`](../visual-acceptance/SKILL.md)，暗色主题对比度检查）。 | 已选择 `line`/`note_line`/文本令牌；导出 PNG 显示 ≥40 灰度级差异；已用 PIL/numpy 列最小扫描。 |

## Routing

| Step | File | Purpose |
|------|------|---------|
| 1 | `style_presets.py` | 令牌字典：`get_style()`、`names`、`REQUIRED_KEYS`。 |
| 2 | `examples/make_gpu_flow_fig.py` | 从一次声明重新生成三个 GPU-pipeline 图。 |
| 3 | `examples/fig-gpu-flow-*.svg` | 三种完成面的 GPU-pipeline 图（academic/web/tech）。 |
| 4 | [parametric-diagram](../parametric-diagram/SKILL.md) | 参数化脚本路线（可声明样式）。 |
| 5 | [declarative-engine](../declarative-engine/SKILL.md) | 声明式引擎路线（可声明样式）。 |
| 6 | [visual-acceptance](../visual-acceptance/SKILL.md) | 暗色主题对比度检查（渲染像素测量）。 |
| 7 | SKILL.md | 本技能概览。 |
