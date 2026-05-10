# Donjon Agency Workspace Audit

**Date:** 2026-04-12
**Path:** `/Users/clay/Desktop/donjon.agency`
**Total items at root:** ~74 (files + dirs)

---

## Directory Inventory

### Root-Level Directories

| Directory | Size | Last Modified | Notes |
|-----------|------|---------------|-------|
| `ARCHIVE/` | 764 MB | Apr 7 | Formal archive folder — old daemon versions |
| `(ARCHIVE)agent-files/` | 48 MB | Feb 28 | Old agent configs, setup packages, zips |
| `Agents/` | 58 MB | Apr 11 | Active agent workspaces (Chef, Dondog, Alfie) |
| `Donjon_Daemon/` | 32 KB | Apr 10 | Board meeting notes, council reports |
| `docs/` | 652 KB | Apr 7 | System docs, specs, guides |
| `sales/` | 372 KB | Mar 31 | Sales docs, outreach, collateral |
| `reports/` | 1.4 MB | Mar 17 | Historical reports (billy, kitchen, servicepro) |
| `skills/` | 72 MB | Mar 27 | Local skills library (65 skills) |
| `website/` | 174 MB | Mar 17 | Astro site with node_modules |
| `commands/` | 124 KB | Feb 22 | Claude slash commands |
| `prompts/` | 128 KB | Feb 20 | Prompt library (agents, trading, general) |
| `hooks/` | 20 KB | Feb 20 | React hooks — tsx/ts files |
| `gremlin-deliverables/` | 88 KB | Apr 10 | Recent gremlin session output |
| `gremlin-results/` | ~8 KB | Apr 7 | One test result JSON |
| `memory/` | 168 KB | Apr 12 | Memory submodule (git repo) |
| `landfill-gas-dashboard/` | 672 KB | Mar 31 | Client project — HTML dashboard + screenshots |
| `n8n-workflows/` | 20 KB | Feb 20 | 3 n8n workflow JSONs |
| `plugins/` | 16 KB | Mar 15 | 1 plugin file |
| `assets/` | (small) | Mar 31 | Diagrams and images |
| `images/` | (small) | Apr 10 | Logo files |
| `anna/` | empty | Feb 28 | Empty directory |
| `workers/` | (small) | Mar 15 | (not listed, likely small) |
| `servicepro/` | (small) | Mar 15 | ServicePro-related files |
| `summaries/` | (small) | Mar 15 | Summaries |
| `output/` | (small) | Mar 11 | Misc output |
| `tasks/` | (small) | Mar 10 | Task files |
| `.opencode/` | 11 MB | Apr 11 | OpenCode config, agents, skills, soul, work |
| `.claude/` | (small) | Apr 12 | Claude worktrees |
| `.playwright-cli/` | 636 KB | Mar 27 | Playwright session logs/screenshots |
| `.pytest_cache/` | 16 KB | Mar 16 | pytest cache |
| `.sisyphus/` | 20 KB | Feb 24 | Sisyphus boulder/plans |
| `.clawhub/` | (small) | Mar 26 | ClawhHub lock file |
| `.letta/` | (small) | Mar 24 | Letta settings |
| `Private & Shared/` | (small) | Mar 13 | Shared files |
| `Private & Shared 2/` | (small) | Mar 14 | Duplicate shared folder |
| `Donjon_Images/` | (small) | Apr 3 | Image folder |

### Root-Level Files (Notable)

