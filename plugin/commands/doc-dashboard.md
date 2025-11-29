---
description: Comprehensive documentation health dashboard with metrics
allowed-tools: mcp__plugin_doc-manager_doc-manager__*
---

# Documentation Health Dashboard

Generate a comprehensive documentation health dashboard.

doc-expert agent Please generate a full documentation health dashboard.

Execute the following analysis and compile into a dashboard report:

## 1. Initialization Check
- Check if `.doc-manager/` exists
- If not initialized, report that and offer setup

## 2. Sync Status
Run `docmgr_detect_changes` and report:
- Total changed code files
- Affected documentation files
- Days since last baseline update
- Sync health indicator (🟢 Current | 🟡 Minor Drift | 🔴 Significant Drift)

## 3. Quality Metrics
Run `docmgr_assess_quality` and report:
- Score for each of the 7 criteria
- Overall quality assessment
- Trend indicators if available

## 4. Validation Status
Run `docmgr_validate_docs` and report:
- Links checked and issues found
- Assets checked and issues found
- Code snippets checked and issues found

## 5. Compile Dashboard

Format as:

```markdown
# 📊 Documentation Health Dashboard

**Project**: [name]
**Platform**: [platform]
**Last Sync**: [date/time]

## Health Summary

| Indicator | Status | Details |
|-----------|--------|---------|
| Sync Status | [🟢/🟡/🔴] | [X files changed] |
| Quality | [🟢/🟡/🔴] | [Overall: good/fair/poor] |
| Validation | [🟢/🟡/🔴] | [X issues found] |

## Sync Status

- **Changed Code Files**: X
- **Affected Doc Files**: X
- **Days Since Sync**: X

## Quality Scores

| Criterion | Score | Issues |
|-----------|-------|--------|
| Relevance | [🟢/🟡/🔴] | X |
| Accuracy | [🟢/🟡/🔴] | X |
| Purposefulness | [🟢/🟡/🔴] | X |
| Uniqueness | [🟢/🟡/🔴] | X |
| Consistency | [🟢/🟡/🔴] | X |
| Clarity | [🟢/🟡/🔴] | X |
| Structure | [🟢/🟡/🔴] | X |

**Overall Quality**: [excellent/good/fair/poor]

## Validation Results

| Check | Scanned | Issues |
|-------|---------|--------|
| Links | X | X |
| Assets | X | X |
| Code Snippets | X | X |

## Top Issues (if any)

1. [Most critical issue with file:line]
2. [Second issue]
3. [Third issue]

## Recommended Actions

1. [Highest priority action]
2. [Second priority action]
3. [Third priority action]

## Quick Commands

| Command | Action |
|---------|--------|
| `/doc-sync` | Sync documentation with code |
| `/doc-quality` | Detailed quality report |
| `/doc-status` | Quick status check |
```

## 6. Health Indicators

Use these thresholds:
- 🟢 Green: In sync, quality good, no validation issues
- 🟡 Yellow: Minor drift (<10 files), quality fair, minor issues
- 🔴 Red: Significant drift (10+ files), quality poor, critical issues
