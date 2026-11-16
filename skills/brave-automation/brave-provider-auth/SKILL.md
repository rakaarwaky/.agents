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
9. **Inspect before scripting**: Before writing click logic for a new provider, open the auth page in a visible Brave window and enumerate `get_by_role("link")` and `get_by_role("button")` separately. OAuth "Continue with X" elements are often `<a>` links, not buttons — a button locator matches zero elements and the loop spins without action. Confirm the element role matches the locator role before automating.
10. **Strict mode violations**: `get_by_role` with a name regex can match multiple elements (e.g. two "Connect" buttons in a dialog). Always use `.first.click()` to avoid `strict mode violation` errors that abort the entire run.

### Cline (`api.cline.bot`)
- **Type**: OAuth redirect + callback-paste flow.
- **AuthKit page**: Cline uses AuthKit (`authkit.cline.bot`), NOT the same UI as Kilo Code. "Continue with Google" is a `<a>` **link**, not a `<button>` — use `page.get_by_role("link", name=re.compile(r"continue with google", re.IGNORECASE))`. Clicking a button locator silently matches nothing and the script loops forever.
- **Dashboard flow**: Dashboard Connect button → consent dialog ("I understand, continue") → dialog with auth URL input → extract URL → open in Brave → after Google login, redirect chain goes `authkit.cline.bot` → `accounts.google.com` → `api.cline.bot/api/v1/auth/callback` → `localhost:7777/callback?code=...&state=...` → capture the final callback URL → paste it back into the dashboard dialog's second input and click Connect.
- **Callback URL capture**: Poll `page.url` for `localhost:7777/callback` or (`code=` AND `localhost`). Do not stop at `api.cline.bot` — that is an intermediate redirect, not the final callback.
- **Google consent**: Same multilingual consent patterns as other providers (Continue/Allow/Lanjutkan/Setuju/Izinkan).
- **Challenge handling**: Same as other providers — if Google shows reCAPTCHA/2FA/password, switch to interactive runner and wait for manual resolution.
- **Success verification**: Query `~/.omniroute/storage.sqlite` for `SELECT email FROM provider_connections WHERE provider='cline' AND is_active=1`.

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