| File | Size | Notes |
|------|------|-------|
| `dd-automation-v2.excalidraw` | 8.7 MB | Large diagram — should be in `assets/diagrams/` |
| `kitchen+letta.png` | 7.5 MB | Large image at root |
| `forjacob.pdf` | 4.0 MB | Client-facing PDF — loose at root |
| `Donjon at Work copy for Jacob.pdf` | 794 KB | Client PDF — loose at root |
| `Donjon at Work.pdf` | 576 KB | Client PDF — loose at root |
| `todo-sync-management.png` | 446 KB | Loose artifact |
| `Donjonatworkfinal.zip` | 444 KB | Loose zip |
| `todo-sync-management.pdf` | 320 KB | Loose artifact |
| `ableton-dependency-graph-mvp.html` | 65 KB | Unrelated project at root |
| `affordable_mowing.png` | 60 KB | Completely unrelated image at root |
| `letta+kitchen-infographic.png` | 32 KB | Infographic — should be in assets/ |
| `donjon-bridge-funding.html` | 27 KB | Bridge funding deck |
| `donjon-bridge-funding-deck.html` | 23 KB | Duplicate? Same content? |
| `bridge-preview.svg` | 4.5 KB | Bridge funding asset |
| `bridge-funding-messages.md` | 6.8 KB | Fundraising notes |
| `Donjon_Agency_Pivot_Playbook.docx` | 13 KB | Strategy doc — should be in docs/ |
| `todo-sync-management.svg` | 106 KB | Loose artifact |
| `donjonatwork-editorsreport.zip` | 5.8 KB | Old zip |
| `CLAUDE.md` | 9.6 KB | Active — keep at root |
| `INDEX.md` | 5.7 KB | Active index — keep at root |
| `opencode.jsonc` | 1.6 KB | Config — keep at root |
| `.env` | 5.3 KB | Sensitive — keep at root, confirm in .gitignore |
| `tasks.md` | 137 KB | Very large tasks file |
| `tasks.md.guidelines.md` | 137 KB | Identical size to tasks.md — likely a misnamed duplicate |
| `tasks.md.backup` | 1.8 KB | Backup — archive or delete |
| `tasks-archive-2026-03-13.md` | 137 KB | Old tasks archive |
| `heartbeat.jsonl` | 6.6 KB | Old heartbeat log — archive |
| `soul.md` | 8.2 KB | Soul config — keep or move to `.opencode/` |
| `the-kitchen.md` | 59 KB | Large guide — should be in docs/ |
| `thekitchen.md` | 0 bytes | EMPTY FILE — delete |
| `test_env.py` | 709 bytes | Test script — cleanup or move to tests/ |
| `sandbox-config.json` | 263 bytes | Config — keep or move to .opencode/ |
| `agents alias` | 872 bytes | Alias file with space in name — messy |
| `ableton-dependency-graph-mvp.html` | 65 KB | Unrelated to agency work |
| `roi-playground.html` (in sales/) | 26 KB | Check if this is the right location |

---

## Key Problems Identified

### 1. Loose Files at Root (High Priority)
The root directory has ~40 loose files and 30+ directories — most should be organized into subdirectories:
- PDFs, ZIPs, PNGs, HTML files, SVG files all sitting at root
- Several appear to be client-facing deliverables (`forjacob.pdf`, `Donjon at Work*.pdf`)
- Some are clearly unrelated (`affordable_mowing.png`, `ableton-dependency-graph-mvp.html`)

### 2. Duplicate/Confusing Folder Names
- `(ARCHIVE)agent-files/` — parentheses naming convention is inconsistent with `ARCHIVE/` folder
- `Private & Shared/` and `Private & Shared 2/` — what's the difference?
- `Donjon_Daemon/` at root vs `ARCHIVE/Donjon_Daemon` — the root one is current (board/council notes), but its name is confusing
- `gremlin-deliverables/` and `gremlin-results/` — should probably be one folder
- `.opencode/work/billy-website` and `.opencode/work/billy-website 2` — duplicate with space

### 3. Empty / Stale Items
- `anna/` — completely empty directory (Feb 28 creation, never used)
- `thekitchen.md` — 0-byte empty file, a stub for `the-kitchen.md`
- `tasks.md.guidelines.md` — 137 KB file with `.guidelines.md` extension that exactly matches `tasks.md` in size — almost certainly a misnamed copy
- `tasks.md.backup` — small backup from March 23, can be archived
- `tasks-archive-2026-03-13.md` — dated archive, move to `ARCHIVE/`
- `.pytest_cache/` — test cache, safe to delete

### 4. Skills Folder has " copy" Duplicates
Inside `skills/`, many folders have names like `acquiring-skills copy`, `converting-mcps-to-skills copy` — these appear to be Finder duplicates, not intentional alternatives. Should be reviewed and cleaned up.

### 5. Heartbeat / Soul Logs Scattered
- `heartbeat.jsonl` at root
- `.opencode/soul/heartbeat.jsonl`, `.opencode/soul/heartbeat 2.jsonl`, `.opencode/soul/heartbeat-paused.jsonl`
- `ARCHIVE/Donjon_Daemon/` presumably contains more
- All log data should live in one canonical location

