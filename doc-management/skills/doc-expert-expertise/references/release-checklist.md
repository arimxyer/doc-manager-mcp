# Release Readiness Checklist

Comprehensive guide for pre-release documentation audits.

## Quick Checklist

Before any release, verify:

- [ ] Documentation is in sync with code
- [ ] Accuracy score is "Good"
- [ ] No "Poor" quality scores
- [ ] No broken links to critical resources
- [ ] No missing assets referenced in docs
- [ ] Code examples compile/run
- [ ] Version numbers updated
- [ ] Changelog/release notes current
- [ ] Deprecated features marked
- [ ] New features documented

## Detailed Audit Process

### Phase 1: Sync Check

**Run**: `docmgr_sync(mode="check")`

**Evaluate**:
| Status | Action |
|--------|--------|
| In sync | Proceed to Phase 2 |
| <10 files out of sync | Run sync first |
| 10+ files out of sync | WARN: Major sync needed |

**Blocking Condition**: >10 files out of sync should trigger full sync before release.

### Phase 2: Quality Assessment

**Run**: `docmgr_assess_quality()`

**Evaluate per criterion**:

| Criterion | Good | Fair | Poor |
|-----------|------|------|------|
| Accuracy | ✓ Required | ⚠ Risky | ✗ Block |
| Relevance | ✓ Ideal | ✓ OK | ⚠ Note |
| Purposefulness | ✓ Ideal | ✓ OK | ⚠ Note |
| Uniqueness | ✓ Ideal | ✓ OK | ⚠ Note |
| Consistency | ✓ Ideal | ✓ OK | ⚠ Note |
| Clarity | ✓ Ideal | ⚠ Risky | ✗ Block |
| Structure | ✓ Ideal | ✓ OK | ⚠ Note |

**Blocking Conditions**:
- Accuracy = Poor → Block release
- Clarity = Poor → Block release (users can't understand docs)
- 3+ criteria = Poor → Block release

### Phase 3: Validation

**Run**: `docmgr_validate_docs(check_links=true, check_assets=true, check_snippets=true, validate_symbols=true)`

**Evaluate issues**:

| Issue Type | Severity | Action |
|------------|----------|--------|
| Broken internal link | High | Fix before release |
| Broken external link (critical) | High | Fix or remove |
| Broken external link (optional) | Low | Note, fix later |
| Missing asset (in content) | High | Fix before release |
| Missing alt text | Low | Note, fix later |
| Invalid code syntax | Medium | Fix before release |
| Documented symbol not in code | High | Fix before release |

**Blocking Conditions**:
- Broken links to critical resources (install guide, API reference)
- Missing assets that are referenced in key docs
- Code examples that don't compile

### Phase 4: Content Review

**Manual checks**:

1. **Version Numbers**
   - README version matches release
   - Installation docs show correct version
   - API docs reference correct version

2. **Changelog**
   - Current release is documented
   - Breaking changes highlighted
   - Migration guide if needed

3. **Deprecations**
   - Deprecated features marked
   - Removal timeline documented
   - Alternative approaches suggested

4. **New Features**
   - All new features documented
   - Examples provided
   - Linked from relevant guides

## Release Verdict Criteria

### READY

All of:
- Documentation in sync
- Accuracy = Good
- No Poor scores
- No critical validation failures
- Version numbers correct
- Changelog current

### READY WITH NOTES

All of:
- Documentation in sync
- Accuracy = Fair or Good
- Max 1 Poor score (not Accuracy or Clarity)
- Minor validation issues only

Notes should document:
- Which criterion is Poor/Fair
- Known issues being deferred
- Timeline for fixes

### NOT READY

Any of:
- Documentation significantly out of sync (10+ files)
- Accuracy = Poor
- Clarity = Poor
- 3+ Poor scores
- Critical validation failures
- Missing documentation for breaking changes

## Report Templates

### READY Report

```markdown
## Release Readiness: READY ✓

### Summary
Documentation is ready for release.

### Quality Scores
| Criterion | Score |
|-----------|-------|
| Accuracy | Good |
| Relevance | Good |
| Purposefulness | Good |
| Uniqueness | Fair |
| Consistency | Good |
| Clarity | Good |
| Structure | Good |

### Validation
- Links: 45 checked, 0 issues
- Assets: 12 checked, 0 issues
- Code: 23 snippets, 0 syntax errors

### Checklist
- [x] In sync with code
- [x] Accuracy verified
- [x] No critical issues
- [x] Version numbers correct
- [x] Changelog updated

**Recommendation**: Proceed with release.
```

### READY WITH NOTES Report

```markdown
## Release Readiness: READY WITH NOTES ⚠

### Summary
Documentation can be released with noted limitations.

### Quality Scores
| Criterion | Score | Note |
|-----------|-------|------|
| Accuracy | Good | |
| Relevance | Fair | Some v1.x content still present |
| Purposefulness | Good | |
| Uniqueness | Poor | Duplicate API docs in 2 files |
| Consistency | Fair | |
| Clarity | Good | |
| Structure | Good | |

### Known Issues (Deferred)
1. **Uniqueness**: API documented in both api.md and reference.md
   - Impact: Low (information is consistent)
   - Timeline: Fix in next patch release

2. **Relevance**: v1.x migration guide still prominent
   - Impact: Low (still useful for some users)
   - Timeline: Archive after v3.0

### Validation
- Links: 45 checked, 1 warning (external timeout)
- Assets: 12 checked, 0 issues
- Code: 23 snippets, 0 syntax errors

**Recommendation**: Proceed with release. Address noted issues in next cycle.
```

### NOT READY Report

```markdown
## Release Readiness: NOT READY ✗

### Blocking Issues

1. **Accuracy: Poor**
   - docs/api.md:45 - Return type mismatch
   - docs/api.md:89 - Undocumented parameter
   - docs/api.md:123 - Removed function still documented

2. **Validation Failures**
   - docs/guide.md:23 - Broken link to installation.md
   - docs/quickstart.md - Missing required asset: setup-screenshot.png

### Required Actions

**Before Release**:
1. Fix accuracy issues in docs/api.md
2. Fix broken link in docs/guide.md
3. Add or remove reference to setup-screenshot.png

**Estimated Effort**: 1-2 hours

### After Fixing
1. Run `/doc-quality` to re-verify
2. Run `/doc-sync` to update baseline
3. Re-run release readiness check

Would you like me to help fix these issues now?
```

## Post-Release Actions

After successful release:

1. **Update Baseline**
   - Run `docmgr_update_baseline` to mark current state as release-synced

2. **Tag Documentation**
   - Consider git tagging docs state with release version

3. **Archive Old Versions**
   - Move superseded documentation to archive if applicable

4. **Update Tracking**
   - Note release date in documentation metadata

5. **Plan Next Cycle**
   - Create issues for deferred documentation tasks
   - Schedule time for addressing "Fair" scores
