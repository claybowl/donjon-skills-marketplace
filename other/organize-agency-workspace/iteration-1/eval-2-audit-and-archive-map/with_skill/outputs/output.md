# Agency File Index — Audit & Archive Map
_Generated: 2026-04-12 | Target: `/Users/clay/Desktop/donjon.agency`_
_Skill: organize-agency | Phase 0 + Phase 1 executed_

---

## Phase 0 — Target Confirmed

**Directory:** `/Users/clay/Desktop/donjon.agency`

---

## Phase 1 — Audit Summary

### Counts

| Category | Count |
|----------|-------|
| Total files (excl. hidden + node_modules) | ~1,265 |
| Markdown (.md) | 603 |
| TypeScript (.ts/.tsx) | 234 |
| Python (.py/.pyc) | 169 |
| JSON/JSONC/JSONL | 76 |
| HTML | 29 |
| PDF | 13 |
| ZIP | 4 |
| DOCX | 2 |
| Images (PNG, SVG, ICO) | 25 |
| Other (sh, yaml, excalidraw, etc.) | ~100 |

### Files Sitting Loose at Root (misplaced or ambiguous)

These files are directly in `/donjon.agency/` with no subdirectory — almost all should be moved or classified:

| File | Last Modified | Notes |
|------|--------------|-------|
| `CLAUDE.md` | 2026-04-03 | Agent config — stays at root (intentional) |
| `INDEX.md` | 2026-04-07 | Index — stays at root (intentional) |
| `opencode.jsonc` | 2026-04-07 | Dev config — stays at root (intentional) |
| `soul.md` | 2026-03-15 | Agency soul/persona doc — move to `docs/` |
| `tasks.md` | 2026-03-23 | Active task list — stays or move to `docs/` |
| `tasks.md.backup` | 2026-03-23 | Backup file — archive or delete |
| `tasks.md.guidelines.md` | 2026-03-23 | Meta-doc — move to `docs/` |
| `tasks-archive-2026-03-13.md` | 2026-03-15 | Archived tasks — move to `archive/2026/` |
| `the-kitchen.md` | 2026-03-15 | Duplicate of `thekitchen.md`? — consolidate |
| `thekitchen.md` | 2026-03-15 | Kitchen ops doc — move to `docs/` |
| `heartbeat.jsonl` | 2026-03-15 | Live runtime log — move to `Donjon_Daemon/` |
| `bridge-funding-messages.md` | 2026-03-31 | Funding doc — move to `docs/` or `sales/` |
| `bridge-preview.svg` | 2026-03-31 | Visual asset — move to `assets/` |
| `donjon-bridge-funding-deck.html` | 2026-03-31 | Deliverable deck — move to `docs/deliverables/` |
| `donjon-bridge-funding.html` | 2026-03-31 | Deliverable — move to `docs/deliverables/` |
| `ableton-dependency-graph-mvp.html` | 2026-04-08 | Tool/demo — move to `projects/` |
| `dd-automation-v2.excalidraw` | 2026-03-15 | Diagram — move to `assets/diagrams/` |
| `forjacob.pdf` | 2026-03-19 | Deliverable PDF — move to `docs/deliverables/` |
| `todo-sync-management.pdf` | 2026-03-12 | Deliverable/tool output — move to `docs/` |
| `todo-sync-management.png` | 2026-03-12 | Image — move to `assets/images/` |
| `todo-sync-management.svg` | 2026-03-12 | SVG — move to `assets/diagrams/` |
| `Donjon at Work.pdf` | 2026-03-13 | Deliverable — move to `docs/deliverables/` |
| `Donjon at Work copy for Jacob.pdf` | 2026-03-14 | Duplicate deliverable — move to `docs/deliverables/` |
| `Donjon_Agency_Pivot_Playbook.docx` | 2026-03-05 | Strategy doc — move to `docs/` |
| `Donjonatworkfinal.zip` | 2026-03-13 | Deliverable ZIP — move to `docs/deliverables/` |
| `donjonatwork-editorsreport.zip` | 2026-03-13 | Deliverable ZIP — move to `docs/deliverables/` |
| `sandbox-config.json` | 2026-02-23 | Config — move to `Agents/` or agent config dir |
| `test_env.py` | 2026-03-22 | Test script — move to `ARCHIVE/Donjon_Daemon/` |
| `affordable_mowing.png` | 2026-03-11 | Random image — unclear purpose, archive candidate |
| `kitchen+letta.png` | 2026-03-12 | Infographic — move to `assets/images/` |
| `letta+kitchen-infographic.png` | 2026-03-12 | Infographic — move to `assets/images/` |

