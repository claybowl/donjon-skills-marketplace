# Windows Code Signing — Deep Dive

Full Windows signing flow, focused on the **SignPath cloud signing path** (the recommended path for most Donjon work) and the **self-hosted EV token path** as a fallback.

## Why signing matters on Windows

Without code signing, Windows SmartScreen shows a "Windows protected your PC" dialog when users run your installer. With a standard (OV) cert, the warning still shows until reputation builds (can take weeks, thousands of installs). With an EV cert, reputation is immediate from install #1.

**For a new app going to market: use EV signing.** The cost difference ($100 → $400/yr) is invisible next to the marketing cost of a SmartScreen dialog scaring off users.

## Path 1 — Cloud code signing service (RECOMMENDED)

Services host the hardware token in the cloud. Your CI uploads binaries, they sign, CI downloads signed binaries.

### Options

| Service | Cost / yr | Notes |
|---|---|---|
| **SignPath.io** | Free tier available for open source; ~$150/yr for closed source small orgs | Best DX, native GitHub Actions integration, policy-based signing |
| **Certum SimplySign** | ~$150/yr EV | European CA; budget-friendly; decent automation |
| **DigiCert KeyLocker** | ~$400/yr | Enterprise-grade; tight integration with DigiCert HSM |
| **SSL.com eSigner** | ~$300/yr | Good support, widely used |

**SignPath is the default recommendation.** Their GitHub Action is first-class and free-tier friendly.

### SignPath workflow

1. Sign up at signpath.io. Create an organization.
2. Buy (or get from SignPath partners) an EV code signing certificate — SignPath manages it for you.
3. Create a project in SignPath for your app.
4. Create a signing policy that defines who can sign what.
5. Get credentials from SignPath → GitHub Secrets:
   - `SIGNPATH_ORG_ID`
   - `SIGNPATH_PROJECT_SLUG`
   - `SIGNPATH_SIGNING_POLICY_SLUG`
   - `SIGNPATH_API_TOKEN`

### Workflow YAML (additive to the Mac workflow from macos-deep-dive.md)

Add this step after electron-builder produces the unsigned Windows installer:

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
        run: |
          gh release upload ${{ github.ref_name }} signed-installer/*.exe
```

Note: you can also have electron-builder call SignPath directly via a custom signing hook if you want the installer uploaded already-signed in one step.

## Path 2 — Self-hosted EV hardware token

If you buy an EV cert directly from DigiCert/Sectigo/Comodo, they ship a **USB hardware token**. The private key never leaves the token. Signing requires physical access to a machine with the token plugged in.

**Consequence for CI:** GitHub's hosted Windows runners cannot use USB-attached hardware tokens. You need:
- A self-hosted Windows runner with the token plugged in, OR
- A third-party service that fronts the token for you (back to Path 1)

Unless you have a dedicated Windows release machine already running, **Path 1 is dramatically less pain.**

### If you do go self-hosted

1. Set up a Windows VM or physical machine as a [self-hosted GH Actions runner](https://docs.github.com/en/actions/hosting-your-own-runners/managing-self-hosted-runners/about-self-hosted-runners).
2. Install the signing vendor's driver (DigiCert SafeNet, etc.).
3. Plug in the token. Unlock with its password (stored as GH secret).
4. Use `signtool.exe` via electron-builder's built-in Windows signing config:

```yaml
win:
  certificateSubjectName: "Donjon Intelligence Systems"
  signingHashAlgorithms:
    - sha256
```

electron-builder finds the cert by subject name and uses signtool.

## Path 3 — Standard (OV) Code Signing — NOT RECOMMENDED for new apps

Cheaper ($80–150/yr), no hardware token needed. But SmartScreen still warns users until your cert builds reputation. Reputation comes from install count. For a brand-new app with no users yet, this creates a chicken-and-egg: users don't install because of the warning, so reputation doesn't build.

Use this only if:
- You have thousands of existing users who'll install regardless of the warning
- You're migrating from no signing (OV is strictly better than nothing)

## Installer target — `nsis` vs `nsis-web` vs `msi`

| Target | Installer size | Download UX | Auto-update compatible | Use when |
|---|---|---|---|---|
| `nsis` | Larger (~150MB+) | User downloads everything upfront | ✅ Yes | Default choice |
| `nsis-web` | Tiny stub (~1MB) | Downloads full installer on first run | ✅ Yes | You want a small download for bandwidth-sensitive users |
| `msi` | Variable | Native Windows installer | ❌ **No** — fights with electron-updater | Avoid for auto-updating apps |

**Default for Donjon work: `nsis`** — simplest, most predictable behavior.

## Common Windows signing errors

### "SignerSign() failed" with error 0x80092004

Signing cert not found in the store. Either wrong subject name, or cert isn't installed on the runner.

### "The specified timestamp server could not be reached"

electron-builder uses a timestamp server by default (Comodo / DigiCert). If blocked, configure an alternate:

```yaml
win:
  signtoolOptions:
    signingHashAlgorithms: ["sha256"]
    timeStampServer: "http://timestamp.digicert.com"
```

### SmartScreen warning despite EV signing

Reputation still needs ~24 hours to propagate after a new cert is issued. Wait a day, try again.

### "SignPath signing request failed: policy X rejected"

Your SignPath policy doesn't allow signing this artifact. Check policy-slug matches what the project expects.

## Before every Windows release

- Verify cert is still valid (SignPath dashboard or token inspection)
- Test-install the signed installer on a clean Windows VM — confirm no SmartScreen warning
- Sanity-check the installer size; a bloated installer often means unnecessary files got packed

## Donjon-specific notes

(To be populated after first Donjon Windows release)

- Which signing path we ended up using
- App ID / cert subject name
- Any quirks