### 6. Bridge Funding Assets Spread Out
- `bridge-funding-messages.md` at root
- `bridge-preview.svg` at root
- `donjon-bridge-funding.html` at root
- `donjon-bridge-funding-deck.html` at root (are these the same?)
- These should all be in `sales/` or a dedicated `sales/bridge-funding/` subfolder

### 7. `website/` — Large and Possibly Stale
- 174 MB total, mostly `node_modules` (250 directories)
- Last modified Mar 17 — not recently active
- `node_modules` should never be in the workspace root, but it's inside the website project, which is fine if the project is active. If inactive, the whole folder could be archived after removing node_modules.

---

## Proposed Reorganization Plan

### Actions — Root Cleanup

| Action | Item | Destination |
|--------|------|-------------|
| MOVE | `dd-automation-v2.excalidraw` | `assets/diagrams/` |
| MOVE | `kitchen+letta.png` | `assets/images/` |
| MOVE | `letta+kitchen-infographic.png` | `assets/images/` |
| MOVE | `todo-sync-management.pdf/.png/.svg` (3 files) | `assets/diagrams/` or `ARCHIVE/` |
| MOVE | `Donjon at Work.pdf`, `Donjon at Work copy for Jacob.pdf`, `forjacob.pdf` | `sales/collateral/` |
| MOVE | `Donjonatworkfinal.zip`, `donjonatwork-editorsreport.zip` | `ARCHIVE/deliverables/` |
| MOVE | `bridge-funding-messages.md`, `bridge-preview.svg`, `donjon-bridge-funding.html`, `donjon-bridge-funding-deck.html` | `sales/bridge-funding/` |
| MOVE | `Donjon_Agency_Pivot_Playbook.docx` | `docs/` |
| MOVE | `the-kitchen.md` | `docs/` |
| MOVE | `soul.md` | `.opencode/` (already has a soul.md there — reconcile) |
| MOVE | `tasks-archive-2026-03-13.md` | `ARCHIVE/` |
| MOVE | `heartbeat.jsonl` | `ARCHIVE/` (old log) |
| MOVE | `sandbox-config.json` | `.opencode/` or `docs/config/` |
| MOVE | `test_env.py` | `Donjon_Daemon/` or delete if stale |
| MOVE | `ableton-dependency-graph-mvp.html` | `ARCHIVE/` or separate projects folder |
| MOVE | `affordable_mowing.png` | `ARCHIVE/misc/` or delete (unrelated) |
| MOVE | `agents alias` (file with space in name) | Rename to `agents-alias.sh` and move to `commands/` or delete |
| DELETE | `thekitchen.md` | 0 bytes — empty file |
| REVIEW | `tasks.md.guidelines.md` | Likely duplicate of tasks.md — verify and delete |
| ARCHIVE | `tasks.md.backup` | Move to `ARCHIVE/` |
| DELETE | `.pytest_cache/` | Safe to remove — regenerated on test run |
| DELETE | `anna/` | Empty directory |

### Actions — Folder Consolidation

| Action | Item | Notes |
|--------|------|-------|
| MERGE | `gremlin-deliverables/` + `gremlin-results/` | Into single `gremlin-output/` folder |
| RENAME | `(ARCHIVE)agent-files/` | Move contents into `ARCHIVE/agent-files/` to match naming convention |
| REVIEW | `Private & Shared/` vs `Private & Shared 2/` | Determine if one is a duplicate; merge or delete the older |
| RENAME | `Donjon_Daemon/` at root | Consider renaming to `council/` or `board/` — it only contains board/council meeting notes now |
| DELETE | `.opencode/work/billy-website 2/` | Likely Finder duplicate of `billy-website/` |
| REVIEW | `.opencode/soul/heartbeat 2.jsonl` | Finder duplicate artifact — reconcile with `heartbeat.jsonl` |

### Actions — Skills Folder Cleanup

The `skills/` directory has many folders with ` copy` suffix (Finder duplicates):
- `acquiring-skills copy`
- `converting-mcps-to-skills copy`
- `creating-skills copy`
- `defragmenting-memory copy`
- `finding-agents copy`
- `initializing-memory copy`
- `messaging-agents copy`
- `migrating-from-codex-and-claude-code copy`
- `migrating-memory copy`
- `searching-messages copy`
- `syncing-memory-filesystem copy`
- `working-in-parallel copy`

**Recommendation:** For each, compare to the original. If identical, delete the copy. If different, reconcile and keep one version with a meaningful name.

