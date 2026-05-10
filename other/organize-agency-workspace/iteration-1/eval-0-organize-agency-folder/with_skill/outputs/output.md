# Agency Folder Audit & Reorganization Proposal

_Target: `/Users/clay/Desktop/donjon.agency`_
_Audit date: 2026-04-12_
_Phase: 0-2 complete. Awaiting approval before any files are moved._

---

## Phase 0 — Target Confirmed

Directory: `/Users/clay/Desktop/donjon.agency`

---

## Phase 1 — Audit Summary

### File Counts by Type / Area

| Category | Count (approx) | Notes |
|----------|----------------|-------|
| Markdown docs (`.md`) | ~180 | Scattered across root, reports, sales, agents, docs |
| JSON files (`.json`, `.jsonl`, `.jsonc`) | ~30 | Config, prompts, gremlin results, workflows |
| Python files (`.py`) | ~3 | `test_env.py` at root, others in ARCHIVE |
| Images (`.png`, `.svg`, `.jpg`) | ~15 | Root, assets/, images/, Donjon_Images (empty) |
| HTML files (`.html`) | ~10 | Root, docs, sales/tools, landfill-gas-dashboard |
| PDFs (`.pdf`) | ~12 | Root, agents, docs, skills |
| ZIPs/Archives (`.zip`) | ~4 | Root, (ARCHIVE) folder |
| `.docx` / Office files | ~1 | Root — `Donjon_Agency_Pivot_Playbook.docx` |
| `.excalidraw` diagrams | ~6 | Root and assets/diagrams |
| TypeScript / source code | ~10+ | Agents/Dondog, website, hooks |
| Skills (SKILL.md folders) | ~55+ | `skills/` directory |
| Node modules | Large | `website/node_modules`, `Agents/Dondog/node_modules`, etc. |

### Files Sitting Directly at Root (Misplaced)

These files are at the top level and need homes:

- `Donjon at Work.pdf` — deliverable PDF
- `Donjon at Work copy for Jacob.pdf` — deliverable, named recipient
- `forjacob.pdf` — deliverable for Jacob
- `Donjonatworkfinal.zip` — deliverable zip
- `donjonatwork-editorsreport.zip` — deliverable zip
- `Donjon_Agency_Pivot_Playbook.docx` — internal strategy doc
- `ableton-dependency-graph-mvp.html` — project artifact (Ableton MVP)
- `dd-automation-v2.excalidraw` — diagram
- `donjon-bridge-funding-deck.html` — pitch deck
- `donjon-bridge-funding.html` — pitch deck
- `bridge-funding-messages.md` — outreach/funding notes
- `bridge-preview.svg` — asset for funding deck
- `heartbeat.jsonl` — live agent data log
- `soul.md` — agent persona/system doc
- `the-kitchen.md` — internal playbook doc
- `thekitchen.md` — empty duplicate of above
- `tasks.md` — active task tracker
- `tasks.md.backup` — backup of tasks file
- `tasks.md.guidelines.md` — meta doc about tasks
- `tasks-archive-2026-03-13.md` — archived tasks
- `test_env.py` — stray Python script
- `sandbox-config.json` — config file
- `agents alias` — stray alias file
- `affordable_mowing.png` — client image (likely Billy or a prospect)
- `kitchen+letta.png` — internal infographic
- `letta+kitchen-infographic.png` — duplicate infographic
- `todo-sync-management.pdf` / `.png` / `.svg` — diagram trio at root
- `INDEX.md` — keep at root (correct location per taxonomy)
- `opencode.jsonc` — agent config (correct at root)
- `CLAUDE.md` — agent config (correct at root)

### Files with "final", "v2", "FINAL", "copy", "backup" in Name

- `Donjon at Work copy for Jacob.pdf` — deliverable copy
- `Donjonatworkfinal.zip` — final deliverable
- `dd-automation-v2.excalidraw` — v2 diagram
- `tasks.md.backup` — backup file
- `CLAY_WAKE_UP_ALFIE_GREMLINS_FINAL_2026-03-07.md` — in Agents/Chef
- `SERVICEPRO_FINAL_REPORT_CHEF_2025-02-25.md` — in Agents/Chef
- `SERVICEPRO_FINAL_TEST_CYCLE_REPORT_2026-02-26.md` — in Agents/Chef
- `hvac-automation-example-v2.md` — in sales/case-studies
- Many reports with "FINAL" in name in `reports/` subtrees

### Empty Directories (Candidates for Removal)

