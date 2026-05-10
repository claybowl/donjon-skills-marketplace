# macOS Code Signing & Notarization — Deep Dive

The full Mac signing + notarization workflow, from Apple Developer enrollment through CI. Load when the user is actually doing the signing setup, not just reading about it.

## Phase 1 — Apple Developer Program enrollment

1. Go to [developer.apple.com/programs](https://developer.apple.com/programs/) and click **Enroll**.
2. Choose **Individual** (solo dev) or **Organization** (company).
3. For Organization: Apple requires a D-U-N-S number. You can [look up / request one free](https://developer.apple.com/support/D-U-N-S/). Takes 1–3 business days.
4. Pay $99.
5. Wait for approval email — usually same-day for Individual, 24–48h for Organization.

**Donjon note:** If you want "Donjon Intelligence Systems" on the Mac "from" line when users install, enroll as Organization, not Individual. Individual enrollment uses your personal name.

## Phase 2 — Create the Developer ID certificate

1. Go to [developer.apple.com/account/resources/certificates](https://developer.apple.com/account/resources/certificates).
2. Click **+** to create a new certificate.
3. Under **Software**, select **Developer ID Application**. (NOT "Apple Development" — that's for local testing only.)
4. Apple will ask you to generate a Certificate Signing Request (CSR) from Keychain Access:
   - Open **Keychain Access** → Menu **Certificate Assistant** → **Request a Certificate From a Certificate Authority**
   - User email: your Apple ID
   - Common name: "Donjon Intelligence Systems" (or your name)
   - Saved to disk
5. Upload the CSR to Apple Developer portal. Apple returns a `.cer` file.
6. Double-click the `.cer` to install it in Keychain.

**Verify it installed correctly:** Open Keychain Access → login → My Certificates. You should see "Developer ID Application: Your Name (TEAMID)" with a private key expandable under it.

## Phase 3 — Export certificate for CI

1. In Keychain Access, find your "Developer ID Application" certificate.
2. Right-click → **Export**.
3. Save as `.p12` file. Set a strong password — you'll paste this in GH Secrets.
4. Store the `.p12` somewhere safe (1Password, Bitwarden, encrypted drive). **Don't commit it.**

## Phase 4 — Set up app-specific password for notarization

1. Go to [appleid.apple.com](https://appleid.apple.com/).
2. Sign In & Security → **App-Specific Passwords** → **Generate**.
3. Label it "electron-notarize".
4. Copy the password (one-time view). Store it in your password manager.

## Phase 5 — GitHub Actions secrets

In your repo → Settings → Secrets and variables → Actions → New repository secret. Add these:

| Secret name | Value |
|---|---|
| `MAC_CERTIFICATE` | Base64-encoded `.p12` file: `base64 -i YourCert.p12 \| pbcopy` then paste |
| `MAC_CERTIFICATE_PASSWORD` | The password you set when exporting the `.p12` |
| `APPLE_ID` | Your Apple ID email |
| `APPLE_APP_SPECIFIC_PASSWORD` | The password from Phase 4 |
| `APPLE_TEAM_ID` | 10-character team ID — find it at [developer.apple.com/account](https://developer.apple.com/account) under Membership Details |

## Phase 6 — GitHub Actions workflow

`.github/workflows/release.yml`:

```yaml
name: Release

on:
  push:
    tags:
      - 'v*.*.*'

jobs:
  release:
    runs-on: ${{ matrix.os }}
    strategy:
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

      # Import Mac cert into a temporary keychain (Mac runner only)
      - name: Import Mac certificate
        if: matrix.os == 'macos-latest'
        env:
          MAC_CERTIFICATE: ${{ secrets.MAC_CERTIFICATE }}
          MAC_CERTIFICATE_PASSWORD: ${{ secrets.MAC_CERTIFICATE_PASSWORD }}
        run: |
          echo $MAC_CERTIFICATE | base64 --decode > certificate.p12
          security create-keychain -p "$MAC_CERTIFICATE_PASSWORD" build.keychain
          security default-keychain -s build.keychain
          security unlock-keychain -p "$MAC_CERTIFICATE_PASSWORD" build.keychain
          security set-keychain-settings -t 3600 -l build.keychain
          security import certificate.p12 -k build.keychain -P "$MAC_CERTIFICATE_PASSWORD" -T /usr/bin/codesign
          security set-key-partition-list -S apple-tool:,apple: -s -k "$MAC_CERTIFICATE_PASSWORD" build.keychain
          rm certificate.p12

      - name: Build and publish
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          APPLE_ID: ${{ secrets.APPLE_ID }}
          APPLE_APP_SPECIFIC_PASSWORD: ${{ secrets.APPLE_APP_SPECIFIC_PASSWORD }}
          APPLE_TEAM_ID: ${{ secrets.APPLE_TEAM_ID }}
        run: pnpm exec electron-builder --publish always
```

This builds, signs, and notarizes in one go. electron-builder handles everything after the cert is in the keychain.

## Phase 7 — Verify the signed binary

After CI produces an artifact, download it and verify:

```sh
# Check signature
codesign -dvvv /path/to/YourApp.app

# Expected: "Authority=Developer ID Application: Your Name (TEAMID)"
# Expected: "TeamIdentifier=TEAMID"

# Check notarization
spctl -a -t exec -vvv /path/to/YourApp.app

# Expected: "source=Notarized Developer ID"
```

If either check fails, the binary won't work for auto-update. Triage before publishing.

## Phase 8 — Before every release

- Check cert expiry: Keychain Access → your cert → Get Info. If within 45 days of expiry, renew now.
- Rotate app-specific password every 6 months; update the GH Secret.

## Common macOS signing errors

### "errSecInternalComponent" during signing

Usually: keychain locked or partition-list not set correctly. Re-run the keychain setup, ensure `security set-key-partition-list` runs.

### Notarization bounces with "hardened runtime not enabled"

Set `hardenedRuntime: true` in `electron-builder.yml` under `mac`.

### Notarization bounces with "invalid entitlements"

Missing `com.apple.security.cs.allow-jit`. Add to your entitlements plist.

### Notarization succeeds but app still shows "unidentified developer"

You forgot to staple. electron-builder does this automatically, but if you signed manually you need `xcrun stapler staple YourApp.app`.

### "user interaction is not allowed" during `security` commands

The keychain isn't unlocked. Add `security set-keychain-settings -t 3600 -l build.keychain` after `create-keychain`.

## Donjon-specific notes

(To be populated after first Donjon Mac release)

- Actual app IDs used
- Team ID
- Any quirks from the first release we should remember
