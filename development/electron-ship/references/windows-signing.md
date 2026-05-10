# Windows Code Signing — Deep Dive

Full Windows signing flow, focused on the **SignPath cloud signing path** (recommended) and self-hosted hardware token path as fallback.

## Why signing matters on Windows

Without code signing, Windows SmartScreen Filter shows a "Windows protected your PC" dialog when users run your installer. Depending on cert type:

| Cert type | What users see on install |
|---|---|
| Unsigned | SmartScreen blocks; users must click "More info → Run anyway" |
| OV (Organization Validation) | SmartScreen warns until reputation builds (weeks, thousands of installs) |
| EV (Extended Validation) | No SmartScreen warning from install #1 |

**For a new app with no install base: use EV.** The $100 → $400/yr difference is invisible next to the marketing cost of a SmartScreen dialog scaring off users.

## Path 1 — Cloud code signing service (RECOMMENDED)

Services host the hardware token in the cloud. You upload unsigned binaries; they sign; CI downloads signed binaries.

### Options compared

| Service | Cost / yr | Notes |
|---|---|---|
| **SignPath.io** | Free tier for open source; ~$150/yr for closed-source small orgs | Best DX, first-class GitHub Action, policy-based signing |
| **Certum SimplySign** | ~$150/yr EV | European CA; budget-friendly; automation via their API |
| **DigiCert KeyLocker** | ~$400/yr | Enterprise-grade; tight integration with DigiCert HSM |
| **SSL.com eSigner** | ~$300/yr | Good support, widely used |

**SignPath is the default recommendation** for Donjon-style small teams. Their GitHub Action is first-class and their free tier is generous for open source.

### SignPath setup

1. Sign up at [signpath.io](https://signpath.io). Create an Organization.
2. Acquire an EV code signing certificate (SignPath can broker this from Certum or DigiCert).
3. In SignPath, create a **Project** for your app.
4. Create a **Signing Policy** (who can sign which artifacts for which project).
5. Get credentials → add to GitHub Secrets:
   - `SIGNPATH_ORG_ID`
   - `SIGNPATH_PROJECT_SLUG`
   - `SIGNPATH_SIGNING_POLICY_SLUG`
   - `SIGNPATH_API_TOKEN`

### CI workflow snippet

Add after `electron-builder` produces the unsigned Windows installer:

```yaml
- name: Sign Windows installer with SignPath
  if: matrix.os == 'windows-latest'
  uses: signpath/github-action-submit-signing-request@v1
  with:
    api-token: ${{ secrets.SIGNPATH_API_TOKEN }}
    organization-id: ${{ secrets.SIGNPATH_ORG_ID }}
    project-slug: ${{ secrets.SIGNPATH_PROJECT_SLUG }}
    signing-policy-slug: ${{ secrets.SIGNPATH_SIGNING_POLICY_SLUG }}
    github-artifact-name: windows-installer
    wait-for-completion: true
    output-artifact-directory: 'signed-installer'

- name: Upload signed installer to release
  if: matrix.os == 'windows-latest'
  run: gh release upload ${{ github.ref_name }} signed-installer/*.exe
  env:
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Timing

SignPath's sync signing usually completes in 30–90 seconds. Async signing (for higher-volume accounts) can take longer but doesn't block CI.

## Path 2 — Self-hosted EV hardware token

If you buy an EV cert directly from DigiCert / Sectigo / Comodo, they ship a **USB hardware token**. The private key never leaves the token — signing requires physical access.

**Consequence for CI:** GitHub's hosted Windows runners **cannot** use USB hardware tokens. You need:
- A self-hosted Windows runner with the token plugged in, OR
- A third-party service that fronts the token for you (→ back to Path 1)

Unless you already have a dedicated Windows release machine running, **Path 1 is dramatically less pain.**

### If you do go self-hosted

1. Set up a [self-hosted GH Actions runner](https://docs.github.com/en/actions/hosting-your-own-runners) on a Windows machine.
2. Install the vendor's signing driver (DigiCert SafeNet, etc.).
3. Plug in the token. Unlock with its password (stored as GH secret and passed to `signtool`).
4. Use electron-builder's built-in Windows signing config:

```yaml
win:
  certificateSubjectName: "Your Organization Name"
  signingHashAlgorithms:
    - sha256
```

electron-builder finds the cert by subject name and calls `signtool.exe` automatically.

## Path 3 — Standard (OV) Code Signing — NOT recommended for new apps

Cheaper ($80–150/yr), no hardware token. But SmartScreen warns until cert reputation builds — needs thousands of installs. Chicken-and-egg: users don't install because of the warning; reputation doesn't build.

Use this only if:
- You have thousands of existing users who'll install regardless of the warning
- You're migrating from unsigned (OV is strictly better than nothing)

## Installer target — pick once

| Target | Installer size | Auto-update compatible | Use when |
|---|---|---|---|
| `nsis` | Larger (~150MB+) | ✅ Yes | Default choice |
| `nsis-web` | Tiny stub (~1MB) | ✅ Yes | Bandwidth-sensitive |
| `portable` | Standalone exe | ❌ No | No-install standalone |
| `msi` | Variable | ❌ No — fights electron-updater | Avoid |

**Default: `nsis`.**

## Before every Windows release

- Verify cert is still valid (check SignPath dashboard or token inspection)
- Test-install the signed installer on a clean Windows 10 / 11 VM
- Confirm no SmartScreen warning
- Sanity-check installer size — bloated installers usually mean unnecessary `files` globs

## Common Windows signing errors

### `SignerSign() failed` with error `0x80092004`

Signing cert not found in the store. Either wrong subject name (Path 2) or cert isn't installed on the runner.

### `The specified timestamp server could not be reached`

electron-builder uses a timestamp server by default (DigiCert). If blocked, configure alternate:

```yaml
win:
  signtoolOptions:
    signingHashAlgorithms: ["sha256"]
    timeStampServer: "http://timestamp.digicert.com"
```

Common alternatives: `http://ts.ssl.com`, `http://timestamp.sectigo.com`.

### SmartScreen warning despite EV signing

Reputation needs ~24 hours to propagate after a new cert is issued. Wait a day, try again. If it persists after 72 hours, submit the binary for [Microsoft Defender false-positive review](https://www.microsoft.com/en-us/wdsi/filesubmission).

### `SignPath signing request failed: policy X rejected`

Your SignPath policy doesn't permit signing this artifact. Check:
- Policy slug matches what the workflow passes
- Artifact name matches policy's allowed patterns
- User / org has permission on the policy

### Install fails silently on Windows

Check the log file: `%USERPROFILE%\AppData\Roaming\<app>\logs\main.log`. Common causes:
- Wrong `perMachine` setting mid-lifecycle (don't change this)
- Antivirus blocked the installer
- User clicked "More info → Don't run" from SmartScreen

### Per-user vs per-machine confusion

In `electron-builder.yml`:

```yaml
nsis:
  perMachine: false  # per-user install (default; no UAC)
  # OR
  perMachine: true   # per-machine (requires UAC admin)
```

**Don't change this mid-lifecycle.** Users from before the change will break on update. Pick once and keep.

## Antivirus false positives

Electron apps occasionally trigger antivirus heuristics, especially on Windows. Mitigations:
- EV signing reduces this significantly
- Submit known-good binaries to [Microsoft Defender](https://www.microsoft.com/en-us/wdsi/filesubmission) and [VirusTotal](https://www.virustotal.com/) proactively
- Document the false-positive pattern for your users' IT teams
