# GitHub Releases Auto-Update Pipeline — Full Setup

End-to-end walkthrough for the `electron-updater` + GitHub Releases pipeline. This is the minimum-viable, known-good path.

## Prerequisites before you start

1. Code signing is set up and working. See `electron-code-signing/references/macos-deep-dive.md` and `windows-deep-dive.md`.
2. The app runs locally in dev and produces a packaged binary with `pnpm exec electron-builder`.
3. You have a GitHub repo for the app. Private or public — both work.

Don't skip prereq 1. Unsigned auto-update fails silently on macOS. No amount of debugging the feed helps if the cert isn't right.

## Complete GitHub Actions workflow

`.github/workflows/release.yml`:

```yaml
name: Release

on:
  push:
    tags:
      - 'v*.*.*'
  workflow_dispatch:  # allows manual trigger from GH UI for testing

permissions:
  contents: write  # needed to create/update releases

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

      - run: pnpm build  # or whatever your build script is called

      # --- Mac-only signing setup ---
      - name: Import Mac certificate
        if: matrix.os == 'macos-latest'
        env:
          MAC_CERTIFICATE: ${{ secrets.MAC_CERTIFICATE }}
          MAC_CERTIFICATE_PASSWORD: ${{ secrets.MAC_CERTIFICATE_PASSWORD }}
        run: |
          echo "$MAC_CERTIFICATE" | base64 --decode > certificate.p12
          security create-keychain -p "$MAC_CERTIFICATE_PASSWORD" build.keychain
          security default-keychain -s build.keychain
          security unlock-keychain -p "$MAC_CERTIFICATE_PASSWORD" build.keychain
          security set-keychain-settings -t 3600 -l build.keychain
          security import certificate.p12 -k build.keychain \
            -P "$MAC_CERTIFICATE_PASSWORD" -T /usr/bin/codesign
          security set-key-partition-list \
            -S apple-tool:,apple: \
            -s -k "$MAC_CERTIFICATE_PASSWORD" \
            build.keychain
          rm certificate.p12

      # --- The actual build & publish ---
      - name: Build and publish to GitHub Releases
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          APPLE_ID: ${{ secrets.APPLE_ID }}
          APPLE_APP_SPECIFIC_PASSWORD: ${{ secrets.APPLE_APP_SPECIFIC_PASSWORD }}
          APPLE_TEAM_ID: ${{ secrets.APPLE_TEAM_ID }}
        run: pnpm exec electron-builder --publish always

      # --- Windows: sign after build via SignPath ---
      # See electron-code-signing/references/windows-deep-dive.md for SignPath step
```

## electron-builder publish config

In `electron-builder.yml`:

```yaml
publish:
  provider: github
  owner: <your-gh-username-or-org>
  repo: <your-repo-name>
  releaseType: release  # 'release' | 'prerelease' | 'draft'
  private: true         # true if your repo is private
  vPrefixedTagName: true
```

Key points:
- `releaseType: release` publishes immediately as "latest". Use `draft` if you want to write release notes before users get the update.
- `private: true` requires authenticated downloads — the app will need `GH_TOKEN` at runtime for private repos (see next section).

## Handling private repos at runtime

If the repo is private, the installed app needs a GitHub token to download updates. Two options:

### Option A — Bundle a fine-grained GH token

Create a fine-grained personal access token with **contents: read** permission on just that repo. Bundle it in the app's env or hardcoded config.

**Only acceptable when:**
- The token is read-only and scoped to this single repo
- The app is already signed (so the binary is tamper-evident)
- Your team's threat model is "occasional leak ≠ disaster"

**Not acceptable when:**
- The app ships to external paying customers (they can extract the token)
- The token has any write permission anywhere

### Option B — Make the repo public

Counterintuitively, this is often the right answer. Releases can be public-download even if the code repo is private — use a **separate public repo for releases**, triggered from your private source repo.

Set up a "release-assets" public repo. CI in your private repo pushes release binaries to the public repo. electron-updater points at the public repo. Source code stays private; binaries are public.

### Option C — Host updates elsewhere

Use S3, DigitalOcean Spaces, or Cloudflare R2 as a generic provider. `electron-builder` supports it out of the box.

```yaml
publish:
  provider: s3
  bucket: doer-updates
  region: us-east-1
```

Set `AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY` in CI.

## What electron-builder publishes

For each release tag, electron-builder uploads:

| File | Purpose |
|---|---|
| `Doer-1.0.1-mac.dmg` | Mac installer (x64 or universal) |
| `Doer-1.0.1-mac.zip` | Mac auto-update asset (electron-updater downloads this) |
| `Doer-1.0.1-arm64-mac.dmg` | Apple Silicon installer |
| `Doer-1.0.1-arm64-mac.zip` | Apple Silicon auto-update asset |
| `latest-mac.yml` | Manifest describing the latest Mac version |
| `Doer Setup 1.0.1.exe` | Windows installer |
| `Doer Setup 1.0.1.exe.blockmap` | Windows delta-update metadata |
| `latest.yml` | Manifest describing the latest Windows version |
| `Doer-1.0.1.AppImage` | Linux installer |
| `latest-linux.yml` | Manifest describing the latest Linux version |

electron-updater reads `latest-mac.yml` / `latest.yml` / `latest-linux.yml` to detect new versions.

## First-release checklist

- [ ] All code signing secrets in GH
- [ ] electron-builder publish config set
- [ ] `package.json` version is reasonable (`0.1.0` or `1.0.0`)
- [ ] Icons in place
- [ ] `appId` set uniquely
- [ ] Workflow YAML committed
- [ ] Test the signed local build works before CI
- [ ] Tag and push: `npm version patch && git push --follow-tags`
- [ ] Watch CI: `gh run watch`
- [ ] Verify release appears: `gh release view`
- [ ] Download and install the signed binary on a clean VM
- [ ] Run it; confirm no OS warnings

## Test the update pipeline (do this once after the first release)

1. Install your 1.0.0 app on a clean VM. Run it. Confirm it works.
2. Bump to 1.0.1, push the tag. Wait for CI to publish.
3. Launch the 1.0.0 app on the VM. Wait 30–60 seconds.
4. Confirm the update prompt appears.
5. Click Update / Restart.
6. Confirm the app relaunches as 1.0.1.

**If any of those five steps fails, stop shipping and triage.** Better to catch it now than after real users are affected.

## Channels & pre-releases (future)

`electron-builder` supports channels (`latest`, `beta`, `alpha`). `electron-updater` can be configured to only subscribe to `latest`, or to opt into `beta` / `alpha`.

Setup is slightly more involved; defer until v0.2.0 of this plugin. For v1 releases, stick to `latest` only.
