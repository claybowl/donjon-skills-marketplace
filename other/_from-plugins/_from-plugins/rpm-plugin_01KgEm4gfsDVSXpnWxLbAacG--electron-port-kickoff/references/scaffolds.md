# Electron Scaffold Comparison

Deeper read on which scaffold to fork. Refer here when `electron-port-kickoff`'s decision table needs justification or the stack doesn't fit the defaults.

## The candidates

### `luanroger/electron-shadcn` — **primary recommendation for Donjon work**

**Stack:** Electron + Vite + TypeScript + React + Tailwind + shadcn/ui + CI/CD
**Trust score (Context7):** 9.9
**Good for:** Modern React apps with shadcn-based UI (which is most of Donjon's internal tooling)
**Ships with:** Preconfigured GitHub Actions workflow, sample IPC patterns, Tailwind config, shadcn components

**Pros:**
- Near-1:1 fit for Doer's UI stack
- CI is already wired (GH Actions matrix for Mac/Win)
- Follows modern Electron security defaults (`contextIsolation: true`, sandboxed renderer)
- Active maintenance

**Cons:**
- Opinionated on shadcn — if your existing app uses Mantine / Chakra / Radix directly, there's config friction
- Not the most "canonical" Electron setup; Forge people may grumble

### `electron-vite/electron-vite-react`

**Stack:** Electron + Vite + TypeScript + React + Sass (Tailwind not default)
**Good for:** React apps that don't use shadcn/ui
**Ships with:** Minimal scaffold, HMR for main and renderer

**Pros:**
- Canonical Vite + Electron + React
- Lower opinion surface — easier to bend to your stack
- Well-documented

**Cons:**
- You provide the UI kit (Tailwind, shadcn, etc.) yourself
- CI is not preconfigured — you wire GH Actions yourself

### `electron-vite/electron-vite-vue`

**Stack:** Same as React variant, Vue flavor
**Good for:** Vue apps (obvious fit)

### `alex8088/electron-vite` (the base)

**Stack:** Electron + Vite, framework-agnostic
**Good for:** Svelte, Solid, vanilla — anything not covered by the framework-specific variants
**Trust score:** 9.1

Start here and pick your own framework.

### `electron/forge` — **only if you need Forge's plugin ecosystem**

**Stack:** Electron Forge — the officially-maintained all-in-one build pipeline
**Trust score:** 10
**Good for:** Teams that want the canonical officially-blessed setup, or projects that will grow to need Forge's plugin architecture

**Pros:**
- Officially maintained by the Electron team
- Plugin system for custom loaders, publishers, makers
- Biggest long-term support horizon

**Cons:**
- Heavier; more config surface
- You wire more yourself (UI framework, CI, etc.)
- Slower to get to "binary on desktop" than a preconfigured scaffold

### Others worth knowing about (but don't default to)

- `dromara/electron-egg-docs` — enterprise-focused, heavier, good for multi-window apps with complex native integration
- `guasam/electrovite-react` — another React+Vite+Electron scaffold; less active
- `websites/dev_overwolf_ow-electron` — if you're building in-game overlays (not your problem 99% of the time)

## Decision shortcut

If your target app uses **Vite + React + Tailwind + shadcn**, stop reading and fork `luanroger/electron-shadcn`. That's the whole decision.

If it uses **Vite + React** but not shadcn, use `electron-vite/electron-vite-react`.

If it uses **Vue / Svelte / Solid**, use the corresponding `electron-vite` variant.

If you're building something ambitious that will outgrow a simple scaffold within 6 months, or you want the "this is the official way" comfort, use `electron/forge`.

## What to change after forking

Regardless of which scaffold you pick, audit these in the first hour:

1. **`package.json` name, version, description** — set to your project's values
2. **`electron-builder.yml` (or `build` block)** — set `appId`, `productName`, `publish` target
3. **Icon assets** — every scaffold ships with a placeholder icon; replace before your first release
4. **GitHub Actions workflow** — review triggers, node version, runner images
5. **CSP (Content Security Policy)** — scaffolds often have a permissive dev CSP; tighten for production

## If the scaffold breaks on first run

Common culprits:

- **Node version mismatch.** Scaffolds often require Node 18+ or 20+. Use `nvm use`.
- **Xcode Command Line Tools missing (Mac).** `xcode-select --install`.
- **Python missing (for node-gyp).** macOS ships Python 3; some scaffolds want Python 2 for older native deps. Install `python-setuptools` via brew if you hit this.
- **pnpm version.** Scaffolds pin a pnpm version via packageManager field. `corepack enable` then `corepack prepare pnpm@<version> --activate`.
- **Windows native module build tools.** Run `npm install --global windows-build-tools` on Windows, or use `pnpm rebuild` after install.

## War stories (to be filled in after shipping Doer)

- _Scaffold X failed because…_
- _Scaffold Y's CI workflow needed…_
- _The first Mac build blew up because…_

Add field notes here after each Donjon port completes.
