# Delegation Protocol

Comprehensive guide to working with doc-writer agent.

## When to Delegate

**Delegate to doc-writer when**:
- Content needs to be created or updated
- Scope is clear and well-defined
- Source code locations are identified
- Platform and conventions are known

**Do NOT delegate when**:
- Scope is unclear (assess first)
- Need analysis or decision-making
- Quality assessment required
- State operations needed

## Delegation Template

Always provide this structure when delegating:

```markdown
doc-writer agent Please update documentation:

**Context**: [1-2 sentences explaining what changed and why documentation is needed]

**Platform**: [MkDocs / Sphinx / Docusaurus / Hugo / Jekyll / Plain Markdown]

**Batch**: [N of M total] (if batching)

**Files to Update**:
1. [docs/path/file.md] - [What to document]
   - Source: [src/path/file.py]:[line_start]-[line_end]
   - Type: [function / class / module / guide section]
   - Key details: [parameters, returns, exceptions, behaviors]

2. [docs/path/another.md] - [What to document]
   - Source: [src/path/code.py]:[lines]
   - Type: [type]
   - Key details: [details]

**Conventions**:
- [Project-specific rule 1]
- [Project-specific rule 2]
- [Style preferences]

**Existing Patterns**: [Note any patterns from existing docs to follow]

Run `docmgr_validate_docs` before returning your results.
```

## Delegation Examples

### Example 1: New Function Documentation

```markdown
doc-writer agent Please update documentation:

**Context**: New data processing function added to handle batch transformations.

**Platform**: MkDocs

**Files to Update**:
1. docs/api/processor.md - Document new `batch_transform()` function
   - Source: src/processor.py:145-189
   - Type: function
   - Key details:
     - Parameters: data (List[dict]), config (TransformConfig)
     - Returns: TransformResult with transformed items and stats
     - Raises: ValidationError if data format invalid
     - Important: Processes in chunks of 100 for memory efficiency

**Conventions**:
- Use imperative mood for descriptions
- Include type hints in parameter docs
- Add code example for every public function

Run `docmgr_validate_docs` before returning.
```

### Example 2: Multiple Files Batch

```markdown
doc-writer agent Please update documentation:

**Context**: Authentication module refactored with new OAuth support.

**Platform**: Sphinx

**Batch**: 1 of 2 (10 files)

**Files to Update**:
1. docs/api/auth.rst - Update `authenticate()` signature change
   - Source: src/auth/core.py:45-78
   - Type: function
   - Key details: New `provider` parameter, returns AuthResult instead of bool

2. docs/api/auth.rst - Add new `oauth_login()` function
   - Source: src/auth/oauth.py:23-67
   - Type: function
   - Key details: OAuth flow initiation, returns redirect URL

3. docs/guides/authentication.rst - Update auth flow diagram
   - Source: N/A (conceptual)
   - Type: guide section
   - Key details: Add OAuth as third authentication option

[... continue for remaining 7 files ...]

**Conventions**:
- Use Sphinx autodoc format
- Cross-reference with :func: and :class: roles
- Include .. versionadded:: 2.0 for new functions

Run `docmgr_validate_docs` before returning.
```

### Example 3: Guide Update

```markdown
doc-writer agent Please update documentation:

**Context**: Installation process simplified with new CLI installer.

**Platform**: Docusaurus

**Files to Update**:
1. docs/getting-started/installation.md - Rewrite installation section
   - Source: N/A (process documentation)
   - Type: guide section
   - Key details:
     - Old: Manual pip install with dependencies
     - New: Single `npx create-myapp` command
     - Keep: Manual installation as alternative
     - Add: Troubleshooting for common issues

**Conventions**:
- Use :::tip for helpful hints
- Use :::warning for potential issues
- Include copy-able code blocks with titles

Run `docmgr_validate_docs` before returning.
```

## Receiving Results

### What to Expect

Doc-writer will return a structured report:

```markdown
## Completed

**Updated**:
- docs/api/processor.md - Added batch_transform() documentation

**Validation**: All checks passed

Ready for quality assessment.
```

Or for partial completion:

```markdown
## Partial Completion

**Updated**:
- docs/api/processor.md - Added batch_transform()

**Failed**:
- docs/guides/processing.md - File not found

**Validation**:
- 1 warning: External link timeout

**Action Needed**:
- Confirm processing.md location
```

### Post-Delegation Steps

1. **Review** the completion report
2. **Check** validation results for issues
3. **Run** `docmgr_assess_quality` on updated files
4. **Evaluate** quality scores:
   - All "Fair" or better → Accept
   - Any "Poor" → Provide feedback
5. **Proceed** to next batch or finalize

## Feedback Protocol

### When Quality Issues Found

Provide specific, actionable feedback:

```markdown
Quality assessment found issues:

**Accuracy** (score: poor):
- docs/api/processor.md:45 - Parameter type is `List[dict]`, documented as `dict`
- docs/api/processor.md:52 - Return type should be `TransformResult`, not `dict`

**Clarity** (score: fair):
- docs/api/processor.md:60-75 - Add code example showing batch processing
- docs/api/processor.md:78 - Explain what happens when chunk size exceeds data length

Please revise these specific sections. Focus on Accuracy first.
```

### Feedback Best Practices

1. **Be specific**: Include file:line references
2. **Prioritize**: Address "Poor" scores before "Fair"
3. **Explain**: Say what's wrong AND what's needed
4. **Limit scope**: Don't overwhelm with all issues at once

### Iteration Limits

```
Iteration 1: Assess → Feedback if needed
Iteration 2: Re-assess → More specific feedback if still issues
Iteration 3: Re-assess → If still "Poor", escalate to user

After 3 iterations, escalate:
"Quality threshold not met after 3 revision cycles.

Remaining issues:
- [Specific issues]

Options:
1. Accept current state (with noted limitations)
2. Provide additional guidance
3. Handle manually

How would you like to proceed?"
```

## Batch Management

### Batching Rules

| Total Files | Batch Size | Batches |
|-------------|-----------|---------|
| 1-14 | All | 1 |
| 15-30 | 10-15 | 2 |
| 31-45 | 10-15 | 3 |
| 46+ | 10-15 | Warn user first |

### Checkpoint Strategy

After each batch:
1. Validate batch results
2. Assess batch quality
3. If acceptable, can update baseline for completed files
4. Proceed to next batch

This allows recovery if later batches fail.

### Handling Batch Failures

If doc-writer reports failures in a batch:
1. Note which files succeeded
2. Note which files failed and why
3. Either:
   - Resolve the blocker and re-delegate failed files
   - Proceed with successful files, address failures separately
4. Don't let one failure block entire sync

## Communication Patterns

### Clear Delegation
```
❌ "Update the docs"
✓ "Update docs/api.md to document the new process_data() function at src/processor.py:45-89"
```

### Specific Feedback
```
❌ "Needs improvement"
✓ "docs/api.md:45 - Change parameter type from 'dict' to 'List[dict]' to match code"
```

### Actionable Context
```
❌ "Something changed in auth"
✓ "Authentication now supports OAuth. Add oauth_login() docs and update the auth flow guide."
```
