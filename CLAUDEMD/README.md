# CLAUDEMD Directory - Domain-Specific Documentation

This directory contains optimized, domain-specific documentation files for the KICKAI project, designed for maximum Claude Code efficiency.

## File Structure & Token Optimization

### Core Files (Total: ~2,300 tokens)
- **`agentic-design.md`** (340 words) - CrewAI collaboration system, agent routing
- **`development-patterns.md`** (440 words) - Tool patterns, coding standards, troubleshooting
- **`telegram-integration.md`** (219 words) - Bot API, messaging, commands
- **`database.md`** (314 words) - Firebase patterns, migrations, data access
- **`mock-testing.md`** (276 words) - Mock UI, testing frameworks
- **`sdlc.md`** (367 words) - Testing strategy, CI/CD, deployment
- **`environment-setup.md`** (342 words) - Configuration, dependencies, setup

### Index File
- **`../CLAUDE.md`** (475 words) - Optimized index with quick reference and file links

## Optimization Benefits

### Token Efficiency
- **Reduced Context**: Load only relevant domain documentation
- **Focused Content**: Each file covers a specific technical domain
- **Quick Reference**: Essential patterns and rules in main index
- **Minimal Redundancy**: Cross-references instead of duplication

### Usage Patterns
1. **Quick Start**: Use main `CLAUDE.md` for essential commands and patterns
2. **Domain-Specific**: Load specific files when working on particular areas
3. **Troubleshooting**: `development-patterns.md` contains comprehensive issue resolution
4. **Setup**: `environment-setup.md` for new development environment configuration

## Claude Code Usage
```
# For general development
Include: CLAUDE.md

# For agent system work
Include: CLAUDE.md + CLAUDEMD/agentic-design.md

# For testing work  
Include: CLAUDE.md + CLAUDEMD/mock-testing.md + CLAUDEMD/sdlc.md

# For database operations
Include: CLAUDE.md + CLAUDEMD/database.md + CLAUDEMD/development-patterns.md
```

## Maintenance
- Update individual files when domain-specific changes occur
- Keep main `CLAUDE.md` as lightweight index with critical quick-reference
- Ensure cross-references between files remain accurate
- Validate token efficiency periodically with `wc -w` commands