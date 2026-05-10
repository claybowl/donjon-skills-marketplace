# Scaffold Selection — Which Starter to Fork

Deeper read on choosing the right Electron scaffold to port your app into.

## Candidates

### `luanroger/electron-shadcn` — best default for modern React apps

**Stack:** Electron + Vite + TypeScript + React + Tailwind + shadcn/ui + CI/CD preconfigured
**Context7 trust score:** 9.9

**Good for:** React apps already using shadcn/ui, or ready to adopt it. Near-1:1 fit for most modern TypeScript React codebases.

**Ships with:**
- Preconfigured GitHub Actions workflow with matrix builds
- Sample IPC patterns via `contextBridge`
- Tailwind config, shadcn component library already wired
- Electron 28+ with modern security defaults (`contextIsolation: true`, sandboxed renderer)

**Pros:**
- Fastest time to a runnable signed binary
- CI wired end-to-end
- Active maintenance

**Cons:**
- Opinionated on shadcn — friction if your existing UI uses Mantine / Chakra / MUI
- Not the "canonical" Electron setup that purists prefer

### `electron-vite/electron-vite-react`

**Stack:** Electron + Vite + TypeScript + React + Sass (no Tailwind by default)

**Good for:** React apps that don't use shadcn, or teams that want minimal opinion.

**Pros:**
- Canonical Vite + Electron + React
- Lower opinion surface; easier to bend to your stack
- Well-documented

**Cons:**
- Provide your own UI kit (Tailwind, component library, etc.)
- CI not preconfigured — you wire GH Actions yourself

### `electron-vite/electron-vite-vue`

**Stack:** Same as React variant, Vue flavor.

**Good for:** Vue apps — the obvious fit.

### `alex8088/electron-vite` (framework-agnostic base)

**Stack:** Electron + Vite, no framework opinion.
**Context7 trust score:** 9.1

**Good for:** Svelte, Solid, Qwik, vanilla JS — anything not covered by framework-specific variants.

Start here and bring your own framework.

### `electron/forge` — the official all-in-one

**Stack:** Electron Forge — officially maintained by the Electron team.
**Context7 trust score:** 10

**Good for:** Teams that want the "officially blessed" setup, or projects that will grow to need Forge's plugin ecosystem (custom makers, publishers, loaders).

**Pros:**
- Officially maintained; longest support horizon
- Plugin system for custom build pipelines
- Most "canonical" Electron setup

**Cons:**
- Heavier; more config surface
- You wire UI framework, CI, etc. yourself
- Slower to "runnable binary" than a preconfigured scaffold

### Others worth knowing about (but don't default to)

- **`dromara/electron-egg-docs`** — Enterprise-focused, heavier. Good for multi-window apps with complex native integrations.
- **`guasam/electrovite-react`** — Another React + Vite + Electron scaffold; less active maintenance.
- **`discord/electron`** — Discord's fork; useful as a reference, not as a starter.

## Decision shortcut

- Modern React + Vite + Tailwind + shadcn? Stop reading. Fork `luanroger/electron-shadcn`.
- React + Vite without shadcn? `electron-vite/electron-vite-react`.
- Vue / Svelte / Solid + Vite? `electron-vite` variant for your framework.
- Long-term bet on a polished Electron architecture? `electron/forge`.

## What to change after forking

Regardless of scaffold, audit these in the first hour:

1. **`package.json`** — set `name`, `version`, `description`, `author`, `productName` to your project's values.
2. **`electron-builder.yml` (or `build` block)** — set `appId` (reverse-DNS, unique, don't change later), `productName`, `publish` target.
3. **Icon assets** — every scaffold ships with a placeholder icon. Replace before the first release.
4. **GitHub Actions workflow** — review triggers, Node version, runner images, and any hardcoded secrets names.
5. **Content Security Policy** — scaffolds often ship a permissive dev CSP; tighten for production.

## If the scaffold breaks on first run

Common culprits:

### Node version mismatch

Scaffolds pin a Node version (usually 18+ or 20+). Use `nvm use` or check the `packageManager` field in `package.json`.

### Xcode Command Line Tools missing (macOS)

```sh
xcode-select --install
```

### Python missing (for node-gyp)

macOS ships Python 3. Some native modules still expect `python2`. Install via brew if you hit this:
```sh
brew install python@3.11
```

For `node-gyp` itself:
```sh
npm install -g node-gyp
```

### pnpm version mismatch

Scaffolds pin pnpm via the `packageManager` field. Enable corepack and prepare the right version:
```sh
corepack enable
corepack prepare pnpm@9.0.0 --activate
```

### Windows native module build tools

On Windows, install Visual Studio Build Tools with "Desktop development with C++":
```powershell
winget install Microsoft.VisualStudio.2022.BuildTools
```

Or use:
```sh
pnpm rebuild
```

## How to port without losing your mind

When copying your existing app into the scaffold:

1. **Start with the renderer, not the main process.** Get the UI rendering inside the scaffold's `src/renderer/` first. Main process can come later.
2. **Preserve your Vite config carefully.** The scaffold has its own `vite.config.ts`; merge thoughtfully rather than overwriting.
3. **Move environment variables.** Existing `.env` files may use Vite's `VITE_` prefix for renderer access; main process gets env vars normally. Document both sets.
4. **Test packaged builds early and often.** Run `pnpm package` at least once a week during porting. Regressions against packaged mode hide easily in dev.
5. **Don't turn off `contextIsolation`.** Ever. It's the 2025 security default. Use `contextBridge.exposeInMainWorld` instead.