### Files with "final", "copy", "backup", "v2" in Name (duplicates / deliverables)

| File | Location | Notes |
|------|----------|-------|
| `Donjon at Work copy for Jacob.pdf` | root | Duplicate of `Donjon at Work.pdf` |
| `tasks.md.backup` | root | Backup of tasks.md |
| `CLAY_WAKE_UP_ALFIE_GREMLINS_FINAL_2026-03-07.md` | `Agents/Chef/` | Sent deliverable |
| `DONDOG_SERVICEPRO_TEST_CYCLE_REPORT_2026-03-07 2.md` | `Agents/Chef/` | Duplicate (note " 2") |
| `SERVICEPRO_FINAL_REPORT_CHEF_2025-02-25.md` | `Agents/Chef/` | Year-old final report |
| `SERVICEPRO_GREMLIN_FINAL_REPORT_2025-02-25.md` | `Agents/Chef/` | Year-old final report |
| `hvac-automation-example-v2.md` | `sales/case-studies/` | V2 next to v1 — one is superseded |
| `legacy_actions` / `legacy_actions 2` | `sales/archive/` | Duplicate archive dirs |
| `openwork-dondog-setup-package 2.zip` | `(ARCHIVE)agent-files/` | Duplicate ZIP |
| `BILLY_FIX_COMPLETE 2.txt` + `BILLY_FIX_SUMMARY 2.txt` | `reports/billy/` | Duplicates |
| `BILLY_WEBSITE_FIX_STATUS 2.md` | `reports/billy/` | Duplicate |
| `BILLY_WEBSITE_STATUS_REPORT_2026-03-04 2.md` | `reports/billy/` | Duplicate |
| `Donjonatworkfinal.zip` | root | "final" in name = sent deliverable |

---

## Directory Map (2–3 levels, annotated)

