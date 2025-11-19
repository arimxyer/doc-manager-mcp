---
name: speckit.testing
description: Comprehensive testing guide for speckit workflow - test pyramid, metadata tags, registry commands, and retirement workflows
---

# Speckit Testing Guide

Complete reference for testing standards, test registry usage, and quality maintenance throughout the speckit workflow.

## Overview

The speckit testing strategy is built on three pillars:

1. **Test Pyramid** (70/20/10 ratio): Balanced distribution for fast, reliable test suites
2. **Test Registry**: Automated tracking with metadata tags for ownership and health monitoring
3. **Test Retirement**: Systematic cleanup of obsolete tests to prevent bloat

## Test Pyramid Strategy

### Target Distribution

- **70% Unit Tests**: Fast, isolated tests for individual functions/components
- **20% Integration Tests**: Tests for component interactions and workflows
- **10% E2E Tests**: Full system tests simulating real user scenarios

### Pyramid Health Status

**HEALTHY**: Ratios within ±10% of targets
- Example: 65% unit, 23% integration, 12% e2e

**WARN**: Inverted pyramid (more integration than unit tests)
- Example: 30% unit, 55% integration, 15% e2e
- Action: Add unit tests or retire excessive integration tests

**CRITICAL**: E2E tests exceed 20% of total suite
- Example: 20% unit, 30% integration, 50% e2e
- Action: Immediate remediation required

### Why This Distribution?

**Unit Tests (70%)**:
- Fastest execution (milliseconds)
- Easiest to maintain
- Precise failure localization
- Enable TDD workflows

**Integration Tests (20%)**:
- Validate component contracts
- Test realistic data flows
- Catch integration bugs
- Moderate execution time (seconds)

**E2E Tests (10%)**:
- Validate critical user journeys
- Test complete system behavior
- Catch UI/UX issues
- Slowest execution (seconds to minutes)

## Test Metadata Tags

All tests must be tagged with metadata for registry tracking. See `testing/metadata-schema.md` for complete reference.

### Required Tags

**@spec <number-name>**: Links test to specification (kebab-case format: 001-production-readiness)

```python
# Python
"""
@spec 001-production-readiness
"""
def test_user_authentication():
    assert authenticate("user", "password") == True
```

```javascript
// JavaScript/TypeScript
/**
 * @spec 001-production-readiness
 */
it('authenticates users', () => {
  expect(authenticate('user', 'password')).toBe(true);
});
```

```go
// Go
// @spec 001-production-readiness
func TestUserAuthentication(t *testing.T) {
    result := Authenticate("user", "password")
    assert.True(t, result)
}
```

```rust
// Rust
/// @spec 001-production-readiness
#[test]
fn test_user_authentication() {
    assert_eq!(authenticate("user", "password"), true);
}
```

### Optional Tags

**@testType unit|integration|e2e**: Explicit test type (overrides path inference). Only use when path-based inference is incorrect (e.g., test in wrong directory)

```python
"""
@spec 001-production-readiness
@testType integration
"""
def test_database_connection():
    db = connect_database()
    assert db.is_connected() == True
```

**@userStory <id>**: Links to user story

```python
"""
@spec 001-production-readiness
@userStory US1
@functionalReq FR-031
"""
def test_user_registration():
    result = register_user("test@example.com")
    assert result.success == True
```

**@mockDependent**: Flags tests using mocks/stubs (retirement candidate for migration specs)

```python
"""
@spec 001-production-readiness
@mockDependent
"""
def test_api_call_with_mock():
    with mock.patch('api.client') as mock_client:
        mock_client.return_value = {"status": "success"}
        result = call_api()
        assert result["status"] == "success"
```

**@slow**: Marks tests taking >1 second (performance optimization candidate)

```python
"""
@spec 001-production-readiness
@slow
"""
async def test_large_dataset_processing():
    data = generate_large_dataset(10000)
    result = await process(data)
    assert len(result) == 10000
```

**@retirementCandidate**: Explicitly marks test for planned removal

**@contractTest**: Flags API contract tests (affected by API changes)

## Test Registry Commands

### Initialize Registry (First Time)

```bash
# Automatically happens during first speckit.plan execution
# Or manually:
test-registry.sh init
```

### Bootstrap Existing Tests (Brownfield Projects)