- `Donjon_Images/` — completely empty
- `Private & Shared/` — completely empty
- `tasks/` — completely empty
- `anna/` — completely empty
- `output/playwright` — appears empty or near-empty

### Archive Candidates (90+ days old, not recently modified)

Files not modified since ~Jan 12, 2026 (90 days before audit date):

- Everything in `(ARCHIVE)agent-files/` — already marked archive, last touched months ago
- Everything in `ARCHIVE/` subdirectories — already archive, fold into `archive/<year>/`
- `sales/CLAY_ACTION_*` files with dates in Feb-Mar 2026 — completed action items
- `reports/kitchen-checks/` — daily check reports from Feb-Mar 2026
- `reports/t-0027/` — all status reports from Mar 2026
- `reports/servicepro/` — test cycle reports from Feb-Mar 2026
- `reports/executive-summaries/` — reports from Mar 2026
- `docs/NOTION-LINEAR-SYNC.md` — Linear was removed from active use
- `docs/LETTA-MASTER-GUIDE.md`, `LETTA-MEMORY-SETUP-SUMMARY.md` — may be outdated
- `heartbeat.jsonl` — live log file, should move to a logs/ or archive location
- `tasks-archive-2026-03-13.md` — explicitly archived tasks
- `Agents/Chef/` reports — all from Feb-Mar 2026, stale

### Structural Issues

1. **Two archive folders exist** at root: `ARCHIVE/` and `(ARCHIVE)agent-files/` — these should merge into one `archive/` with year subfolders.
2. **`reports/` is large but well-organized** — keep in place, but archive the dated subdirs.
3. **`skills/` folder has many "copy" variants** (`acquiring-skills copy`, `creating-skills copy`, etc.) — these should be renamed or cleaned up.
4. **`Private & Shared 2/`** contains a Notion export and an AI-generated image — misplaced.
5. **`hooks/`** contains React hook files (`use-mobile.tsx`, `use-toast.ts`) — likely belong to the website project.
6. **Duplicate infographics** at root: `kitchen+letta.png` and `letta+kitchen-infographic.png`.

---

## Phase 2 — Proposed Structure

```
donjon.agency/
├── CLAUDE.md              (keep — harness config)
├── INDEX.md               (keep — auto-generated index)
├── opencode.jsonc         (keep — agent config)
├── clients/
│   └── jacob/
│       └── deliverables/  (PDFs and zips sent to Jacob)
├── projects/
│   ├── donjon-daemon/     (active Donjon_Daemon working files)
│   ├── ableton/           (ableton MVP artifact)
│   ├── bridge-funding/    (pitch deck files)
│   └── website/           (existing website/ folder)
├── assets/
│   ├── diagrams/          (existing — keep)
│   └── images/            (existing + root images)
├── docs/                  (existing — keep)
├── agents/                (consolidate Agents/ → agents/)
├── sales/                 (existing — keep structure)
├── skills/                (existing — keep)
├── reports/               (existing — keep; archive dated subdirs)
├── memory/                (existing — keep)
└── archive/
    ├── 2025/
    └── 2026/
        ├── agent-files/   (from (ARCHIVE)agent-files/)
        ├── donjon-daemon/ (from ARCHIVE/Donjon_Daemon)
        ├── lettabot/      (from ARCHIVE/lettabot)
        ├── donjon-org/    (from ARCHIVE/donjon_org)
        └── reports/       (all kitchen-checks, t-0027, servicepro, etc.)
```

---

## Proposed Move List

### Group 1: Root Files → clients/jacob/deliverables/

| Before | After |
|--------|-------|
| `Donjon at Work.pdf` | `clients/jacob/deliverables/Donjon at Work.pdf` |
| `Donjon at Work copy for Jacob.pdf` | `clients/jacob/deliverables/Donjon at Work copy for Jacob.pdf` |
| `forjacob.pdf` | `clients/jacob/deliverables/forjacob.pdf` |
| `Donjonatworkfinal.zip` | `clients/jacob/deliverables/Donjonatworkfinal.zip` |
| `donjonatwork-editorsreport.zip` | `clients/jacob/deliverables/donjonatwork-editorsreport.zip` |
| `Private & Shared 2/` (entire folder) | `clients/jacob/deliverables/notion-export/` |

### Group 2: Root Files → projects/bridge-funding/

| Before | After |
|--------|-------|
| `donjon-bridge-funding-deck.html` | `projects/bridge-funding/donjon-bridge-funding-deck.html` |
| `donjon-bridge-funding.html` | `projects/bridge-funding/donjon-bridge-funding.html` |
| `bridge-funding-messages.md` | `projects/bridge-funding/bridge-funding-messages.md` |
| `bridge-preview.svg` | `projects/bridge-funding/bridge-preview.svg` |