```
donjon.agency/
│
├── (ARCHIVE)agent-files/         ← Old agent configs (DonDog, Chef setup packages, heartbeat log)
│   ├── agents-old-workspaces/    ← Superseded workspace configs for Chef, DonDog
│   ├── openwork-dondog-setup-package/   ← Archived setup bundle
│   ├── openwork-dondog-setup-package.zip + " 2.zip"  ← Duplicate ZIPs
│   ├── org_chart.html            ← Old org chart
│   └── tools-archive/            ← Archived tool scripts
│
├── ARCHIVE/                      ← Main archive folder
│   ├── Donjon_Daemon/            ← Full v3 daemon codebase (Python, PRDs, tests) — superseded
│   ├── Donjon_Daemon_theTower/   ← Tower branch of daemon — superseded
│   ├── Donjon.Daemon.v3/         ← Another version — superseded
│   ├── Donjon.Daemon.v3_theTower/ ← Tower branch v3 — superseded
│   ├── donjon_org/               ← Dwight benchmark project (TypeScript, HTML) — superseded
│   ├── lettabot/                 ← Full lettabot project (Node, Dockerfile, tests) — superseded
│   └── lettabot_theTower/        ← Tower branch lettabot — superseded
│
├── Agents/                       ← Active agent definitions and workspaces
│   ├── Chef/                     ← Chef agent reports and scripts (Feb–Mar 2026)
│   ├── Dondog/                   ← DonDog agent (TypeScript project, research)
│   ├── alfie-agent/              ← Alfie agent docs (PDFs, MDs, CurveAI context)
│   ├── sub-agents/               ← Gremlin sub-agent templates (needs work / ready-to-use)
│   ├── OpenWork.md               ← OpenWork agent definition
│   └── The-Chef.md               ← Chef agent definition
│
├── Donjon_Daemon/                ← ACTIVE daemon (current board meeting notes, council tasks)
│   └── agent_prompts/
│
├── Donjon_Images/                ← Empty folder
│
├── Private & Shared/             ← Empty folder (likely Notion export artifact)
├── Private & Shared 2/           ← Notion export: "Donjon at Work" with one image
│
├── anna/                         ← Empty folder (placeholder for Anna Kate project?)
│
├── agents alias                  ← Alias/shortcut file (not a directory)
│
├── assets/
│   ├── diagrams/                 ← Excalidraw, PNG, SVG, PDF diagrams of orchestration system
│   └── images/                  ← Billy website hero image
│
├── commands/                     ← Claude command prompts (book-summarizer, PRD creator, etc.)
│
├── docs/                         ← Agency docs, guides, architecture specs
│   ├── know-defeat/              ← Trading architecture docs (Know Defeat project)
│   ├── servicepro/               ← ServicePro feedback system docs
│   └── superpowers/plans/        ← Superpowers planning docs
│
├── gremlin-deliverables/
│   └── 2026-04-10-session/       ← Latest gremlin session outputs (Riptide, Quill, Crunch)
│
├── gremlin-results/              ← Gremlin test results (LOCAL-TEST-001.json)
│
├── hooks/                        ← React hooks (use-mobile, use-realtime, use-toast) — misplaced?
│
├── images/logos/                 ← Donjon logo files (PNG)
│
├── landfill-gas-dashboard/       ← Client project: landfill gas dashboard (HTML, screenshots)
│
├── memory/system/                ← Agent memory files (persona, work, human, donjon contexts)
│
├── n8n-workflows/                ← n8n automation workflows (JSON)
│
├── output/playwright/            ← Playwright test output
│
├── plugins/
│   └── donjon-hq.plugin          ← HQ plugin file
│
├── prompts/                      ← Agent prompt libraries
│   ├── agent_development_plans/  ← n8n AI agent dev plan
│   ├── agent_specific/           ← 10 specialized agent prompts
│   ├── general/                  ← 5 general prompts
│   └── trading_specific/         ← 10 trading strategy prompts
│
├── reports/                      ← Agent-generated reports
│   ├── billy/                    ← Billy website fix reports (Feb–Mar 2026)
│   ├── dondog/                   ← DonDog sync reports (Mar 2026)
│   ├── executive-summaries/      ← Daily Clay executive summaries (Mar 2026)
│   ├── heartbeat/                ← Heartbeat reports
│   ├── kitchen-checks/           ← Chef kitchen check reports (Feb–Mar 2026, by date)
│   ├── notion-linear/            ← Notion-Linear sync reports
│   ├── service-pro/              ← ServicePro reports
│   ├── servicepro/               ← More ServicePro reports (overlaps with service-pro/)
│   └── t-0027/                   ← T-0027 hourly monitor reports (Mar 2026)
│
├── sales/                        ← Sales materials and outreach
│   ├── archive/legacy_actions/   ← Old sales action files
│   ├── assets/                   ← Sales content drafts, call kit
│   ├── case-studies/             ← HVAC automation case study (v1 + v2)
│   ├── collateral/               ← One-pager, pricing sheet, service menu
│   ├── contacts/                 ← LinkedIn prospect list (Feb 2026)
│   ├── demo/                     ← Chatbot demo HTML
│   ├── outreach/                 ← Email/text/LinkedIn templates and tracking
│   ├── research/                 ← Tulsa HVAC market research
│   ├── tools/                    ← Pricing calculator HTML
│   └── workflows/                ← Onboarding checklist, proposal template, discovery
│
├── servicepro/                   ← ServicePro feedback system (1 file — overlaps with docs/servicepro)
│
├── skills/                       ← Claude skill library (~60 skills)
│   └── [60+ skill subdirectories with SKILL.md files]
│
├── summaries/
│   └── D.D. Heartbeat Orchestrator/   ← Empty folder
│
├── tasks/                        ← Empty folder
│
├── website/                      ← Astro website project (built, has node_modules)
│   └── dist/                     ← Built site (index.html, favicons)
│
└── workers/
    └── dondog-sync/              ← DonDog sync worker (TypeScript project)

```

---

## Archive Candidates

Today's date: **2026-04-12**. Files not modified in 90+ days would predate **2026-01-12**. The `find` command returned 0 such files, meaning everything has been touched in the last 90 days — likely due to macOS propagating timestamps on directory access. Instead, archive candidates are identified by content signals (delivered, superseded, duplicate, mislabeled).

### Tier 1 — Already Archived (confirm and consolidate)

These are already in `ARCHIVE/` or `(ARCHIVE)agent-files/`. They're fine where they are but could be consolidated:

| Location | Reason |
|----------|--------|
| `(ARCHIVE)agent-files/` | Old agent configs, superseded setup packages, old org chart |
| `ARCHIVE/Donjon_Daemon/` | v3 daemon Python codebase — superseded by current `Donjon_Daemon/` |
| `ARCHIVE/Donjon_Daemon_theTower/` | Tower branch — superseded |
| `ARCHIVE/Donjon.Daemon.v3/` + `Donjon.Daemon.v3_theTower/` | Old versioned copies |
| `ARCHIVE/donjon_org/` | Dwight benchmark project — completed/abandoned |
| `ARCHIVE/lettabot/` + `lettabot_theTower/` | Lettabot project — superseded |

