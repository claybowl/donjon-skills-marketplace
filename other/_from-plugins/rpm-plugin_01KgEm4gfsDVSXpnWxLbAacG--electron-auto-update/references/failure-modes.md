# Auto-Update Failure Modes — Deep Triage Guide

Every known failure mode for `electron-updater` with GitHub Releases, organized by symptom. The `/ep-debug-update` command walks through all five in order; this document provides the detail.

## How to read this guide

Each failure mode has four sections:
1. **Symptom** — what the user reports
2. **Likely cause** — what's actually broken
3. **Diagnostic** — how to confirm
4. **Fix** — how to solve it

## Failure Mode 1 — Update not detected

**Symptom:** "I shipped version 1.0.1 yesterday. Users on 1.0.0 are not getting the update prompt."

### Cause A: Feed URL doesn't point at the right repo

**Diagnostic:**
- Open `electron-builder.yml` or the `build.publish` block in `package.json`.
- Confirm `provider`, `owner`, `repo` match the actual repo where releases are uploaded.
- Check the built manifest: `open dist/latest-mac.yml` (after a local build). Confirm it has the right version.

**Fix:** Correct the publish config. Rebuild and republish.

### Cause B: New release isn't marked "latest"

**Diagnostic:**
```sh
curl https://api.github.com/repos/<owner>/<repo>/releases/latest
```
(Add `-H "Authorization: Bearer $GH_TOKEN"` for private repos.)

Compare the returned `tag_name` against what you expect. If it doesn't match your newest release, the release is probably a draft or prerelease.

**Fix:** Go to the release on GitHub → uncheck "Set as a pre-release" or publish from draft → "Set as latest release".

Alternatively, in your electron-builder config:
```yaml
publish:
  releaseType: release
```

### Cause C: Client-side update check is throttled or cached

**Diagnostic:** `electron-updater` caches the last-check timestamp. By default it only checks once per hour. Force a check with `autoUpdater.checkForUpdates()` manually (not the `AndNotify` variant).

**Fix:** Restart the app, or add a manual check button in settings:
```typescript
import { autoUpdater } from 'electron-updater';
ipcMain.handle('check-for-updates', () => autoUpdater.checkForUpdates());
```

### Cause D: Asset naming mismatch

**Diagnostic:** The release must contain a `latest-mac.yml` (or `latest.yml` / `latest-linux.yml`) file. Check the release page on GitHub — these manifest files should be listed as assets.

**Fix:** If they're missing, electron-builder didn't finish publishing. Re-run CI. If they're there but wrong, check the version inside them against the release tag.

---

## Failure Mode 2 — Update detected but download fails

**Symptom:** "User sees update prompt, but download bar hangs or errors out."

### Cause A: Private repo + missing GH_TOKEN at runtime

**Diagnostic:** Check the user's log file (`~/Library/Logs/<app>/main.log` or Windows equivalent) for 401 or 403 responses.

**Fix:** Either make the repo (or a release-assets repo) public, or bundle a read-only GH token into the app. See `github-releases-setup.md` on private repo strategies.

### Cause B: CORS or CDN block

**Diagnostic:** Check logs for CORS errors or timeouts from `github-releases.s3.amazonaws.com` or similar.

**Fix:** Usually a user-side corporate firewall. Document it in support; no universal fix.

### Cause C: Antivirus or Windows Defender blocking download

**Diagnostic:** On Windows especially, check Windows Security → Protection history for blocked downloads.

**Fix:** Signed binaries with good reputation rarely hit this. If new (OV) cert, users get past it by clicking through. With EV, shouldn't happen.

### Cause D: Disk full or permissions

**Diagnostic:** Check the user's disk space. Check write permissions on the update cache directory (`~/Library/Application Support/Caches/<app>-updater` or `%APPDATA%/<app>-updater`).

**Fix:** Usually self-resolving once disk space is cleared. If permissions: reinstall.

---

## Failure Mode 3 — Install fails / signature mismatch

**Symptom:** "Update downloads, but install fails or app won't restart into the new version. Often silent on Mac."

### Cause A: Cert rotated between versions (most common)

**Diagnostic:**
```sh
codesign -dvvv /Applications/YourApp.app | grep Authority
# vs
codesign -dvvv /Applications/YourApp.app.updated | grep Authority
```

If the Authority strings differ, electron-updater refuses to swap the binary. This is a security feature, not a bug.

**Fix:** Use the same signing cert for every release. If the cert must rotate (expired, lost), users will need to reinstall manually. You cannot push a seamless update across a cert rotation.

