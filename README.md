# Donjon Intelligence Systems Skills Marketplace

A curated collection of specialized AI agent skills for OpenWork/OpenCode agents. This repository serves as a marketplace for sharing, discovering, and installing skills that extend the capabilities of AI agents.

## 📂 Categories

- **agents/** - Agent creation and management skills
- **ai-ml/** - AI/ML, LLM, and MCP related skills
- **brand-marketing/** - Branding, marketing, and content creation skills
- **career/** - Career development and job search skills
- **development/** - Software development and DevOps skills
- **diagnostics/** - Troubleshooting and root cause analysis skills
- **finance/** - Financial analysis and pricing skills
- **gtm-sales/** - Go-to-market, sales, and CRM skills
- **media/** - Multimedia, design, and creative skills
- **productivity/** - Productivity and workflow automation skills
- **research/** - Research and analysis skills
- **security/** - Security and compliance skills
- **utilities/** - Utility and helper skills
- **vintage-thrifting/** - Vintage shopping and thrifting skills

## 🚀 How to Use

To install a skill from this marketplace:

```bash
# Clone this repository
git clone https://github.com/claybowl/donjon-skills-marketplace.git

# Copy the skill you want to your OpenCode skills directory
cp -r donjon-skills-marketplace/<category>/<skill-name> ~/.config/opencode/skills/

# Or if using Claude Code:
cp -r donjon-skills-marketplace/<category>/<skill-name> ~/.claude/skills/
```

## 📝 Contributing

To add your skill to the marketplace:

1. Fork this repository
2. Create a new branch: `git checkout -b add-my-awesome-skill`
3. Place your skill in the appropriate category directory (or create a new one)
4. Ensure your skill has a `SKILL.md` file with proper documentation
5. Commit your changes: `git commit -m "Add: <skill-name> skill"`
6. Push to your fork: `git push origin add-my-awesome-skill`
7. Open a pull request

## 🔍 Finding Skills

Browse the category directories above or use GitHub's search to find skills by name or functionality.

## 🏷️ Skill Metadata

Each skill should include:
- `SKILL.md` - Documentation with triggers, description, and usage instructions
- Any required scripts, templates, or resources
- Proper categorization based on skill functionality

## 💡 Examples of Skills in This Marketplace

- **5-whys** - Root cause analysis using the Five Whys methodology
- **agent-creator** - Create new OpenCode agents
- **brand-agency** - Apply Agency brand colors and typography
- **deep-research** - Conduct enterprise-grade research with multi-source synthesis
- **donjon-intel-report** - Generate premium Donjon Intelligence Systems PDF reports
- **electron-ship** - Ship web apps as desktop Electron apps
- **exa-search** - Neural search via Exa MCP
- **figma-implement-design** - Translate Figma designs into production code
- **gtm-engineering** - Build GTM automation with code
- **letta-memory** - Core Letta memory integration via MCP
- **research-synthesis** - Synthesize user research into themes and insights
- **social-selling** - Sell through social media with LinkedIn optimization
- **worktree-workflow** - Enforce a worktree-per-task workflow

## 📜 License

Individual skills may have their own licenses. Please check each skill's directory for specific licensing information.

---

*Built with ❤️ by the Donjon Intelligence Systems team*
