# Failure Modes — Triage Guide

Every known failure mode for the ship-an-electron-app pipeline, organized by symptom. Walk through these in order when something breaks.

## How to read this guide

Each failure mode has four sections:
1. **Symptom** — what the user or developer reports
2. **Likely cause** — what's actually broken
3. **Diagnostic** — how to confirm
4. **Fix** — how to solve it

## Failure Mode 1 — Update not detected

**Symptom:** "I shipped v1.0.1 yesterday. Users on v1.0.0 aren't getting the update prompt."

### Cause A — Feed URL doesn't point at the right repo

**Diagnostic:**
- Open `electron-builder.yml` or the `build.publish` block in `package.json`.
- Confirm `provider`, `owner`, `repo` match the actual repo where releases are uploaded.
- Check the built manifest: `open dist/latest-mac.yml` after a local build. Confirm it has the right version.

**Fix:** Correct the publish config. Rebuild and republish.

### Cause B — New release isn't marked "latest"

**Diagnostic:**
```sh
curl https://api.github.com/repos/<owner>/<repo>/releases/latest
```
(Add `-H "Authorization: Bearer $GH_TOKEN"` for private repos.)

Compare the returned `tag_name` against your expected version. If mismatched, the release is probably a draft or prerelease.

**Fix:** On GitHub, edit the release → uncheck "Set as pre-release" → check "Set as latest release" → publish.

Or in your config:
```yaml
publish:
  releaseType: release
```

### Cause C — Client-side update check is throttled or cached

**Diagnostic:** electron-updater caches the last-check timestamp. Default check interval is ~1 hour.

**Fix:** Force a manual check:
```typescript
import { autoUpdater } from 'electron-updater';
ipcMain.handle('check-for-updates', () => autoUpdater.checkForUpdates());
```
Or just restart the app.

### Cause D — Asset naming mismatch

**Diagnostic:** The release must contain `latest-mac.yml`, `latest.yml`, `latest-linux.yml` files. Check the release page on GitHub — these manifests should appear as assets.

**Fix:** If missing, electron-builder didn't finish publishing. Re-run CI. If present but stale, check the version strings inside them against the git tag.

---

## Failure Mode 2 — Update detected but download fails

**Symptom:** "User sees the update prompt, but download bar hangs or errors out."

### Cause A — Private repo + missing GH_TOKEN at runtime

**Diagnostic:** Check the user's log file for 401 or 403 responses:
- macOS: `~/Library/Logs/<app>/main.log`
- Windows: `%USERPROFILE%\AppData\Roaming\<app>\logs\main.log`
- Linux: `~/.config/<app>/logs/main.log`

**Fix:** Either:
- Make the repo (or a separate release-assets repo) public
- Bundle a read-only GH token in the app

See `auto-update.md` for strategies.

### Cause B — CORS or CDN block

**Diagnostic:** Look for CORS errors, SSL failures, or timeouts from `github-releases.s3.amazonaws.com` in the logs.

**Fix:** Usually user-side (corporate firewall, overly aggressive proxy). Document in support channels; no universal fix.

### Cause C — Antivirus or Windows Defender blocking

**Diagnostic:** On Windows, check Windows Security → Protection history for blocked downloads.

**Fix:** EV-signed binaries with good reputation rarely hit this. If you're seeing it with OV signing, the best fix is upgrading to EV.

### Cause D — Disk full or permission denied

**Diagnostic:** Check user's disk space. Check write permissions on the update cache directory:
- macOS: `~/Library/Application Support/Caches/<app>-updater`
- Windows: `%APPDATA%\<app>-updater`
- Linux: `~/.config/<app>-updater`

**Fix:** Usually self-resolving once disk space is freed. If permissions are broken: reinstall.

---

## Failure Mode 3 — Install fails / signature mismatch

**Symptom:** "Update downloads, but install silently fails or app won't restart into the new version."

### Cause A — Cert rotated between versions (most common)

**Diagnostic:**
```sh
codesign -dvvv /Applications/YourApp.app | grep Authority
codesign -dvvv /path/to/new/YourApp.app | grep Authority
```

If Authority strings differ, electron-updater refuses to swap the binary. **This is a security feature, not a bug.**

**Fix:** Use the same signing cert for every release. If the cert must rotate:
- Users on the previous cert must reinstall manually
- You cannot push a seamless update across a cert change

**Prevention:**
- Calendar reminder 45 days before cert expiry
- Apple Developer certs last 5 years from issue — renew well ahead

### Cause B — Hardened runtime or notarization missing

**Diagnostic:**
```sh
spctl -a -t exec -vvv /path/to/YourApp.app
```
Expected: `source=Notarized Developer ID`. Any other output = notarization problem.

