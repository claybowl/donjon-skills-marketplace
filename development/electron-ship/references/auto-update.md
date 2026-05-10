# Auto-Update — electron-updater + GitHub Releases Complete Setup

The end-to-end pipeline. Gets you from "first release published manually" to "I tag v1.0.1 and CI does everything."

## Prerequisites

1. Code signing works end-to-end. See `macos-signing.md` and `windows-signing.md`. **This is not optional** — unsigned auto-update fails silently on macOS.
2. `pnpm exec electron-builder` produces a signed binary locally.
3. You have a GitHub repo (private or public — both work).

## Install electron-updater

```sh
pnpm add electron-updater
```

## Wire it in the main process

```typescript
// src/main/main.ts
import { app, BrowserWindow } from 'electron';
import { autoUpdater } from 'electron-updater';
import log from 'electron-log';

// Pipe update logs to electron-log so users can send them for support
autoUpdater.logger = log;
log.transports.file.level = 'info';

app.whenReady().then(() => {
  // ...create window...
  autoUpdater.checkForUpdatesAndNotify();
});
```

That's the whole client side. electron-updater finds the feed URL from `package.json` (which electron-builder writes based on your publish config).

## Configure electron-builder publish target

In `electron-builder.yml`:

```yaml
publish:
  provider: github
  owner: your-gh-username-or-org
  repo: your-repo-name
  releaseType: release  # 'release' | 'prerelease' | 'draft'
  private: true         # set false for public repos
  vPrefixedTagName: true
```

Key points:
- `releaseType: release` publishes immediately as "latest". Use `draft` if you want to write release notes before users get the update.
- `private: true` means the app will need a `GH_TOKEN` at runtime to download updates (see below).

## Complete GitHub Actions workflow

See `assets/release.yml` for the copy-paste version. The shape:

- Trigger on `push` to tags matching `v*.*.*`
- Matrix: `macos-latest` + `windows-latest`
- Install → build → package → sign → notarize (Mac) → `electron-builder --publish always`

```yaml
name: Release

on:
  push:
    tags: ['v*.*.*']
  workflow_dispatch:  # allow manual trigger for testing

permissions:
  contents: write

jobs:
  release:
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        os: [macos-latest, windows-latest]

    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v2
        with:
          version: 9
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: pnpm
      - run: pnpm install --frozen-lockfile
      - run: pnpm build

      # Mac cert import (see macos-signing.md for full step)
      - name: Import Mac certificate
        if: matrix.os == 'macos-latest'
        env:
          MAC_CERTIFICATE: ${{ secrets.MAC_CERTIFICATE }}
          MAC_CERTIFICATE_PASSWORD: ${{ secrets.MAC_CERTIFICATE_PASSWORD }}
        run: |
          # ... keychain dance (see macos-signing.md) ...

      - name: Build and publish
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          APPLE_ID: ${{ secrets.APPLE_ID }}
          APPLE_APP_SPECIFIC_PASSWORD: ${{ secrets.APPLE_APP_SPECIFIC_PASSWORD }}
          APPLE_TEAM_ID: ${{ secrets.APPLE_TEAM_ID }}
        run: pnpm exec electron-builder --publish always

      # Optional: Windows signing via SignPath (see windows-signing.md)
```

## Cutting a release

```sh
# Bump version + create signed git tag atomically
npm version patch   # 1.0.0 → 1.0.1
# or: npm version minor  # 1.0.0 → 1.1.0
# or: npm version major  # 1.0.0 → 2.0.0

# Push commit + tag; CI fires
git push --follow-tags

# Watch the build live
gh run watch
```

