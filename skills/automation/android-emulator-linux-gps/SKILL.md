---
name: android-emulator-linux-gps
description: Use when running or installing Android apps on a Linux host with the AOSP emulator and spoofing GPS via adb emu geo fix, including AVD setup, x86 image ABI selection, and apkpure/apkcombo APK retrieval.
when-to-use: Use when the user wants the Android emulator on Linux, Deepin or X11 hosts, an AVD that boots headlessly, 32-bit ARM APK installation, Android GPS spoofing or mock location, or apkpure/apkcombo APK downloads without browser automation.
argument-hint: "<emulator | avd | gps | apk> [options] | <freeform task>"
---

# Android emulator on Linux + GPS spoofing

Run or install Android applications on a Linux host using the AOSP emulator, configure headless AVDs, handle 32-bit ARM translation on x86 system images, retrieve APKs directly, and spoof GPS coordinates reliably.

## Rules

| ID | Rule | Check |
|----|------|-------|
| R1 | Prefer AOSP emulator over Waydroid for host GPS hooks and X11/Deepin compatibility. | Verify emulator is used instead of Waydroid on X11 hosts. |
| R2 | Relocate AVDs to `~/.android/avd` and configure `disk.dataPartition.path` to persist userdata across reboots. | Inspect `~/.android/avd` and check `config.ini` for `disk.dataPartition.path`. |
| R3 | Use 32-bit x86 system images (`google_apis;x86`) when running 32-bit ARM APKs to avoid ABI install failures. | Run `unzip -l` on APK native libs and confirm image ABI supports target architecture. |
| R4 | Retrieve APKs directly from apkpure/apkcombo endpoints bypassing Cloudflare using browser user-agents. | Verify direct download endpoints return APK/XAPK packages without browser automation. |
| R5 | Use `adb emu geo fix <lon> <lat>` with longitude first and repeat every 2 seconds while location is requested. | Check `dumpsys location` for active mock location update and provider status. |

## Routing

| Reference | Purpose |
|-----------|---------|
| [`references/apk-retrieval.md`](references/apk-retrieval.md) | Getting APKs from apkpure/apkcombo without Cloudflare |
| [`references/avd-and-abi.md`](references/avd-and-abi.md) | AVD path setup and ARM/x86 ABI trap |
| [`references/gps-spoof.md`](references/gps-spoof.md) | GPS spoofing mechanisms and helper scripts |
| [`references/headless-and-host.md`](references/headless-and-host.md) | Headless UI poking and Deepin host facts |