**Prevention:** Set calendar reminder 45 days before cert expiry. Apple Developer certs last 5 years from issue; treat this as a rare problem, but know the rules.

### Cause B: Hardened runtime or notarization missing on new version

**Diagnostic:**
```sh
spctl -a -t exec -vvv /path/to/YourApp.app
```
Should output `source=Notarized Developer ID`. If it says "unsigned" or "rejected", you have a notarization problem.

**Fix:** Re-run the release build. Confirm `hardenedRuntime: true` and `notarize: true` in electron-builder config.

### Cause C: Windows UAC rejected elevation

**Diagnostic:** Windows `%USERPROFILE%\AppData\Roaming\<app>\logs\main.log` will show elevation errors.

**Fix:** Use `perMachine: false` in electron-builder's nsis config so updates don't require UAC elevation.

---

## Failure Mode 4 — Version mismatch

**Symptom:** "I tagged v1.0.1 and CI finished, but the feed still shows 1.0.0."

### Cause: package.json version ≠ git tag

electron-builder writes the feed from `package.json`. If you tag `v1.0.1` but `package.json` still says `"version": "1.0.0"`, the feed says 1.0.0, and users running 1.0.0 see no new version.

**Diagnostic:**
```sh
cat package.json | jq .version
git describe --tags --abbrev=0
```

They must match (without the `v` prefix).

**Fix:** Use `npm version patch` (or `minor` / `major`) to bump package.json AND create the git tag in one atomic step. Don't tag manually.

**Prevention:** The `/ep-release` command runs this check pre-flight.

---

## Failure Mode 5 — Windows UAC loop / installer fails

**Symptom:** "On Windows, the update installer runs, prompts for admin password, user enters it — then the same prompt shows again. Or the install just silently fails."

### Cause A: Wrong installer target

**Diagnostic:** Check `electron-builder.yml`:
```yaml
win:
  target:
    - target: msi   # ← THIS IS THE PROBLEM
```

MSI installers fight with electron-updater.

**Fix:** Change to `nsis` or `nsis-web`:
```yaml
win:
  target:
    - target: nsis
```

### Cause B: Per-machine vs per-user mismatch

**Diagnostic:** Check `nsis.perMachine` in config.

If the app was originally installed per-user (default) but the update tries per-machine install, or vice versa, Windows refuses.

**Fix:** Set explicitly: `nsis.perMachine: false` (per-user, default) or `true`. Don't change this mid-lifecycle — users from before the change will break.

### Cause C: Unsigned or OV-signed installer hitting SmartScreen

**Diagnostic:** Check if the new installer is EV-signed. Run:
```powershell
Get-AuthenticodeSignature .\YourApp-Setup.exe
```

If the signer's reputation is low, SmartScreen blocks silently.

**Fix:** Use EV signing (see `electron-code-signing/references/windows-deep-dive.md`). OV certs build reputation slowly over thousands of installs.

---

## Failure Mode 6 — No known cause (escalation path)

When all five above come back clean and the update still doesn't work:

1. **Read the full log file.**
   - Mac: `~/Library/Logs/<app>/main.log`
   - Windows: `%USERPROFILE%\AppData\Roaming\<app>\logs\main.log`
   - Linux: `~/.config/<app>/logs/main.log`

2. **Enable verbose logging temporarily:**
```typescript
import log from 'electron-log';
log.transports.file.level = 'debug';
autoUpdater.logger = log;
```

3. **Force a full re-download** by deleting the update cache:
   - Mac: `~/Library/Application Support/Caches/<app>-updater`
   - Windows: `%APPDATA%\<app>-updater`

4. **Compare a known-good release** (one that worked for previous users) with the failing one. Diff the `latest-mac.yml` / `latest.yml` files.

5. **Post an issue to [electron-userland/electron-builder](https://github.com/electron-userland/electron-builder/issues)** with the full log and the workflow YAML.

## Prevention — the release checklist

After every release, confirm:

- [ ] `package.json` version matches `git describe --tags --abbrev=0`
- [ ] GH Release is marked "latest" (not draft, not prerelease)
- [ ] `latest-mac.yml`, `latest.yml`, `latest-linux.yml` present in release assets
- [ ] Signing cert matches the previous release (`codesign -dvvv`)
- [ ] Notarization confirmed on Mac (`spctl -a -t exec -vvv`)
- [ ] Test install on clean VM passes
- [ ] Auto-update from previous version to this version works on clean VM

The `/ep-debug-update` command automates most of these checks. Run it before publicizing any release.
