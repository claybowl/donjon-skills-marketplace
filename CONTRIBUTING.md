# Contributing to Donjon Skills Marketplace

Thank you for considering contributing to our skills marketplace! Here's how you can help.

## How to Contribute

1. **Fork the repository**
2. **Create a new branch** for your skill: `git checkout -b add/your-skill-name`
3. **Add your skill** to the appropriate category directory
4. **Ensure proper documentation** with a SKILL.md file
5. **Commit your changes**: `git commit -m "Add: your-skill-name skill"`
6. **Push to your fork**: `git push origin add/your-skill-name`
7. **Open a Pull Request**

## Skill Requirements

Each skill should include:

### SKILL.md
Every skill must have a SKILL.md file with:
- **Name**: Clear, descriptive name
- **Description**: What the skill does
- **Triggers**: Phrases that activate the skill
- **Location**: Path to the skill (relative to skills directory)
- **Usage Instructions**: How to use the skill
- **Examples**: Example invocations (optional but recommended)

### Directory Structure
```
your-skill-name/
├── SKILL.md
├── scripts/          # Optional: helper scripts
├── templates/        # Optional: template files
└── resources/        # Optional: additional resources
```

## Best Practices

- **Keep skills focused**: Each skill should do one thing well
- **Avoid secrets**: Never commit API keys, tokens, or credentials
- **Document thoroughly**: Clear instructions help others use your skill
- **Test your skill**: Ensure it works before submitting
- **Follow naming conventions**: Use lowercase with hyphens (kebab-case)

## Categories

Skills should be placed in the most appropriate category:
- `agents/` - Agent creation and management
- `ai-ml/` - AI/ML, LLM, and MCP skills
- `brand-marketing/` - Branding, marketing, content
- `career/` - Career development, job search
- `development/` - Software development, DevOps
- `diagnostics/` - Troubleshooting, root cause analysis
- `finance/` - Financial analysis, pricing
- `gtm-sales/` - Go-to-market, sales, CRM
- `media/` - Multimedia, design, creative
- `productivity/` - Productivity, workflow automation
- `research/` - Research, analysis
- `security/` - Security, compliance
- `utilities/` - Utility, helper skills
- `vintage-thrifting/` - Vintage shopping, thrifting

## Questions?

Open an issue or reach out to the maintainers. Happy skill sharing! 🚀