### Actions — Website

- If the website project is no longer actively developed, run `rm -rf website/node_modules` and move the whole `website/` folder to `ARCHIVE/` — saves ~170 MB.
- If still active, leave in place but consider moving to a dedicated `projects/` directory to separate it from agency operations.

---

## Proposed Target Structure

```
donjon.agency/
├── CLAUDE.md                    # Keep at root
├── INDEX.md                     # Keep at root
├── opencode.jsonc               # Keep at root
├── .env                         # Keep at root (sensitive)
├── .gitignore                   # Keep at root
│
├── Agents/                      # Active agent workspaces
│   ├── Chef/
│   ├── Dondog/
│   ├── alfie-agent/
│   └── sub-agents/
│
├── council/                     # (renamed from Donjon_Daemon/)
│   ├── board-meeting_2026-04-08.md
│   ├── board-meeting_2026-04-10.md
│   ├── council_report_2026-04-07.md
│   └── council_tasks_2026-04-10.json
│
├── docs/                        # All documentation
│   ├── (existing docs)
│   ├── the-kitchen.md           # moved from root
│   ├── Donjon_Agency_Pivot_Playbook.docx  # moved from root
│   └── ...
│
├── sales/                       # All sales & revenue
│   ├── bridge-funding/          # (consolidated from root)
│   │   ├── bridge-funding-messages.md
│   │   ├── bridge-preview.svg
│   │   ├── donjon-bridge-funding.html
│   │   └── donjon-bridge-funding-deck.html
│   ├── collateral/              # Client PDFs
│   │   ├── Donjon at Work.pdf   # moved from root
│   │   ├── Donjon at Work copy for Jacob.pdf
│   │   └── forjacob.pdf
│   └── (existing: outreach, case-studies, etc.)
│
├── assets/                      # All media/diagrams
│   ├── diagrams/
│   │   ├── dd-automation-v2.excalidraw  # moved from root
│   │   └── todo-sync-management.*       # moved from root
│   └── images/
│       ├── kitchen+letta.png            # moved from root
│       └── letta+kitchen-infographic.png
│
├── gremlin-output/              # (merged: gremlin-deliverables/ + gremlin-results/)
│
├── memory/                      # Memory submodule
│
├── skills/                      # Skills library (clean up copy duplicates)
│
├── commands/                    # Claude slash commands
│
├── prompts/                     # Prompt library
│
├── plugins/                     # Plugin files
│
├── n8n-workflows/               # Automation workflows
│
├── reports/                     # Historical reports
│
├── website/                     # Agency website (or archive if stale)
│
├── tasks.md                     # Active task list
│
├── ARCHIVE/                     # All archived content
│   ├── agent-files/             # (from (ARCHIVE)agent-files/)
│   ├── Donjon_Daemon/           # Old daemon versions
│   ├── deliverables/            # Old zips and deliverables
│   │   ├── Donjonatworkfinal.zip
│   │   └── donjonatwork-editorsreport.zip
│   ├── tasks-archive-2026-03-13.md
│   ├── heartbeat.jsonl
│   └── ...
│
└── .opencode/                   # OpenCode tooling (keep as-is internally)
```

---

## Quick Wins (Safe to do immediately)

1. Delete `anna/` — empty directory
2. Delete `thekitchen.md` — 0-byte empty file
3. Delete `.pytest_cache/` — regenerable cache
4. Review and likely delete `tasks.md.guidelines.md` — appears to be a misnamed duplicate
5. Archive `tasks.md.backup` and `tasks-archive-2026-03-13.md`
6. Move all bridge-funding files into `sales/bridge-funding/`
7. Move client PDFs into `sales/collateral/`
8. Delete or archive `affordable_mowing.png` (unrelated)
9. Rename `(ARCHIVE)agent-files/` to `ARCHIVE/agent-files/`
10. Remove ` copy` skills folders after confirming they're exact duplicates

## Estimated Space Recovery

| Action | Estimated Savings |
|--------|------------------|
| `website/node_modules` (if archived) | ~170 MB |
| `ARCHIVE/` slim-down (old .venv, etc.) | potentially 100+ MB |
| Playwright CLI logs/screenshots | ~636 KB |
| Pytest cache | ~16 KB |
| Total without website | ~5–10 MB of clutter removed |
| Total with website archive | ~175 MB |
