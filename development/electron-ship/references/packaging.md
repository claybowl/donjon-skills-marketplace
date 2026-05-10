# Packaging — electron-builder Configuration Deep Dive

Complete reference for configuring `electron-builder` to produce signed, distributable installers. A copy-paste config is in `assets/electron-builder.yml`.

## Where config lives

Two equivalent formats:
- `electron-builder.yml` (recommended — cleaner for complex configs)
- `build` block inside `package.json`

Pick one; don't mix.

## Key fields reference

| Field | Purpose |
|---|---|
| `appId` | Reverse-DNS identifier (e.g., `com.example.myapp`). Used by macOS for app identity, Windows for upgrade detection. **Never change after shipping.** |
| `productName` | User-facing app name. Shows in Finder / Start Menu / dock. |
| `files` | Glob patterns for what to include in the packaged app. |
| `directories.output` | Where packaged artifacts land. Default `dist/`. |
| `directories.buildResources` | Where icons, entitlements, installer assets live. Default `build/`. |
| `asar` | Keep default `true`. Asar is the packed archive format that makes packaging efficient. |
| `asarUnpack` | Native modules or binaries that need real filesystem access (not virtual asar FS). |
| `mac.hardenedRuntime` | **Must be `true`** for Mac notarization. |
| `mac.entitlements` | Path to entitlements plist. Electron needs JIT entitlement. |
| `mac.notarize` | `true` to trigger notarization. Requires Apple credentials as env vars. |
| `win.target` | `nsis` (default) or `nsis-web`. **Never `msi`** — fights with electron-updater. |
| `linux.target` | `AppImage` (universal), `deb`, `rpm`, `snap`. |
| `publish.provider` | `github` (easiest), `s3`, `generic`, `snapStore`. |

## Platform targets and architectures

### macOS

- `x64` — Intel Macs
- `arm64` — Apple Silicon

Modern default: both. Ship a universal `.dmg` if your bundle supports it, or separate installers.

For auto-update, `electron-builder` needs the `.zip` target in addition to the `.dmg`:

```yaml
mac:
  target:
    - target: dmg
      arch: [x64, arm64]
    - target: zip
      arch: [x64, arm64]
```

### Windows

- `x64` — modern Windows
- `ia32` — 32-bit Windows (rare in 2026; skip unless you know you need it)

Installer options:

| Target | Installer size | Best for |
|---|---|---|
| `nsis` | Larger (~150MB+) | Default choice; user downloads complete installer |
| `nsis-web` | Tiny stub (~1MB) | Bandwidth-sensitive users; downloads main installer on first run |
| `portable` | Standalone exe | No-install single executable |
| `msi` | Variable | **Avoid** — fights with electron-updater |

### Linux

- `AppImage` — universal, self-contained
- `deb` — Debian / Ubuntu
- `rpm` — Fedora / RHEL
- `snap` — Snap Store

AppImage is the safest default for broad distribution.

## Entitlements (macOS)

`build/entitlements.mac.plist` — required for notarization. Example in `assets/entitlements.mac.plist`. Core entitlements Electron needs:

```xml
<key>com.apple.security.cs.allow-jit</key>
<true/>
<key>com.apple.security.cs.allow-unsigned-executable-memory</key>
<true/>
<key>com.apple.security.cs.disable-library-validation</key>
<true/>
<key>com.apple.security.network.client</key>
<true/>
<key>com.apple.security.network.server</key>
<true/>
```

**Don't delete these.** They're required for V8, native modules, and network access.

## Icons

Required formats per platform:

| Platform | File | Min size | Tool to generate |
|---|---|---|---|
| macOS | `build/icon.icns` | Multi-resolution (16 → 1024) | `iconutil` (built-in) or `png2icns` |
| Windows | `build/icon.ico` | Multi-resolution (16 → 256) | Online `.ico` converter |
| Linux | `build/icon.png` | 512×512 | Just a PNG |

**One-command tool:** `electron-icon-builder`. Pass a single 1024×1024 PNG and it generates all formats:

```sh
pnpm add -D electron-icon-builder
pnpm exec electron-icon-builder --input=./build/icon-source.png --output=./build --flatten
```

## The `files` field — what goes in the package

Default patterns work for most cases:

```yaml
files:
  - "out/**/*"       # built code
  - "package.json"
  - "!**/node_modules/*/{CHANGELOG.md,README.md,readme.md,*.d.ts}"
```

**Do not include `node_modules/`.** electron-builder handles dependencies automatically — explicitly listing `node_modules/**` doubles them into the package.

**Do include** the output directory of your build step (`out/`, `dist/`, or whatever your `pnpm build` produces).

**For monorepos**, you may need to explicitly include dependencies from workspace packages:

```yaml
files:
  - "out/**/*"
  - "packages/shared/dist/**/*"
  - "packages/server/dist/**/*"
  - "package.json"
```

## Build commands

```sh
# Package for current platform only (dev sanity check — no installer)
pnpm exec electron-builder --dir

# Full installer for current platform
pnpm exec electron-builder

# Explicit platform + arch
pnpm exec electron-builder --mac dmg --x64 --arm64
pnpm exec electron-builder --win nsis --x64
pnpm exec electron-builder --linux AppImage

# Build AND publish to GitHub Releases (requires GH_TOKEN in env)
pnpm exec electron-builder --publish always

# Cross-compile: can build Windows installers on macOS/Linux; cannot build Mac on non-Mac
pnpm exec electron-builder --win --linux
```

## Common gotchas

1. **Forgetting to update `appId` after forking the scaffold.** You'll ship as `com.luanroger.shadcn` — bad branding, worse for upgrade detection.
2. **Including `node_modules/` in `files`.** Don't. Dependencies get packed automatically via the `dependencies` block in `package.json`.
3. **Setting `asar: false`.** Keep `asar: true` unless you have code that can't read from a virtual FS. Then use `asarUnpack` for only those files.
4. **Missing `asarUnpack` for native modules.** If `better-sqlite3`, `keytar`, or similar are in your `dependencies`, add `"**/node_modules/<module-name>/**/*"` to `asarUnpack`.
5. **Forgetting `copyright`.** Required for Mac App Store; good hygiene everywhere else.
6. **Mismatched `productName` and `appId`.** `productName` is display only; `appId` is identity. Users see `productName`; OS tracks `appId`.
7. **Using `msi` on Windows.** MSI installers don't play with `electron-updater`. Always `nsis` or `nsis-web`.

## NSIS customization (Windows)

Common tweaks for the Windows installer:

```yaml
nsis:
  oneClick: false              # Show installer UI (vs. silent install)
  perMachine: false            # Per-user install (default; no UAC)
  allowElevation: true         # Allow user to opt in to per-machine
  allowToChangeInstallationDirectory: true
  createDesktopShortcut: true
  createStartMenuShortcut: true
  shortcutName: "Your App"
  include: "build/installer.nsh"   # Custom NSIS script hook
```

For silent enterprise-friendly installs: `oneClick: true, perMachine: true`.

## DMG customization (macOS)

```yaml
dmg:
  icon: "build/icon.icns"
  background: "build/dmg-background.png"   # 540x380 recommended
  contents:
    - x: 130
      y: 220
      type: file
    - x: 410
      y: 220
      type: link
      path: "/Applications"
  window:
    width: 540
    height: 380
```

The window layout controls where the app icon and `/Applications` shortcut appear when users open the DMG.

## Linux AppImage customization

```yaml
linux:
  target: AppImage
  category: Development
  desktop:
    Name: "Your App"
    Comment: "Your app description"
    Keywords: "productivity;developer;"
```