CI takes 15–25 minutes. Apple notarization varies (5 min to 2 hours — not a failure, just Apple's queue).

## What electron-builder uploads to GitHub Releases

For each release tag, these artifacts appear on the GH Release page:

| File | Purpose |
|---|---|
| `YourApp-1.0.1-mac.dmg` | Mac installer (x64 or universal) |
| `YourApp-1.0.1-mac.zip` | Mac auto-update asset (electron-updater downloads this) |
| `YourApp-1.0.1-arm64-mac.dmg` | Apple Silicon installer |
| `YourApp-1.0.1-arm64-mac.zip` | Apple Silicon auto-update asset |
| `latest-mac.yml` | Manifest describing the latest Mac version |
| `YourApp Setup 1.0.1.exe` | Windows installer |
| `YourApp Setup 1.0.1.exe.blockmap` | Windows delta-update metadata |
| `latest.yml` | Manifest describing the latest Windows version |
| `YourApp-1.0.1.AppImage` | Linux installer |
| `latest-linux.yml` | Manifest describing the latest Linux version |

`electron-updater` reads `latest-mac.yml` / `latest.yml` / `latest-linux.yml` to detect new versions. These manifests are the feed.

## What users experience

**Default flow:**
1. App launches → `electron-updater` polls feed in background
2. Sees new version → downloads delta silently while user works
3. Shows a notification "Update available, restart to install"
4. User quits the app → installer runs → app relaunches as new version

**Customizable:**
- Prompt immediately (modal dialog) instead of on-quit
- Defer until idle or explicit user action
- Progress bar for long downloads via the `download-progress` event
- Custom update UI entirely (listen to `update-available`, control flow yourself)

Event-based API:

```typescript
autoUpdater.on('update-available', (info) => {
  // Show your own UI
});

autoUpdater.on('download-progress', (progress) => {
  // progress.percent, progress.bytesPerSecond, etc.
});

autoUpdater.on('update-downloaded', (info) => {
  // Prompt for restart
  autoUpdater.quitAndInstall();
});
```

## Handling private repos at runtime

If your repo is private, the installed app needs a GitHub token to download updates. Three options ranked by practicality:

### Option A — Bundle a read-only fine-grained PAT

Create a [fine-grained personal access token](https://github.com/settings/tokens?type=beta) with `contents: read` on just the release repo. Bundle in env or set at build time.

**Acceptable when:**
- Token is scoped to a single repo, read-only
- App is signed (binary is tamper-evident)
- Threat model: "occasional leak ≠ disaster"

**Not acceptable when:**
- App ships to external paying customers (token can be extracted from the binary)
- Token has any write permission anywhere

### Option B — Separate public repo for releases

Counterintuitively, often the right answer. Use a **public release-assets repo** distinct from your private source repo. Private repo's CI pushes binaries to public repo; `electron-updater` points at public repo.

Source stays private; binaries are public.

### Option C — Host updates elsewhere

Use S3, DigitalOcean Spaces, Cloudflare R2, or a generic HTTP server. electron-builder supports `generic`, `s3`, `spaces` providers.

```yaml
publish:
  provider: s3
  bucket: my-app-updates
  region: us-east-1
```

Set `AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY` in CI.

## First-release checklist

- [ ] All code signing secrets in GH Actions
- [ ] electron-builder publish config set
- [ ] `package.json` version is what you want for v1
- [ ] Icons in place
- [ ] `appId` set (uniquely, won't change)
- [ ] Workflow YAML committed
- [ ] Local signed build produces a working binary
- [ ] Tag and push: `npm version patch && git push --follow-tags`
- [ ] Watch CI: `gh run watch`
- [ ] Verify release appears: `gh release view`
- [ ] Download and install signed binary on clean VM
- [ ] Run; confirm no OS warnings

## Test the update pipeline (do this once after first release)

1. Install your v1.0.0 app on a clean VM. Launch. Confirm it works.
2. Bump to v1.0.1, push tag. Wait for CI to publish.
3. Launch the v1.0.0 app on the VM. Wait 30–60 seconds.
4. Confirm update prompt appears.
5. Click Update / Restart.
6. Confirm app relaunches as v1.0.1.

**If any of those fails, stop shipping and triage.** Better to catch it now than after real users are affected. See `failure-modes.md` for the five canonical failures.

## Channels and pre-releases (advanced)

`electron-builder` supports release channels:

- `latest` — production users
- `beta` — opt-in testers
- `alpha` — earliest adopters

In `package.json`, version strings like `1.0.0-beta.1` map to the beta channel.

In `electron-updater`:

```typescript
autoUpdater.channel = 'beta';
autoUpdater.allowPrerelease = true;
```

Setup is doable but adds complexity. Defer until you need it.

## Rollback strategy

electron-updater does not natively support downgrades. Plan for **forward-fix**:

- **Primary:** ship v1.0.2 fixing v1.0.1's bug. Users get a real fix within a release cycle.
- **Secondary:** unpublish the bad GitHub Release (mark as draft in the GH UI). New installs fall back to previous "latest"; existing installs on bad version stay there until v1.0.2.
- **Never:** force downgrade. electron-updater refuses and users end up with broken installs.

Treat every release as if you can't un-ship it.

## Alternative hosts (when GitHub Releases isn't the right fit)

| Provider | Best for | Setup |
|---|---|---|
| `github` | Default. 95% of cases. | Covered above |
| `s3` | Private enterprise, custom auth | Set AWS creds in CI |
| `spaces` (DigitalOcean) | Budget-friendly S3 alternative | Similar to s3 |
| `generic` | Custom HTTP server | Just a URL; you provide the feed |
| `hazel` | Free update server (deployable to Vercel) | Host Hazel; point at it |

For most Donjon-style projects, GitHub Releases is correct. If you find yourself wanting something else, it's usually a sign that auth or privacy needs are driving the decision.
