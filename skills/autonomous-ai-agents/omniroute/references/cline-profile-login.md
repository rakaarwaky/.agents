# Cline — Per-Profile Brave Login

Connect Cline (api.cline.bot) provider accounts across Brave profiles via the OmniRoute dashboard OAuth + callback-paste flow.

## Flow

1. **Dashboard login** — `http://localhost:7777/login` with password `CHANGEME`, navigate to `/dashboard/providers/cline`.
2. **Connect button** — Click "Connect" (use `.first.click()` — two Connect buttons may exist in the dialog, causing strict mode violation). Handle consent dialog: click "I understand, continue".
3. **Auth URL** — The dialog shows an `<input>` containing the auth URL. Extract it: `https://api.cline.bot/api/v1/auth/authorize?client_type=extension&callback_url=http%3A%2F%2Flocalhost%3A7777%2Fcallback`.
4. **Launch Brave** — Start Brave with the target profile's `--profile-directory` and `--remote-debugging-port=9333`. Inject `DISPLAY=:1` into env.
5. **AuthKit sign-in** — The auth URL redirects to `authkit.cline.bot` (AuthKit hosted sign-in page). **"Continue with Google" is a `<a>` link**, NOT a button. Use `page.get_by_role("link", name=re.compile(r"continue with google", re.IGNORECASE))`. A button locator matches zero elements and the loop spins silently.
6. **Google sign-in** — Google OAuth opens (`accounts.google.com`). Select the profile email in account chooser (may be in Indonesian: "Login - Akun Google"). Fill email form if shown. Handle multilingual consent (Continue/Allow/Lanjutkan/Setuju/Izinkan).
7. **Redirect chain** — After Google login: `accounts.google.com` → `api.cline.bot/api/v1/auth/callback` → `localhost:7777/callback?code=...&state=...`. The script must keep polling until the final `localhost:7777/callback` URL is captured. Do NOT stop at `api.cline.bot` — that is an intermediate redirect.
8. **Callback paste** — Submit the captured callback URL back to the dashboard dialog's second input and click Connect to complete registration.
9. **Database verification** — `SELECT email FROM provider_connections WHERE provider='cline' AND is_active=1`.

## Pitfalls

- **Link vs button**: The single biggest trap. AuthKit's "Continue with Google" is an `<a>`, not a `<button>`. A `get_by_role("button", ...)` locator silently matches nothing and the automation loops forever. Always inspect `get_by_role("link")` and `get_by_role("button")` separately before scripting.
- **Strict mode violation**: `get_by_role("button", name=re.compile(r"^connect$"))` can match multiple elements. Always use `.first.click()`.
- **Intermediate redirect**: `api.cline.bot/api/v1/auth/callback` is NOT the final callback. The chain continues to `localhost:7777/callback?code=...`. Stopping at `api.cline.bot` means the callback URL is never captured.
- **DISPLAY**: Brave requires `DISPLAY=:1` on this host. Terminal sessions don't inherit it.
- **Dashboard modal must stay open**: Same as Kilo Code — closing the modal early breaks the backend poller.

## Driver

Module: `modules/omniroute/src/capabilities_cline_omniroute.py`

CLI: `baa omni cline [profile_name]`
