---
name: media-acquisition
description: Download music lists to a local MP3 library via mdl.
when-to-use: "Use when the user wants to download songs to a local MP3 music library, build/replenish a music library from a named list, or acquire media assets from external sources."
argument-hint: "<song-list | songs...> [--out-dir DIR] [--format mp3|m4a|opus|flac|wav] [--bitrate 128K..320K|best]"
---

# Media Asset Acquisition

Acquire media assets from external sources into a local library, resolving target URLs and downloading audio formats through command line utilities.

## Rules

| ID | Rule | Check |
|----|------|-------|
| R1 | Resolve all items to concrete track or playlist URLs before invoking download tools. | Check that URL parameters are fully qualified before running downloader. |
| R2 | Execute one tool invocation per collected item; never concatenate multiple URLs into a single run. | Confirm download processes are invoked individually per media item. |
| R3 | Verify query resolution on initial items before dispatching large batch operations. | Test output of first query to ensure endpoint returns valid metadata. |
| R4 | Resolve CLI binary paths explicitly through npm root resolution if not directly present in system PATH. | Verify binary location via `npm root -g` if command is not found. |

## Routing

| Step | Reference | Purpose |
| ---- | --------- | ------- |
| Music download | [`references/music-download.md`](references/music-download.md) | Song-list collection, YouTube Music URL resolution, mdl batch loop, flat-output layout, pitfalls. |
| mdl command reference | [`references/mdl-reference.md`](references/mdl-reference.md) | Condensed mdl CLI flags, provider URL formats, completion checks. |
