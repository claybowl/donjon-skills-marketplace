# macOS Code Signing & Notarization — Deep Dive

End-to-end walkthrough from Apple Developer enrollment through CI-based signing + notarization + stapling.

## Phase 1 — Apple Developer Program enrollment

1. Go to [developer.apple.com/programs](https://developer.apple.com/programs/) and click **Enroll**.
2. Choose **Individual** (solo dev) or **Organization** (company).
3. **For Organization:** Apple requires a D-U-N-S number. [Look it up or request one free](https://developer.apple.com/support/D-U-N-S/). Takes 1–3 business days.
4. Pay $99.
5. Wait for approval email — usually same-day for Individual, 24–48h for Organization.

**Choosing individual vs organization:** Individual enrollment puts your personal name on the app's "from" line. Organization puts your company's legal name. If the app is branded with a company name, enroll as Organization.

## Phase 2 — Create the Developer ID certificate

1. Go to [developer.apple.com/account/resources/certificates](https://developer.apple.com/account/resources/certificates).
2. Click **+** to create a new certificate.
3. Under **Software**, select **Developer ID Application**.
   - NOT "Apple Development" — that's for local dev only, not distribution.
   - NOT "Developer ID Installer" — that's for `.pkg` installers, not `.app` / `.dmg`.
4. Apple prompts you to generate a Certificate Signing Request (CSR) from Keychain:
   - Open **Keychain Access** → **Certificate Assistant** (menu) → **Request a Certificate From a Certificate Authority**
   - User Email Address: your Apple ID email
   - Common Name: "Your Org Name" (or your name for Individual enrollment)
   - Request is: **Saved to disk**
5. Upload the `.certSigningRequest` file to Apple. Apple returns a `.cer` file.
6. Double-click the `.cer` to install it in Keychain.

**Verify it installed correctly:** Open Keychain Access → login keychain → My Certificates. You should see:
- "Developer ID Application: Your Name (TEAMID)"
- An expandable private key nested under the cert

If there's no private key, something went wrong. The cert is useless without its private key — you'll need to regenerate.

## Phase 3 — Export certificate for CI

1. In Keychain Access, find the "Developer ID Application" certificate.
2. Right-click → **Export "Developer ID Application: ..."**.
3. File Format: **Personal Information Exchange (.p12)**.
4. Save as a `.p12` file. Set a strong password — you'll paste it as a GH Actions secret.
5. Store the `.p12` in a password manager or encrypted drive. **Never commit it to git.**

## Phase 4 — App-specific password for notarization

Notarization uses an app-specific password, not your Apple ID password directly.

1. Go to [appleid.apple.com](https://appleid.apple.com/).
2. Sign In and Security → **App-Specific Passwords** → **Generate Password**.
3. Label it "electron-notarize" (or similar).
4. Copy the generated password (16-character format). **Can't be re-viewed later** — store it now.

## Phase 5 — Find your Team ID

1. Go to [developer.apple.com/account](https://developer.apple.com/account).
2. Scroll to Membership Details.
3. Your **Team ID** is a 10-character string. Copy it.

## Phase 6 — GitHub Actions secrets

In your repo: **Settings → Secrets and variables → Actions → New repository secret**. Add:

| Secret name | Value | How to get |
|---|---|---|
| `MAC_CERTIFICATE` | Base64-encoded `.p12` | `base64 -i YourCert.p12 \| pbcopy` then paste |
| `MAC_CERTIFICATE_PASSWORD` | Password you set when exporting | From Phase 3 |
| `APPLE_ID` | Your Apple ID email | - |
| `APPLE_APP_SPECIFIC_PASSWORD` | App-specific password | From Phase 4 |
| `APPLE_TEAM_ID` | 10-char Team ID | From Phase 5 |

## Phase 7 — CI workflow

Complete workflow YAML in `assets/release.yml`. The Mac-specific section:

```yaml
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

- name: Build and publish
  env:
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    APPLE_ID: ${{ secrets.APPLE_ID }}
    APPLE_APP_SPECIFIC_PASSWORD: ${{ secrets.APPLE_APP_SPECIFIC_PASSWORD }}
    APPLE_TEAM_ID: ${{ secrets.APPLE_TEAM_ID }}
  run: pnpm exec electron-builder --publish always
```

This imports the cert, runs `electron-builder` which auto-detects the Developer ID cert, signs, notarizes, and staples — all in one pass. Apple's notarization service handles the actual malware scan (5 min to 2 hours).

## Phase 8 — Verify the signed binary

After CI produces an artifact, download it and verify:

```sh
# Check signature
codesign -dvvv /path/to/YourApp.app

# Expected output:
#   Authority=Developer ID Application: Your Name (TEAMID)
#   Authority=Developer ID Certification Authority
#   Authority=Apple Root CA
#   TeamIdentifier=TEAMID

# Check notarization
spctl -a -t exec -vvv /path/to/YourApp.app

# Expected output:
#   /path/to/YourApp.app: accepted
#   source=Notarized Developer ID
```

If either check fails, the binary won't work for auto-update (and may not install at all on recent macOS).

## Phase 9 — Before every release

- **Check cert expiry.** Keychain Access → your cert → Get Info. If within 45 days of expiry, renew NOW — don't wait for the release to fail.
- **Rotate app-specific password** every 6 months; update the GH Secret.
- **Test-install the signed binary** on a clean Mac. Confirm no Gatekeeper warnings.

## Common macOS signing errors

### `errSecInternalComponent` during signing

Keychain locked, or partition-list not set. Re-run the keychain setup — make sure `security set-key-partition-list` is called after import.

### Notarization rejected with "hardened runtime not enabled"

Set `hardenedRuntime: true` in `electron-builder.yml` under `mac`.

### Notarization rejected with "invalid entitlements"

Missing `com.apple.security.cs.allow-jit`. Add to your entitlements plist. See `assets/entitlements.mac.plist`.

### Notarization succeeds but app still shows "unidentified developer"

You didn't staple. electron-builder does this automatically, but if you signed manually:
```sh
xcrun stapler staple YourApp.app
```

### `"user interaction is not allowed"` during `security` commands in CI

Keychain isn't unlocked. Add `security set-keychain-settings -t 3600 -l build.keychain` after creating the keychain.

### Cert expired mid-release

Renew at Apple Developer portal. You cannot recover the old cert; you'll need to re-issue, re-export, re-upload to GH Secrets. Rotating the cert means new releases are signed differently from old ones — existing installs won't auto-update across the cert change. Users must reinstall manually.

### "The executable does not have the hardened runtime enabled"

Same as the notarization error. `hardenedRuntime: true` is the fix.

## Alternative: signing without the Apple Developer Program

You can distribute an unsigned app on macOS, but users will see "Apple could not verify this app is free of malware" on first launch. Most won't proceed.

Workarounds (mostly bad):
1. **Self-signed certificate.** Works for personal apps; useless for distribution.
2. **Ad-hoc signed** (`codesign --sign -`). Lets the app run on the signer's machine; not transferable.
3. **Tell users to right-click Open.** Explicit user override; doesn't scale.

For any real distribution, the $99/year is the right answer.
