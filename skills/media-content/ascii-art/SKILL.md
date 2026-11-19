---
name: ascii-art
description: "ASCII art: text banners (pyfiglet), cowsay, boxes, image-to-ascii, QR codes, weather art."
when-to-use: "Use when the user wants ASCII art — text banners, character speech bubbles (cowsay), decorative borders (boxes), colored text (toilet), image-to-ASCII conversion, QR codes, weather art, or pre-made ASCII art from the web."
argument-hint: "[banner|cowsay|boxes|toilet|image-to-ascii|qr|weather|search] <text|image> [font|--flag]"
---

# ASCII Art

Select and execute local CLI tools or free REST APIs for ASCII art generation, including banners, speech bubbles, decorative boxes, image conversions, and QR codes without API keys.

## Rules

| ID | Rule | Check |
|----|------|-------|
| R1 | Select default tools according to need decision flow: prefer pyfiglet before external APIs, and install missing CLI tools before falling back. | Check chosen CLI tool against task recommendation in decision tree. |
| R2 | Constrain rendered text output to a maximum width of 60 characters per line in monospace format. | Measure line lengths of generated output to ensure terminal compatibility. |
| R3 | Preserve original artist signatures and initials when retrieving pre-made ASCII art from the web. | Inspect retrieved artwork to confirm artist attribution remains intact. |
| R4 | Verify completion by rendering output cleanly in a monospace terminal context at or under 60 columns. | Test output display in fixed-width terminal buffer. |

## Routing

| Step | Reference | Purpose |
| ---- | --------- | ------- |
| Need -> tool decision | [`references/decision-flow.md`](references/decision-flow.md) | One entry per ASCII-art need; end state: the tool + command is chosen. |
| Per-tool setup and usage | [`references/tools.md`](references/tools.md) | pyfiglet/asciified, cowsay, boxes, toilet, image-to-ASCII, pre-made art search, QR/weather, LLM-generated fallback palettes. |