### Group 3: Root Files → projects/ableton/

| Before | After |
|--------|-------|
| `ableton-dependency-graph-mvp.html` | `projects/ableton/ableton-dependency-graph-mvp.html` |

### Group 4: Root Files → projects/donjon-daemon/

| Before | After |
|--------|-------|
| `Donjon_Daemon/` (entire active folder) | `projects/donjon-daemon/` |
| `heartbeat.jsonl` | `projects/donjon-daemon/heartbeat.jsonl` |

### Group 5: Root Files → assets/

| Before | After |
|--------|-------|
| `dd-automation-v2.excalidraw` | `assets/diagrams/dd-automation-v2.excalidraw` |
| `todo-sync-management.pdf` | `assets/diagrams/todo-sync-management.pdf` |
| `todo-sync-management.png` | `assets/diagrams/todo-sync-management.png` |
| `todo-sync-management.svg` | `assets/diagrams/todo-sync-management.svg` |
| `kitchen+letta.png` | `assets/images/kitchen+letta.png` |
| `letta+kitchen-infographic.png` | `assets/images/letta+kitchen-infographic.png` _(flag as possible duplicate)_ |
| `affordable_mowing.png` | `assets/images/affordable_mowing.png` |
| `images/` (entire folder) | `assets/images/logos/` _(merge into assets/images)_ |

### Group 6: Root Files → docs/

| Before | After |
|--------|-------|
| `soul.md` | `docs/soul.md` |
| `the-kitchen.md` | `docs/the-kitchen.md` |
| `Donjon_Agency_Pivot_Playbook.docx` | `docs/Donjon_Agency_Pivot_Playbook.docx` |

### Group 7: Root Files → agents/

| Before | After |
|--------|-------|
| `Agents/` (entire folder) | `agents/` _(rename Agents → agents)_ |
| `agents alias` | `agents/agents-alias` _(rename, move into agents)_ |
| `plugins/` | `agents/plugins/` |
| `commands/` | `agents/commands/` |
| `prompts/` | `agents/prompts/` |
| `n8n-workflows/` | `agents/n8n-workflows/` |
| `hooks/` | `website/src/hooks/` _(React hooks belong with website project)_ |
| `gremlin-results/` | `agents/gremlin-results/` |
| `gremlin-deliverables/` | `agents/gremlin-deliverables/` |

### Group 8: Root Files → projects/

| Before | After |
|--------|-------|
| `landfill-gas-dashboard/` | `projects/landfill-gas-dashboard/` |
| `servicepro/` | `projects/servicepro/` |

### Group 9: Root Files → archive/2026/

| Before | After |
|--------|-------|
| `tasks-archive-2026-03-13.md` | `archive/2026/tasks-archive-2026-03-13.md` |
| `tasks.md.backup` | `archive/2026/tasks.md.backup` |
| `tasks.md.guidelines.md` | `archive/2026/tasks.md.guidelines.md` |
| `test_env.py` | `archive/2026/test_env.py` |
| `sandbox-config.json` | `archive/2026/sandbox-config.json` |

### Group 10: Merge Existing ARCHIVE Folders → archive/

| Before | After |
|--------|-------|
| `ARCHIVE/Donjon_Daemon/` | `archive/2025/donjon-daemon/` |
| `ARCHIVE/Donjon.Daemon.v3/` | `archive/2025/donjon-daemon-v3/` |
| `ARCHIVE/Donjon.Daemon.v3_theTower/` | `archive/2025/donjon-daemon-v3-the-tower/` |
| `ARCHIVE/Donjon_Daemon_theTower/` | `archive/2025/donjon-daemon-the-tower/` |
| `ARCHIVE/lettabot/` | `archive/2025/lettabot/` |
| `ARCHIVE/lettabot_theTower/` | `archive/2025/lettabot-the-tower/` |
| `ARCHIVE/donjon_org/` | `archive/2025/donjon-org/` |
| `ARCHIVE/DONJON_DAEMON_DIAGNOSTICS_REPORT.md` | `archive/2025/DONJON_DAEMON_DIAGNOSTICS_REPORT.md` |
| `(ARCHIVE)agent-files/` (entire folder) | `archive/2025/agent-files/` |

### Group 11: Dated Reports → archive/2026/reports/

