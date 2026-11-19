---
name: visual-acceptance
description: Pre-delivery acceptance recipe for paper figures — live-page screenshots, tiling self-check, vision-judge dispatch templates, and evidence-driven fix discipline.
when-to-use: Use as the pre-delivery acceptance recipe for paper figures, including live-page screenshots, tiling self-check, vision-judge dispatch templates, and evidence-driven fix discipline.
argument-hint: '<复制品路径|参考图路径>'
---

# Visual acceptance loop

Delivery standard is not "looks fine to me" — it is an **independent vision judge** comparing render vs reference at pixel level and returning PASS.

## Rules

| ID | Rule | Check |
|----|------|-------|
| R1 | **活页面必须截图。** 导出 PNG 有盲点（它们绕过屏幕布局/缩放；fit-to-view 白屏 bug 只在活页面上显示）。将视口设置为用户式窗口，截图，并输出图像供检查。 | 已对活页面截图；未使用导出 PNG 替代活页面截图。 |
| R2 | **导出自检：平铺。** 运行 `check_tiling.py`（本文件夹）——半图差异接近零意味着捕获平铺。仅检查文件大小无法捕获它。修复后重新导出时，**在编辑后重建内联导出页**（反向顺序会将陈旧版本嵌入页面）。 | 已运行 `check_tiling.py`；半图差异接近零或已修正；重新导出时已在编辑后重建内联导出页。 |
| R3 | **视觉裁判比较。** 使用复制品路径 + 参考路径 + 标准 + 有意的偏差列表进行分派。没有位图参考的新鲜图获得标准 + 元素清单；声明样式合同，以便品味差异不被标记为缺陷。 | 已分派视觉裁判（复制品 + 参考 + 标准 + 有意偏差）；无参考图时已声明样式合同；品味差异未标记为缺陷。 |
| R4 | **裁判分派模板。** 模板结构：`You are the visual acceptance gate ... Compare REPLICA vs REFERENCE:` 包含 `replica: <absolute path.png>`（注意坐标系/比例因子）、`reference: <absolute path.png>`、`## What the figure is`（元素清单/拓扑）、`## Acceptance bar`（结构-语义保真 + 每个字符串 + 箭头源→目标拓扑 + 无溢出/重叠/断线；明确列出有意偏差）、`## Your job`（每项清单：文本/拓扑/颜色/质量；"pixel measurements beat impressions"）。返回每页一条 JSON 判定行：`{"page":"...","verdict":"PASS"|"FAIL","issues":[{"severity":"major"|"minor","what":"...","where":"...","evidence":"..."}]}`。批量每裁判 3–4 图，多个裁判并行。重新检查是针对性的：仅先前 FAIL + 回归点，从不完全重新运行。 | 已使用裁判分派模板；批量 3–4 图/裁判；多个裁判并行；重新检查仅先前 FAIL + 回归点。 |
| R5 | **修复纪律。** 从裁判的像素证据修复**根本原因**，而非临时补丁（真实例子：标题变黑 → 根本原因是 CSS 覆盖 SVG 表示属性；框偏差 33 px → 真位置从对齐关系恢复）。修复后，分派针对性重新检查。如果 PASS 但仍有小问题，决定是否打磨到零（当用户关心细节时）。用户标记的缺陷遵循相同循环：量化 → 修复根本原因 → 裁判重新检查。 | 已修复根本原因；已分派针对性重新检查；PASS 后小问题已打磨或报告；用户缺陷已量化/修复/重新检查。 |
| R6 | **浏览器自动化：新内核。** 每个 JS 调用都是新内核：重新引导、列出标签、绑定已验证 id——永不重用陈旧句柄。 | 每个 JS 调用都是新内核；已重新引导/列出/绑定已验证 id；未重用陈旧句柄。 |
| R7 | **浏览器自动化：缓存清理。** 使用 `?v=<timestamp>` 缓存清理重载。 | 已使用 `?v=<timestamp>` 缓存清理重载。 |
| R8 | **浏览器自动化：截图失败。** 偶发截图失败（"activity capture failed"）→ 等待 1s 并重试；优先使用精确内容尺寸视口 + 普通截图而非巨大视口。 | 偶发截图失败时已等待 1s 重试；已使用精确内容尺寸视口 + 普通截图。 |
| R9 | **浏览器自动化：绝不信任 `fullPage: true`。** 在超过一屏的页面上**绝不相信 `screenshot({fullPage: true})`**。即使视口正确，它也可能拼接视口大小的块，重复页面——一个正确尺寸的 PNG 其内容是 4 份副本（真实案例，在应用内浏览器中）。通过 `evaluate` 测量 `scrollWidth`/`scrollHeight`，将视口设置到确切尺寸（上限 3840×2160），并采取无裁剪的普通截图。始终用 `check_tiling.py` 重新验证。 | 未使用 `screenshot({fullPage: true})`；已通过 `evaluate` 测量 `scrollWidth`/`scrollHeight`；视口设置为确切尺寸（≤3840×2160）；无裁剪普通截图；已用 `check_tiling.py` 重新验证。 |
| R10 | **暗色主题对比度：细线。** **1.2 px 细线因抗锯齿失去约 60% 理论对比度。** 暗色主题表格网格在 `#111a2e` 上绘制 `#22304d`（理论 Δ≈50）渲染为 Δ≤12，裁判读为"无边框"——用了两轮修复（`#33507a` 仍 Δ12–22 渲染，`#6288b8` → 渲染 Δ27–43，线像素 53–69）才通过。规则：按**渲染像素测量**而非 hex 数学选择线/文本颜色——扫描导出 PNG 并在实际背景上要求正文文本和网格线 ≥40 灰度级差异。在裁判之前自行扫描（在预期线 x 位置处一次 `PIL/numpy` 列最小扫描）。 | 暗色主题线/文本颜色已按渲染像素测量选择；导出 PNG 在实际背景上显示 ≥40 灰度级差异；已用 PIL/numpy 列最小扫描。 |

## Routing

| Step | File | Purpose |
|------|------|---------|
| 1 | `check_tiling.py` | 重复平铺的启发式检查：比较半图差异，接近零意味着捕获平铺。 |
| 2 | SKILL.md | 本技能概览与规则。 |