**Fix:** Re-run the release build. Confirm:
- `hardenedRuntime: true` in electron-builder config
- `notarize: true` (or relevant env vars present)
- Entitlements plist includes `com.apple.security.cs.allow-jit`

### Cause C — Windows UAC rejected elevation

**Diagnostic:** Windows log at `%USERPROFILE%\AppData\Roaming\<app>\logs\main.log` will show elevation errors.

**Fix:** Use `perMachine: false` in electron-builder's nsis config so updates install per-user (no UAC prompt).

### Cause D — Locked file on Windows

**Symptom:** "Windows says the file is in use."

**Fix:** electron-updater handles this correctly when you use `autoUpdater.quitAndInstall()`. If using custom flow, ensure the app fully quits before the installer runs.

---

## Failure Mode 4 — Version mismatch

**Symptom:** "I tagged v1.0.1 and CI finished, but the feed still shows v1.0.0."

### Cause — `package.json` version ≠ git tag

electron-builder writes the feed from `package.json`. If you tag `v1.0.1` but `package.json` still says `"version": "1.0.0"`, the feed says 1.0.0, and clients see no newer version.

**Diagnostic:**
```sh
cat package.json | jq .version
git describe --tags --abbrev=0
```

They must match (without the `v` prefix).

**Fix:** Use `npm version patch` (or `minor` / `major`) — it bumps package.json AND creates the git tag in one atomic operation. Don't tag manually.

**Prevention:** Always use `npm version <bump>` for releases. If you tagged manually, delete the tag (`git tag -d v1.0.1 && git push origin :v1.0.1`), run `npm version patch`, push again.

---

## Failure Mode 5 — Windows UAC loop / installer fails

**Symptom:** "On Windows, the installer prompts for admin password, user enters it, then same prompt appears again. Or install silently fails."

### Cause A — Wrong installer target

**Diagnostic:** Check `electron-builder.yml`:

```yaml
win:
  target:
    - target: msi   # ← THIS IS THE PROBLEM
```

**Fix:** Change to `nsis`:

```yaml
win:
  target:
    - target: nsis
```

### Cause B — Per-machine vs per-user mismatch

**Diagnostic:** Check `nsis.perMachine`. If it changed between versions, Windows can refuse the update.

**Fix:** Set explicitly:

```yaml
nsis:
  perMachine: false  # per-user (no UAC, default)
  # OR
  perMachine: true   # per-machine (requires UAC)
```

**Don't change this value mid-lifecycle.** Users installed before the change will break on updates.

### Cause C — Unsigned or OV-signed installer hitting SmartScreen

**Diagnostic:** Run on Windows:
```powershell
Get-AuthenticodeSignature .\YourApp-Setup.exe
```

If signer's reputation is low, SmartScreen may block silently.

**Fix:** EV signing. See `windows-signing.md`.

---

## Failure Mode 6 — None of the above (escalation)

When the five canonical modes come back clean and the update still doesn't work:

### Step 1: Read the full log

- macOS: `~/Library/Logs/<app>/main.log`
- Windows: `%USERPROFILE%\AppData\Roaming\<app>\logs\main.log`
- Linux: `~/.config/<app>/logs/main.log`

### Step 2: Enable verbose logging temporarily

```typescript
import log from 'electron-log';
log.transports.file.level = 'debug';
autoUpdater.logger = log;
```

Rebuild, have the user run, collect the debug log.

### Step 3: Force a full re-download

Delete the update cache directory (Failure Mode 2, Cause D). Some corrupted cached manifests can cause weird failures that clear once the cache is wiped.

### Step 4: Diff a known-good release against the failing one

Compare the `latest-mac.yml` / `latest.yml` of the last working release against the current broken one. Look for:
- Version string differences
- SHA512 / hash mismatches
- File size mismatches (truncated uploads)
- Unexpected path differences

### Step 5: Escalate upstream

Post an issue to [electron-userland/electron-builder](https://github.com/electron-userland/electron-builder/issues) with:
- Full debug log
- Your workflow YAML
- electron-builder version
- Platforms affected
- Minimal reproduction if possible

---

## Pre-release checklist (to avoid most of the above)

Run before every release:

- [ ] `package.json` version matches `git describe --tags --abbrev=0`
- [ ] GH Release is "latest" (not draft, not prerelease)
- [ ] `latest-mac.yml`, `latest.yml`, `latest-linux.yml` present in release assets
- [ ] Signing cert matches the previous release (`codesign -dvvv`)
- [ ] Notarization confirmed on Mac (`spctl -a -t exec -vvv`)
- [ ] Windows installer signed (EV ideally)
- [ ] Test install on clean VM passes
- [ ] Auto-update from previous version to this version works on clean VM

The `/ep-debug-update` command in the `donjon-electron-port` plugin automates most of these checks. If you're not using the plugin, consider writing a small script that runs this checklist as part of your release workflow.
