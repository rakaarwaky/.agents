# Connect Antigravity (agy) accounts from Brave profiles

Batch-register per-profile Google sessions as Antigravity CLI provider connections in
OmniRoute (dashboard `http://127.0.0.1:7777/dashboard/providers/agy`).

## Prerequisites
- OmniRoute daemon up on 7777; dashboard password known (default `CHANGEME` unless
  `INITIAL_PASSWORD` was set — the bcrypt hash lives in `storage.sqlite` `key_value`
  namespace `settings` key `password`).
- baa profiles provisioned (`baa profile list` shows every target profile).
- Brave binary resolved by baa (native: `/opt/brave.com/brave-origin/brave`).
- Check who is already connected: `SELECT email FROM provider_connections WHERE provider='agy'`
  in `~/.omniroute/storage.sqlite` — skip those rows in the batch.

## Flow per profile
1. Dashboard: log in (password input + Continue) → open `/dashboard/providers/agy` →
   click **Add** → ToS warning dialog: check **Don't show this again** (flag is NOT
   persisted across dashboard sessions; expect it every session) → **I understand, continue**.
2. Connect dialog: click **Popup blocked? Enter URL manually** → two text inputs appear:
   input[0] = fresh Google OAuth URL (new `state` per Add click — use it exactly once),
   input[1] = paste target. Keep the dialog open.
3. Launch the target profile with CDP (main Brave must be closed first — it owns the
   user-data-dir singleton; `pkill -f 'brave-orig[i]n'` then):
   `/opt/brave.com/brave-origin/brave --user-data-dir=~/.config/BraveSoftware/Brave-Origin \
   --profile-directory=<prof> --remote-debugging-port=9333 --no-first-run \
   --no-default-browser-check --disable-blink-features=AutomationControlled about:blank`
   then Playwright `connect_over_cdp(http://127.0.0.1:9333)`, new page.
4. Open `<auth_url>&hl=en` (force English UI — profiles may be Indonesian and button
   names won't match). Handle the screens in order (all load content lazily, 30-60s of
   spinner is normal; keep polling, do not give up early):
   - **accountchooser**: account rows appear late; wait for the row showing the profile's
     email (`get_by_text(email)`), click it.
   - **nativeapp warning** (`.../oauth/v3/firstparty/nativeapp`, h1 "Make sure that you
     downloaded this app from Google"): click **Sign in**.
   - **consent** (`requestPath=/signin/oauth/v3/consent`): click **Agree and continue**
     (fallback names: Continue / Allow / Indonesian Setuju dan lanjutkan / Lanjutkan).
   - **identifier** (`.../signin/identifier`) — only when the profile has NO Google
     session: type the email, click Next; then on the password screen type the profile's
     password. Credentials come from `profile.csv` (username/password columns); the
     driver types them, the user never types them into chat.
5. Redirect lands on `http://127.0.0.1:7777/callback?code=...&state=...` — capture the
   page URL from the profile browser itself.
6. Close the profile browser gracefully (`Browser.close` CDP command so cookies flush),
   paste the callback URL into input[1] → **Connect** → dialog closes; verify the page
   shows N+1 connections.
7. Loop over all profiles. Brave is left closed at the end; user reopens it normally
   (sessions restore).

## Security checks (captcha / 2FA)
Some profiles are not Google-logged-in (show `signin/identifier`) or trigger
`signin/challenge` (captcha/2FA). Use the interactive variant: it auto-types the
identifier + password from `profile.csv`, waits up to 15 min while the user clears the
captcha/2FA in the visible Brave window, then captures the callback and connects. One
profile at a time; the user's eyes are on the screen the whole time.

## Pitfalls
- The auth URL's `state` is one-shot per Add click: never reuse a stale URL.
- Google's account/consent screens can take 30-60s of spinner before content renders;
  do NOT treat "no button yet" as failure — keep polling.
- A `code=` without redirect means the Google flow hit a challenge (2FA/unusual
  activity): stop that profile, surface it to the user, do not retry blindly.
- **Captcha/2FA is user-handled, never agent-handled.** Launch the profile's window on
  the user's display, tell them which profile needs it; they complete it in the window
  while the driver keeps polling (bounded wait ~15 min). The moment Google redirects,
  the callback is captured and the connection finishes automatically. A
  `TargetClosedError` on `wait_for_timeout` mid-flow usually means a security screen
  closed the browser target: treat it as "needs assisted re-run", not as a batch bug.
- After the batch, check `provider_connections` for duplicate emails (re-connecting an
  already-connected account creates a duplicate row).

Working scripts: `agy_connect_one.py` (auto path) + `agy_batch.py` (loop) +
`agy_interactive.py` (assisted path: auto-types identifier/password from profile.csv,
waits for the user to clear captcha/2FA, then captures the callback). Copies live under
the agent scratch dir; regenerate from this procedure if missing.
