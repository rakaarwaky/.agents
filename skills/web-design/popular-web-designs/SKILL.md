---
name: popular-web-designs
description: 54 real design systems (Stripe, Linear, Vercel) as HTML/CSS.
when-to-use: "Use when the user wants a page styled like a known site — 'build a page that looks like Stripe/Linear/Vercel', a landing page, dashboard, or UI using a real design system's tokens and components."
argument-hint: "<site> [output.html]"
---

# Popular Web Designs

Apply 54 real-world design systems captured as HTML/CSS templates, mapping complete visual vocabularies, typography stacks, spacing rules, and CSS custom property tokens.

## Rules

| ID | Rule | Check |
|----|------|-------|
| R1 | Pair this skill with a dedicated design-process skill for scoping and variant exploration; use this skill for visual tokens. | Verify design system selection matches user aesthetic requirements. |
| R2 | Generate single-file HTML outputs wiring CSS custom properties directly to the chosen template's design tokens. | Inspect generated HTML for `:root` custom properties matching the design system. |
| R3 | Apply designated Google Fonts CDN substitutes closely matching original proprietary font weights and letter spacing. | Verify Google Fonts `<link>` tag and font-family declarations in output HTML. |
| R4 | Validate rendered HTML artifacts against template specifications for color contrast, spacing, and component fidelity. | Confirm visual accuracy and styling consistency with reference template. |

## Routing

| Step | Reference | Purpose |
| ---- | --------- | ------- |
| 1. Pick a design | [`references/catalog.md`](references/catalog.md) | Full catalog of 54 templates grouped by category, plus Choosing a Design heuristics. |
| 2. Generate HTML | [`references/html-pattern.md`](references/html-pattern.md) | Skeleton HTML with CSS custom properties wired to template design tokens. |
| Font mapping | [`references/font-substitution.md`](references/font-substitution.md) | Proprietary to CDN substitute table and zero-loss font recommendations. |
