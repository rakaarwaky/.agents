---
name: brave-provider-auth
description: "Use when authenticating AI providers across Brave profiles."
when-to-use: "Use when automating provider sign-in (Kilo Code, Antigravity, or other OAuth/device-auth providers) across multiple Brave browser profiles, handling passkey bypass, Google OAuth selection, and security challenge coordination."
---

# Brave Provider Auth Automation

Automation recipes and operational rules for connecting third-party AI providers to the local OmniRoute gateway (`http://127.0.0.1:7777`) across isolated Brave profiles (`profile.csv`).

## Core Rules

1. **Explicit Display**: Always launch Brave with `DISPLAY=:1` (or current `$DISPLAY`). Background/daemon terminal processes default to empty `DISPLAY` and fail to acquire X11/CDP locks.
2. **Never Passkey**: On modern AI provider login surfaces (like Kilo Code / app.kilo.ai), the UI defaults to passkey prompts ("Waiting for your passkey…"). Always target "Continue with Google" or "or see other sign-in methods". Never click generic "sign in" or "continue" buttons that trigger passkeys.
3. **Handle Email Form Backtrack**: If an email/password form appears on the provider page, detect the "Back to sign in options" button and click it to recover the "Continue with Google" option.
4. **Session Cookie Injection**: Load session cookies from `~/.local/share/baa/session/{profile}_cookies.json` into the Brave CDP context before navigating. This preserves Google authentication and avoids fresh-login security challenges.
5. **Keep Dashboard Modal Open**: For device-auth flows (like Kilo Code), keep the OmniRoute dashboard browser/modal open during authorization so its backend poller can receive the token and write to `storage.sqlite`.
6. **Multilingual Consent**: Handle Google OAuth consent buttons in both English (`"Continue"`, `"Allow"`) and Indonesian (`"Lanjutkan"`, `"Setuju"`).
7. **Human-in-the-Loop for Security Challenges**:
   - Google reCAPTCHA / "Confirm you're not a robot" and phone 2FA (`challenge/dp`) cannot and must not be solved via blind click scripts.
   - Yield execution to the user with an interactive runner (`kc_interactive.py`), announce the specific challenge clearly, and poll for DB updates.
8. **Playwright Event Loop Conflict**: When mixing headless dashboard automation and CDP profile automation, reuse the existing `sync_playwright()` instance rather than calling `.start()` multiple times on the same thread. Ensure `playwright install chromium` has run in the environment.

## Provider Patterns

### Kilo Code (`app.kilo.ai`)
- **Type**: Device auth flow (`/device-auth?code=XXXX-XXXX`).
- **Dashboard Modal**: Must keep the OmniRoute dashboard browser/modal OPEN during device authorization; closing it early breaks backend token polling.
- **Session Cookie Injection**: Load session cookies from `~/.local/share/baa/session/{profile}_cookies.json` into the Brave CDP context before navigating to avoid unexpected re-authentication.
- **Initial page**: Defaults to passkey wait. Action: click `button[name*="Continue with Google"]` (if email form appears, click "Back to sign in options" first).
- **Google OAuth**: Selects profile in account chooser. Fills password from `profile.csv` if prompted.
- **Multilingual Consent**: Clicks consent button supporting both English (`"Continue"`, `"Allow"`) and Indonesian (`"Lanjutkan"`, `"Setuju"`).
- **Challenge state**: Google may prompt with `signin/challenge/recaptcha` or `signin/challenge/dp` (phone 2FA). Pause automation with interactive runner and notify user.
- **Success**: Clicks "Authorize" on Kilo Code device page, then verifies registration in `~/.omniroute/storage.sqlite`.