| Before | After |
|--------|-------|
| `reports/kitchen-checks/2026-02-*/` through `2026-03-*/` | `archive/2026/reports/kitchen-checks/` |
| `reports/kitchen-checks/CHEF_KITCHEN_CHECK_*.md` | `archive/2026/reports/kitchen-checks/` |
| `reports/t-0027/` (all files) | `archive/2026/reports/t-0027/` |
| `reports/servicepro/` (all files) | `archive/2026/reports/servicepro/` |
| `reports/executive-summaries/` (all files) | `archive/2026/reports/executive-summaries/` |
| `reports/dondog/` (all files) | `archive/2026/reports/dondog/` |
| `reports/billy/` (all files — note: duplicates with " 2" suffix exist) | `archive/2026/reports/billy/` |
| `reports/service-pro/` (all files) | `archive/2026/reports/service-pro/` |
| `Agents/Chef/SERVICEPRO_*.md` files | `archive/2026/reports/chef-service-pro/` |

### Group 12: Empty Directories to Remove

| Directory | Action |
|-----------|--------|
| `Donjon_Images/` | Delete (empty) |
| `Private & Shared/` | Delete (empty) |
| `tasks/` | Delete (empty) |
| `anna/` | Delete (empty) |
| `summaries/D.D. Heartbeat Orchestrator` | Review — appears to be a stray alias/shortcut |

### Group 13: Skills Cleanup (Lower Priority)

| Before | After |
|--------|-------|
| `skills/acquiring-skills copy/` | `skills/acquiring-skills/` _(remove " copy" suffix)_ |
| `skills/converting-mcps-to-skills copy/` | `skills/converting-mcps-to-skills/` |
| `skills/creating-skills copy/` | `skills/creating-skills/` |
| `skills/defragmenting-memory copy/` | `skills/defragmenting-memory/` |
| `skills/finding-agents copy/` | `skills/finding-agents/` |
| `skills/initializing-memory copy/` | `skills/initializing-memory/` |
| `skills/messaging-agents copy/` | `skills/messaging-agents/` |
| `skills/migrating-from-codex-and-claude-code copy/` | `skills/migrating-from-codex-and-claude-code/` |
| `skills/migrating-memory copy/` | `skills/migrating-memory/` |
| `skills/searching-messages copy/` | `skills/searching-messages/` |
| `skills/syncing-memory-filesystem copy/` | `skills/syncing-memory-filesystem/` |
| `skills/working-in-parallel copy/` | `skills/working-in-parallel/` |

---

## Items to Flag / Clarify Before Moving

1. **`tasks.md`** — This appears to be the active task tracker. Leave at root or move to `docs/`? Recommend leaving at root.
2. **`thekitchen.md`** — 0 bytes (empty). Safe to delete? Recommend deletion.
3. **`letta+kitchen-infographic.png` vs `kitchen+letta.png`** — Both are infographics likely from the same session. One may be a duplicate — check before moving.
4. **`reports/billy/` " 2" duplicates** — `BILLY_FIX_COMPLETE 2.txt`, `BILLY_WEBSITE_STATUS_REPORT_2026-03-04 2.md`, etc. These appear to be macOS copy-duplicates. Safe to delete the ` 2` copies?
5. **`ARCHIVE/Donjon.Daemon.v3_theTower/` and `Donjon_Daemon_theTower/`** — Both appear to be "The Tower" variants of the daemon. Confirm they're not the same thing before folding into archive.
6. **`landfill-gas-dashboard/`** — Client project? If so, which client? Currently treated as `projects/` since no client name is clear.
7. **`docs/know-defeat/` and `docs/know-defeat-trading-architecture.md`** — Appears to be a trading/investing client or project. Move to `clients/know-defeat/` if it's a client.
8. **`memory/`** — Active agent memory files. Do not archive — leave in place.
9. **`reports/heartbeat/`** — Empty or near-empty? Check before archiving.
10. **`Agents/sub-agents/`** — Contains a folder literally named `"Needs Work (#Dondog - Use  these as a template and turn them into gremlins!)"` — this is a working note masquerading as a folder name. Should be normalized.

---

## Summary Statistics

| Metric | Count |
|--------|-------|
| Files at root (misplaced) | ~33 |
| Empty directories to remove | 5 |
| Archive candidates (90+ days old) | ~100+ files |
| Skill folders with " copy" naming | 12 |
| Duplicate files (macOS " 2" copies) | ~8 |
| Existing archive folders to consolidate | 2 → 1 |

---

**Does this look right? I'll wait for your go-ahead before moving anything.**
