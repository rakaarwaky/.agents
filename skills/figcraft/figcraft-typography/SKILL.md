---
name: figcraft-typography
description: Chooses and installs the right typeface for a FigCraft document, including downloading free families from the Google Fonts store through font.download, and verifies that no text renders in a silent fallback.
when-to-use: Use when choosing and installing the right typeface for a FigCraft document, including downloading free families from the Google Fonts store through font.download, and verifying that no text renders in a silent fallback.
argument-hint: '<参考描述|字体需求>'
---

# FigCraft Typography

Type carries most of a reference's character. A rounded playful reference set in the default sans immediately looks wrong. This skill decides which family to use, gets it onto the machine when allowed, and proves no text fell back silently.

Load the `figcraft` coordinator for intake and scope rules.

## Rules

| ID | Rule | Check |
|----|------|-------|
| R1 | **读参考，然后提议。** 描述你实际观察到的：骨架、重量范围、对比、终端、圆度、宽度，以及字母形状是几何、无衬线、人文、圆润还是手绘。分别注明 display 与 body 使用。你不能从图片确定字体——不要声称你能。提供两三个候选并说明理由，除非另行指定，说明你将使用哪个。当用户指定字体时，使用它。 | 已描述观察到的骨架/重量/对比/终端/圆度/宽度；提供了 2-3 个候选及理由；未声称从图片确定字体。 |
| R2 | **检查已安装。** `text.fonts` 列出会话可用的每个家族。下载前搜索它；正确的家族或接近的系统等价物通常已存在。`file.fontReport` 检查文档命名的字体。`text.missingFonts` 返回文档引用但未安装的字体，并为每个提供一个 `source`（命名可获取字体的字体存储），或当无法获取时为 `null`。通过 `node.set` 或 `set_properties` 使用 `fontFamily` 应用家族，使用 `fontStyle` 应用 face。`fontStyle` 在家族的最近可用 face 上绘制，当该 face 与名称在重量或倾斜上不同时 `warnings` 报告。阅读这些 warnings；它们是你发现一个 Bold 实际是 Regular 的方式。 | 已检查 `text.fonts`；已运行 `file.fontReport`/`text.missingFonts`；已读 `warnings`；未发现静默 face 替换。 |
| R3 | **从字体存储下载。** `font.download {family}` 从字体存储获取缺失家族，字体存储是 **Google Fonts 和 Noto**，作为固定和校验和验证的文件安装到共享 Craft 字体文件夹中。它在自己的线程上运行；再次调用以读取进度。安装后，重新调整打开文档的文本以适应真实家族。两个约束你必须尊重：**下载可以关闭，且只有用户可以开启**，在 Text ▸ Missing fonts 中。当关闭时，调用被拒绝。先用 `font.downloads` 检查，它返回 `allowed` 加上本会话的下载状态。验证：stock install `{"allowed": false, "downloads": []}`。所以正确顺序是：1) `font.downloads` → 读 `allowed`；2) 如果 `allowed` 为 false，告诉用户确切的开关，或同意使用已安装家族代替——不要反复重试；3) 如果为 true，`font.download {family}`，然后轮询直到 `state` 为 `installed`；4) 重新运行 `text.missingFonts` 并确认家族已从列表消失。只有 Google Fonts 和 Noto 家族可通过此方式访问——商业或自定义字体不可用。对于这些，要求用户提供字体文件并用 `text.loadFont {path | data}` 添加它，它为会话注册文件而不安装它，并重新调整自动调整大小的文本。仅会话意味着后续会话将再次报告它缺失——告诉用户。 | 已用 `font.downloads` 检查 `allowed`；`allowed` 为 false 时已告知用户开关或同意使用已安装家族；`allowed` 为 true 时已 `font.download` 并轮询到 `installed`；已重新运行 `text.missingFonts` 确认家族消失；商业/自定义字体已用 `text.loadFont` 添加并告知仅会话。 |
| R4 | **构建小型字体系。** 定义参考实际使用的角色而非每层一个大小：display 或屏幕标题；章节标题；卡片或列表标题；正文；caption、元数据和 pill 标签。每个角色记录大小、face、行高和字距，并重用它们。当文档将被维护时创建文本样式，以便更改传播。除非参考明确不同，否则跨屏幕保持相同角色相同大小。 | 已定义 5 个角色（display/title、section heading、card/list title、body、caption/metadata/pill）；每个角色记录 size/face/line height/letter spacing；已创建文本样式。 |
| R5 | **验证无静默回退。** 交接前：`text.missingFonts` 返回空列表，或每个剩余条目都有原因报告给用户。字体设置调用的 `warnings` 已解决或报告，因此没有 face 被悄悄替换。渲染显示预期字母形状——回退通常孤立看起来合理但旁边参考明显。每个文本层属于字体系中的角色。行高和换行是刻意的，没有裁剪或截断的 copy。 | `text.missingFonts` 为空或每个条目已报告；`warnings` 已解决或报告；渲染显示预期字母形状；每个文本层属于角色；行高/换行刻意。 |
| R6 | **边界。** 不要自己启用字体下载，不要在调用被拒绝时声称家族已安装。不要悄悄将请求的家族替换为类似外观——说明替换。不要将字体文件打包或重新分发到用户仓库中。不要声称从图片识别了参考的确切字体。 | 未自己启用字体下载；未声称被拒绝的家族已安装；未悄悄替换字体；未打包字体到仓库；未声称从图片识别确切字体。 |

## Routing

| Step | File | Purpose |
|------|------|---------|
| 1 | figcraft-typography/SKILL.md | 本技能概览与规则。 |
| 2 | figcraft/SKILL.md | FigCraft 协调器：intake、scope、完成规则。 |
| 3 | figcraft-builder/SKILL.md | Builder 子技能：原生文本与布局构建。 |
| 4 | figcraft-svg/SKILL.md | SVG 子技能：插图、角色、徽标与有机 artwork（非字体）。 |
| 5 | figcraft-icons/SKILL.md | Icons 子技能：界面图标映射与导入（非字体）。 |