**Recommendation:** Merge `(ARCHIVE)agent-files/` into `ARCHIVE/2026/agent-files/` for consistency.

### Tier 2 — Strong Archive Candidates (completed deliverables, sent files)

| File/Folder | Location | Signal |
|-------------|----------|--------|
| `Donjonatworkfinal.zip` | root | "final" = delivered |
| `donjonatwork-editorsreport.zip` | root | delivered report |
| `Donjon at Work.pdf` | root | deliverable PDF |
| `Donjon at Work copy for Jacob.pdf` | root | "copy for Jacob" = sent |
| `forjacob.pdf` | root | "for Jacob" = sent |
| `tasks.md.backup` | root | backup — superseded by tasks.md |
| `tasks-archive-2026-03-13.md` | root | self-labeled archive |
| `Agents/Chef/SERVICEPRO_FINAL_REPORT_CHEF_2025-02-25.md` | Agents/Chef | 2025 date — over a year old |
| `Agents/Chef/SERVICEPRO_GREMLIN_FINAL_REPORT_2025-02-25.md` | Agents/Chef | 2025 date — over a year old |
| `Agents/Chef/DONDOG_SERVICEPRO_TEST_CYCLE_REPORT_2026-03-07 2.md` | Agents/Chef | duplicate (space + "2") |
| All `reports/kitchen-checks/2026-02-*/` folders | reports/kitchen-checks | Feb kitchen checks — 45+ days old |
| All `reports/t-0027/` files | reports/t-0027 | T-0027 task complete, reports are historical |
| `reports/servicepro/` (all Mar 2026) | reports/servicepro | ServicePro work appears complete |
| `reports/billy/` (all files) | reports/billy | Billy website fixes — complete |
| `reports/dondog/` (all files) | reports/dondog | DonDog sync — complete |
| `reports/executive-summaries/` (all Mar 2026) | reports/executive-summaries | Historical summaries |
| `sales/contacts/linkedin-prospects-2026-02-23.md` | sales/contacts | 7+ weeks old prospect list |
| `ARCHIVE/Donjon_Daemon/` node artifacts | ARCHIVE | `__pycache__/`, `.pyc` files |
| `Agents/alfie-agent/*.pdf` | Agents/alfie-agent | PDF duplicates of `.md` files already present |
| `Private & Shared/` (empty) | root | Empty — delete |
| `Donjon_Images/` (empty) | root | Empty — delete |
| `summaries/D.D. Heartbeat Orchestrator/` (empty) | summaries | Empty — delete |
| `tasks/` (empty) | root | Empty — delete |
| `anna/` (empty) | root | Empty — delete |

### Tier 3 — Cleanup / Consolidation Candidates (not strictly archive, but messy)

| Issue | Detail |
|-------|--------|
| `reports/service-pro/` AND `reports/servicepro/` | Two nearly identical folders — merge into one |
| `sales/case-studies/hvac-automation-example.md` vs `hvac-automation-example-v2.md` | v1 is superseded by v2 |
| `the-kitchen.md` and `thekitchen.md` at root | Likely duplicates — consolidate into `docs/` |
| `docs/servicepro/feedback-system` and `docs/servicepro/feedback-system 2` | Duplicate dirs |
| `sales/archive/legacy_actions` and `legacy_actions 2` | Duplicate archive dirs |
| `hooks/` at root | React hooks sitting in agency root — belongs with a web project |
| `sandbox-config.json` at root | Dev config — move to `Agents/` or project dir |
| `affordable_mowing.png` at root | Random image with no clear context — archive or delete |
| `agents alias` file at root | Alias shortcut — move to `docs/` or `Agents/` |

---

## Misplaced Files at Root — Quick Summary

**28 loose files** are sitting directly in `donjon.agency/` that should be in subdirectories. Of these:
- **3 are intentional** and should stay: `CLAUDE.md`, `INDEX.md`, `opencode.jsonc`
- **9 are deliverables** ready to archive: ZIPs, PDFs, sent docs
- **16 should be moved** to `assets/`, `docs/`, `sales/`, or `Donjon_Daemon/`

---

## Generated by
organize-agency skill | Phase 0 + Phase 1 | graphify: not run (not installed / not requested)
