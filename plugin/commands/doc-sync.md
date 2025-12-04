---
description: Synchronize documentation with code changes
allowed-tools: mcp__plugin_doc-manager_doc-manager__*
---

# Documentation Sync Workflow

Synchronize documentation with code changes.

doc-expert agent Please run a documentation sync workflow.

Execute the full sync process:

1. **Detect Changes**: Run `docmgr_detect_changes` with `include_semantic=true` to understand what changed
2. **Review Action Items**: Use `action_items` and `config_field_changes` from output to prioritize work
3. **Analyze Impact**: Identify which documentation files are affected
4. **Delegate Updates**: If changes require documentation updates:
   - Batch changes into groups of 10-15 files
   - Delegate to doc-writer agent with specific guidance
   - Include platform context and conventions
5. **Validate**: After doc-writer agent completes, validate the updates
6. **Assess Quality**: Run quality assessment on updated documentation
7. **Feedback Loop**: If quality issues found, provide feedback and iterate (max 3 iterations)
8. **Update Baseline**: Once quality is acceptable, ask user if they want to update the baseline
   - If yes: run `docmgr_sync mode="resync"` or `docmgr_update_baseline`
   - If no: report completion without baseline update

Provide progress updates at each step and a final summary:

```
## Documentation Sync Complete

**Changes Detected**: {count} files
**Config Field Changes**: {count} fields
**Action Items**: {count} (critical: N, high: N)
**Documentation Updated**: {count} files
**Validation**: {pass | issues_found}
**Quality Score**: {overall_assessment}
**Baseline**: {updated | not_updated}

### Next Steps
- {any manual actions needed}
```

If no changes detected:
```
## Documentation Sync

**Status**: Documentation is up to date
**No changes** detected since last sync.
```