```bash
# Detect and tag existing untagged tests
test-registry.sh bootstrap --spec 001-production-readiness

# Workflow:
# 1. Scans for untagged tests (specNumber: null)
# 2. Shows dry-run preview
# 3. Prompts for confirmation
# 4. Applies tags with --write
# 5. Re-scans and reports results
```

### Scan and Update Registry

```bash
# Scan all test files and update registry
test-registry.sh scan

# Output shows:
# - Total tests found
# - Pyramid distribution
# - Health status (PASS/WARN/CRITICAL)
# - Orphaned test count
```

### Generate Reports

```bash
# Human-readable report
test-registry.sh report

# JSON output for automation
test-registry.sh report --json
```

### Query by Spec

```bash
# Show all tests for specific spec
test-registry.sh spec 001-production-readiness

# JSON output
test-registry.sh spec 001-production-readiness --json
```

### Find Retirement Candidates

```bash
# Default: tests marked @retirementCandidate
test-registry.sh retire

# Filter by specific tag
test-registry.sh retire --filter mockDependent
test-registry.sh retire --filter slow
test-registry.sh retire --filter contractTest

# JSON output for automation
test-registry.sh retire --filter mockDependent --json
```

### Validate Metadata

```bash
# Check all tests have required @spec tags
test-registry.sh validate

# Returns:
# - Count of tests missing @spec tags
# - Specific file paths and line numbers
```

### Export for Planning

```bash
# Used by speckit.plan workflow
test-registry.sh export-for-plan --json

# Returns:
# - Total tests by type
# - Pyramid health status
# - Orphaned test count
# - Tests for specific spec (if applicable)
```

## Test Retirement Workflow

### When to Retire Tests

1. **Feature deprecation**: Old feature removed, tests no longer relevant
2. **API changes**: Contract tests for old API version
3. **Mock replacement**: Moving from mocked to real dependencies (Tauri migration, etc.)
4. **Performance optimization**: Slow tests replaced with faster alternatives
5. **Duplicate coverage**: Multiple tests covering same scenario

### Retirement Process

**Step 1: Identify candidates during planning**

```bash
# In speckit.plan workflow, check for retirement candidates
test-registry.sh retire --filter mockDependent --json
```

Document in plan.md Testing Strategy section:
- Retirement candidates: 12 tests | Filter: @mockDependent | Timing: Phase 3

**Step 2: Generate retirement tasks**

In speckit.tasks workflow, create retirement tasks:

```markdown
- [ ] T015 [P] Retire 3 mock-dependent workspace tests in tests/unit/test_workspace.py
- [ ] T016 [P] Retire 5 mock-dependent auth tests in tests/integration/test_auth.py
```

**Step 3: Execute retirements**

During speckit.implement:
1. Implement new functionality
2. Verify new tests pass
3. Delete retired test code
4. Run `test-registry.sh scan` to update registry
5. Verify orphanedTests count decreased

### Retirement Best Practices

- **Retire AFTER replacement works**: Don't delete tests before new coverage exists
- **Retire in same phase**: If Phase 3 makes tests obsolete, retire in Phase 3
- **Document reason**: Note why in commit message and tasks.md
- **Check coverage**: Ensure replacement tests exist before deleting
- **Use filters**: Tag candidates early for easy identification later

## Fixing Inverted Test Pyramids

### Strategy 1: Add Unit Tests

**When to use**: Low unit test count, missing coverage for core logic

```markdown
# In tasks.md
- [ ] T020 [P] [US1] Unit tests for UserService in tests/unit/test_user_service.py
- [ ] T021 [P] [US1] Unit tests for AuthHelper in tests/unit/test_auth_helper.py
- [ ] T022 [P] [US1] Unit tests for ValidationUtils in tests/unit/test_validation.py
```

**Impact**: Increases unit test percentage, rebalances pyramid

### Strategy 2: Retire Excessive Integration/E2E Tests

**When to use**: High integration/e2e count, redundant coverage

```bash
# Find candidates
test-registry.sh retire --filter slow
test-registry.sh retire --filter mockDependent

# Generate retirement tasks
- [ ] T030 [P] Retire 5 slow e2e tests (redundant with integration tests)
```

**Impact**: Decreases integration/e2e percentage, speeds up suite

### Strategy 3: Convert Tests

**When to use**: Integration tests that could be unit tests

Example: Database integration test using real DB → Unit test with repository pattern

**Before** (integration test):
```python
@testType integration
def test_user_repository_save():
    db = connect_real_database()  # Slow
    repo = UserRepository(db)
    user = User("test@example.com")
    repo.save(user)
    assert db.query("SELECT * FROM users").count() == 1
```

