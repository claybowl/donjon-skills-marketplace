# electron-builder Configuration Cheat Sheet

Everything you need to configure `electron-builder` for a real release. Load this when the user is past the kickoff and ready to produce signed, distributable installers.

## Where config lives

Two equivalent formats:
- `electron-builder.yml` (recommended — cleaner for complex configs)
- `build` block inside `package.json`

Most scaffolds ship with one or the other preconfigured. Pick one; don't mix.

## Minimum viable electron-builder.yml

```yaml
appId: agency.donjon.doer
productName: Doer
copyright: Copyright © 2026 Donjon Intelligence Systems

directories:
  output: dist
  buildResources: build

files:
  - "out/**/*"
  - "package.json"

mac:
  category: public.app-category.developer-tools
  hardenedRuntime: true
  gatekeeperAssess: false
  entitlements: build/entitlements.mac.plist
  entitlementsInherit: build/entitlements.mac.plist
  notarize: true
  target:
    - target: dmg
      arch:
        - x64
        - arm64
    - target: zip
      arch:
        - x64
        - arm64

win:
  target:
    - target: nsis
      arch:
        - x64
  signingHashAlgorithms:
    - sha256

linux:
  target:
    - AppImage
    - deb
  category: Development

publish:
  provider: github
  owner: claybowl
  repo: Doer
  private: true
```

Replace `claybowl` / `Doer` / `agency.donjon.doer` with the target project's values.

## Key field reference

| Field | Purpose |
|---|---|
| `appId` | Reverse-DNS identifier. Used by macOS for app identity, Windows for upgrade detection. **Never change after shipping** — users with older versions won't upgrade cleanly. |
| `productName` | User-facing app name. Shows in Finder / Start Menu. |
| `files` | Glob patterns for files to include in the packaged app. |
| `directories.output` | Where packaged artifacts land. Default `dist/` or `out/`. |
| `directories.buildResources` | Where icons, entitlements, and installer assets live. Default `build/`. |
| `mac.hardenedRuntime` | **Must be `true`** for notarization to succeed. |
| `mac.entitlements` | Path to entitlements plist. Electron needs JIT entitlement. |
| `mac.notarize` | Set to `true` to trigger notarization. Requires `APPLE_ID` / `APPLE_APP_SPECIFIC_PASSWORD` / `APPLE_TEAM_ID` env vars. |
| `win.target` | `nsis` is the right default. `nsis-web` downloads the installer on first launch (smaller upload). Avoid `msi` — fights with auto-update. |
| `publish.provider` | `github`, `s3`, `bintray`, `generic`, `snapStore`, etc. `github` is the easy path. |

## Entitlements file (macOS)

`build/entitlements.mac.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
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
</dict>
</plist>
```

The scaffold usually provides this. **Do not delete.**

## Icons

Required formats:

| Platform | File | Min size | Notes |
|---|---|---|---|
| macOS | `build/icon.icns` | Multi-resolution (16/32/64/128/256/512/1024) | Use `png2icns` or `iconutil` to create |
| Windows | `build/icon.ico` | Multi-resolution (16/24/32/48/64/128/256) | Use an `.ico` converter |
| Linux | `build/icon.png` | 512×512 | electron-builder generates other sizes |

Tools:
- `electron-icon-builder` (CLI) — one command, all formats, from a single 1024×1024 PNG
- `iconutil` (macOS built-in) — for `.icns`

## Targets & arch combinations

**Mac:** `x64` for Intel, `arm64` for Apple Silicon. Modern default is both. DMG for distribution, ZIP for `electron-updater` deltas.

**Windows:** `x64` for modern machines. Add `ia32` only if you have users on 32-bit Windows (rare in 2026).

**Linux:** `AppImage` (universal), `deb` (Debian/Ubuntu), `rpm` (Fedora/RHEL), `snap` (Snap Store). AppImage is the safest default.

## Common gotchas

1. **Forgetting to update `appId` after forking the scaffold.** You'll end up shipping as `com.lionchena.shadcn` — bad branding, worse for upgrade detection.
2. **Including `node_modules/` in `files`.** Don't. electron-builder handles dependencies automatically.
3. **Setting `asar: false`.** Keep `asar: true` (default) — it's the packed archive format that makes packaging efficient. Turn off only if you have filesystem-sensitive code that can't read from an asar.
4. **Not configuring `asarUnpack`.** If any native module or binary needs real filesystem access (not an asar virtual FS), list it in `asarUnpack`. Most `better-sqlite3`/`keytar`/etc. setups need this.
5. **Forgetting `copyright`.** Required for Mac App Store; optional but good hygiene everywhere.

## Build commands

```sh
# Package for current platform (for dev testing)
pnpm exec electron-builder --dir

# Full installer for current platform
pnpm exec electron-builder

# Explicit platform/arch
pnpm exec electron-builder --mac dmg --x64 --arm64
pnpm exec electron-builder --win nsis --x64
pnpm exec electron-builder --linux AppImage

# Publish to configured provider (GH Releases)
pnpm exec electron-builder --publish always
```

## More to come

This file gets expanded as we learn. Planned additions after Doer ships:
- Real-world `files` glob patterns that work with monorepos
- PGlite-specific packaging notes
- Custom installer UI (NSIS scripts)
- Multi-arch Linux builds for ARM
