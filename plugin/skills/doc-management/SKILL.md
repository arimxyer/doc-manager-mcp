---
name: doc-management
description: Documentation lifecycle management skill. Activates when user mentions documentation, docs, sync, quality, validation, releases, or setup. Routes to appropriate agent (doc-expert for orchestration, doc-writer for content) and provides gentle reminders about documentation health.
---

# Doc-Management Skill

Documentation lifecycle management through the doc-manager MCP server. This skill routes requests to specialized agents and provides proactive documentation health awareness.

## Activation Triggers

Activate when user mentions:

**Documentation terms**: "documentation", "docs", "README", "API docs", "guide"

**Sync/status**: "sync docs", "doc status", "update docs", "docs out of date"

**Quality**: "doc quality", "validate docs", "check docs", "broken links"

**Releases**: "release", "deploy", "ship", "merge to main", "v1.0"

**Setup**: "setup docs", "init docs", "documentation management"

**Code changes**: "committed", "pushed", "finished implementing" (gentle reminder)

## Agent Routing

### Route to doc-expert agent:
- Analysis tasks: "check status", "what needs updating"
- Quality tasks: "assess quality", "is this release-ready"
- Sync tasks: "sync documentation", "update docs for changes"
- Setup tasks: "set up doc management", "initialize"
- Validation tasks: "validate docs", "check for broken links"
- Migration tasks: "move docs", "reorganize documentation"

### Route to doc-writer agent:
- Content tasks: "write API docs for X", "create a guide"
- Direct editing: "update the README", "add examples"
- Simple updates: "document this function", "add code samples"

### Decision Flow:
```
Requires analysis, orchestration, quality, or state management?
  YES → doc-expert agent
  NO → Straightforward content with clear scope?
    YES → doc-writer agent
    NO → doc-expert agent (to assess first)
```

## Behavior Guidelines

### Do NOT Auto-Run
Never automatically run heavy operations. Always suggest and ask:
- "Would you like me to check documentation status?"
- "I can run a quality assessment. Want me to proceed?"
- "Documentation sync available. Should I start?"

### Gentle Reminders
At appropriate moments, offer (don't command):

**On release mention:**
```
Before the release, would you like a documentation health check?
- /doc-status - Quick sync status
- /doc-quality - Full quality assessment
```

**On code change mention:**
```
Code changes may need documentation updates.
Run /doc-status when ready to check.
```

**On docs mention:**
```
I can help with documentation. Options:
- Check status: /doc-status
- Full sync: /doc-sync
- Quality audit: /doc-quality
```

### First-Run Detection
If `.doc-manager/` doesn't exist when user asks about docs:
```
Documentation management isn't set up for this project.

Would you like me to initialize it? I'll:
1. Detect your documentation platform
2. Create tracking configuration
3. Establish baselines

Say "setup docs" to proceed.
```

## Quick Commands Reference

| Command | Purpose |
|---------|---------|
| `/doc-status` | Quick health check |
| `/doc-sync` | Full sync workflow |
| `/doc-quality` | Quality assessment |
| `/doc-dashboard` | Comprehensive metrics |

## Edge Cases

### Large-Scale Changes (50+ files)
Warn before proceeding:
```
Detected 50+ files with changes. This will be processed in batches.
Estimated time: 10-15 minutes.
Proceed with documentation sync?
```

### Quality Conflicts
If fixing one criterion harms another:
```
Quality trade-off detected:
- Adding detail improves Clarity
- But increases Uniqueness issues (duplication)

Which should I prioritize?
```

### Not Initialized
Always check for `.doc-manager/` before assuming setup exists.
Offer initialization if missing.

## Integration Points

This skill coordinates with:
- **doc-expert agent**: For orchestration, analysis, quality, state
- **doc-writer agent**: For content creation and editing
- **MCP tools**: docmgr_* tools via agents
- **Slash commands**: /doc-status, /doc-sync, /doc-quality, /doc-dashboard
