# Kilo Code — Per-Profile Brave Login

Connect Kilo Code (app.kilo.ai) provider accounts across Brave profiles via the OmniRoute dashboard device-auth flow.

## Flow

1. **Dashboard login** — `http://localhost:7777/login` with password `CHANGEME`, navigate to `/dashboard/providers/kilocode`.
2. **Device code** — Click "Connect" (+ "I understand, continue" if shown). Extract `https://app.kilo.ai/device-auth?code=XXXX-XXXX` from the dialog.
3. **Launch Brave** — Start Brave with the target profile's `--profile-directory` and `--remote-debugging-port=9333`. Inject `DISPLAY=:1` into env.
4. **Navigate to device URL** — Connect via CDP, open the device-auth URL.
5. **Kilo sign-in page** — The page defaults to **passkey**. Click **"Back to sign in options"** (if email form shown) or **"or see other sign-in methods"**, then click **"Continue with Google"**. Never use passkey or email/password sign-in.
6. **Turnstile** — Cloudflare Turnstile may appear. Sometimes auto-passes; otherwise user must click the checkbox manually.
7. **Google sign-in** — Google OAuth flow opens. Fill email from profile, click Next. A **recaptcha challenge** ("Confirm you're not a robot") frequently appears and requires manual resolution.
8. **Google consent** — Click "Continue" / "Allow" to grant Kilo Code access.
9. **Device approval** — Kilo redirects back to device-auth page showing success.
10. **Dashboard registration** — OmniRoute dashboard registers the connection in `storage.sqlite` `provider_connections` table.

## Pitfalls

- **Passkey trap**: The Kilo sign-in page defaults to passkey mode. The script must explicitly navigate to Google OAuth via "Continue with Google".
- **Recaptcha**: Google almost always challenges with recaptcha when signing in via Kilo OAuth. This is a manual step — script must wait (up to 15 min recommended timeout).
- **Turnstile**: Usually auto-passes but occasionally needs manual click.
- **DISPLAY**: Brave requires `DISPLAY=:1` on this host. Terminal sessions don't inherit it.
- **Playwright sync loop**: Cannot start a second `sync_playwright().start()` — reuse the instance from dashboard login for CDP connection.
- **TargetClosedError**: Import from `playwright._impl._errors`, not `playwright.sync_api`.

## Driver

Scratch driver: `/home/raka/.hermes/cache/scratch/kc_one2.py`

Usage: `python kc_one2.py <profile_name>` — connects one profile at a time.

## Database verification

```sql
SELECT email, is_active FROM provider_connections WHERE provider='kilocode';
```