**After** (unit test):
```python
@testType unit
def test_user_repository_save():
    mock_db = MockDatabase()  # Fast
    repo = UserRepository(mock_db)
    user = User("test@example.com")
    repo.save(user)
    assert mock_db.saved_users[0].email == "test@example.com"
```

## Common Patterns and Anti-Patterns

### ✅ Good Patterns

**Pattern 1: Test pyramid in task generation**
```markdown
# Phase 3: User Story 1
### Tests
- [ ] T010 [P] [US1] Unit tests for User model (3 tests)
- [ ] T011 [P] [US1] Unit tests for UserService (5 tests)
- [ ] T012 [P] [US1] Unit tests for validation helpers (4 tests)
- [ ] T013 [US1] Integration test for registration flow
- [ ] T014 [US1] E2E test for complete user journey
```

**Pattern 2: Tag all tests immediately**
```python
# Always include @spec when creating test
"""
@spec 001-production-readiness
@testType unit
"""
def test_new_feature():
    pass
```

**Pattern 3: Bootstrap before planning**
```bash
# Brownfield project - tag existing tests first
test-registry.sh bootstrap --spec 001-production-readiness
test-registry.sh scan
# Now plan with accurate baseline
```

### ❌ Anti-Patterns

**Anti-Pattern 1: Writing only e2e tests**
```markdown
# BAD: All tests are e2e (inverted pyramid)
- [ ] T010 [US1] E2E test for user registration
- [ ] T011 [US1] E2E test for user login
- [ ] T012 [US1] E2E test for user profile update
```

**Anti-Pattern 2: No @spec tags**
```python
# BAD: Test not linked to spec
def test_something():
    pass
```

**Anti-Pattern 3: Never retiring tests**
```bash
# BAD: Keeping obsolete mock tests after migration
# Result: test-registry.sh report shows 200 tests, 100 are obsolete
```

**Anti-Pattern 4: Ignoring pyramid warnings**
```bash
# test-registry.sh scan output:
# Pyramid Status: WARN
# You: "I'll fix it later" ← BAD
```

## Integration with Speckit Workflow

### During Specify (Phase 1)

- Include test coverage success criterion: "Feature achieves 70/20/10 pyramid"
- Make requirements testable and unambiguous

### During Plan (Phase 3)

- Initialize registry: `test-registry.sh init` (if not exists)
- Bootstrap if needed: `test-registry.sh bootstrap --spec <number>`
- Load baseline: `test-registry.sh export-for-plan --json`
- Identify retirements: `test-registry.sh retire --filter <tag> --json`
- Document testing strategy in plan.md

### During Tasks (Phase 4)

- Calculate test counts per user story (70/20/10 distribution)
- Generate retirement tasks if applicable
- Reference existing tests: `test-registry.sh spec <number> --json`

### During Implement (Phase 6)

- Write tests with @spec tags
- Run `test-registry.sh scan` after adding tests
- Run `test-registry.sh validate` to check tags
- Check pyramid health: `test-registry.sh report`
- Block if pyramid getting worse (quality gates)

## Troubleshooting

### "Found N untagged tests"

```bash
# Solution: Bootstrap
test-registry.sh bootstrap --spec 001-production-readiness
```

### "Pyramid Status: WARN"

```bash
# Check distribution
test-registry.sh report

# Two strategies:
# 1. Add unit tests
# 2. Retire excessive integration/e2e tests
test-registry.sh retire --filter slow
```

### "OrphanedTests: 45"

```bash
# Tests missing @spec tags
# Solution: Run bootstrap or manually add tags
test-registry.sh bootstrap --spec 001-production-readiness
```

### "Validate failed: 10 tests missing @spec"

```bash
# Check which tests
test-registry.sh validate

# Add @spec tags to those tests
# Re-scan
test-registry.sh scan
```

## Summary

- **Test Pyramid**: 70% unit, 20% integration, 10% e2e for healthy suites
- **Metadata Tags**: All tests need @spec, optional tags for filtering
- **Bootstrap**: Use for brownfield projects with existing tests
- **Retirement**: Systematically remove obsolete tests (retire --filter)
- **Quality Gates**: Block implementation if pyramid getting worse
- **Workflow Integration**: Registry auto-initializes during first plan

For command reference and examples, see `testing/metadata-schema.md`.
For quick commands, see `testing/quick-reference.md`.
