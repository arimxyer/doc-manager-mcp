# Test Metadata Schema

**Version:** 2.1.0
**Status:** ✅ Active
**Last Updated:** 2025-11-19

## Overview

All tests must include standardized metadata tags for spec ownership tracking and test lifecycle management. This schema supports multiple programming languages with language-appropriate comment syntax.

**Supported Languages:**
- Python (`.py`)
- JavaScript (`.js`, `.jsx`)
- TypeScript (`.ts`, `.tsx`)
- Go (`.go`)
- Rust (`.rs`)

## Language Support Matrix

| Language | Comment Syntax | Tag Location | Example |
|----------|---------------|--------------|---------|
| **Python** | Docstring `"""..."""` or `#` comments | Above function/class or as first statement | See Python Examples |
| **JavaScript/TypeScript** | JSDoc `/** ... */` | Above function/describe block | See JavaScript Examples |
| **Go** | Line comments `//` | Above function | See Go Examples |
| **Rust** | Doc comments `///` | Above function | See Rust Examples |

## Language-Specific Behaviors

| Feature | Python | JavaScript/TS | Go | Rust |
|---------|--------|---------------|-----|------|
| **Blank lines between tags and test** | ✅ Allowed (parser skips) | ✅ Allowed (parser skips) | ⚠️ Avoid (use `//` only) | ⚠️ Avoid (use `///` only) |
| **Tag location** | After decorators, in docstring | Before function | Before function | Before attributes (`#[test]`) |
| **Comment syntax** | `"""..."""` or `#` | `/** ... */` | `//` only (NOT `/* */`) | `///` only (NOT `//`) |
| **Nested test detection** | Class methods tracked individually | Describe blocks tracked with full path | Subtests (`t.Run`) NOT individually tracked | Module tests NOT inherited |
| **Multiple decorators/attributes** | Supported (tags after all decorators) | N/A (no decorators) | N/A (no decorators) | Tags before all attributes |

## Tag Definitions

### Required Tags

| Tag | Format | Required | Description |
|-----|--------|----------|-------------|
| `@spec` | `@spec <number-name>` | Yes | Spec identifier that owns this test (001-production-readiness, 002-add-feature...) - kebab-case format |

### Optional Tags

| Tag | Format | Multiple | Description |
|-----|--------|----------|-------------|
| `@userStory` | `@userStory <code>` | Yes | User story coverage (US1, US2, US10...) |
| `@functionalReq` | `@functionalReq <code>` | Yes | Functional requirement validation (FR-001, FR-031...) |
| `@testType` | `@testType unit\|integration\|e2e` | No | Explicit test type classification |
| `@mockDependent` | `@mockDependent` | No | Flag: test depends on mock API |
| `@retirementCandidate` | `@retirementCandidate` | No | Flag: test marked for planned retirement |
| `@contractTest` | `@contractTest` | No | Flag: test validates API contract parity |
| `@slow` | `@slow` | No | Flag: test has execution time >1s |

## Test Type Classification

If `@testType` not specified, inferred from file path:
- `__tests__/` or `/unit/` → `unit`
- `/integration/` → `integration`
- `/e2e/` or `.e2e.` → `e2e`

## ⚠️ Critical Placement Rules

**IMPORTANT**: Tags must be placed correctly or parser will fail to find them.

1. ✅ **Tags MUST be in proper comment format**:
   - Python: Docstring `"""..."""` (AFTER decorators) OR `#` comments
   - JavaScript/TypeScript: JSDoc `/** ... */` (BEFORE function)
   - Go: Line comments `//` (BEFORE function, NO `/* */` block comments)
   - Rust: Doc comments `///` (BEFORE attributes, NO regular `//`)

2. ✅ **Tags MUST be on each individual test** - NO automatic inheritance from file/module/class level

3. ✅ **Blank lines between tags and test are handled by parser** - Parser skips whitespace/newlines, but avoid blank lines for readability (language-specific: Python/JavaScript parsers skip them, Go/Rust recommended to avoid)

4. ✅ **At least @spec tag is required** - Tests without @spec become orphaned

---

## Python Examples

### Basic Test with Tags

```python
"""
@spec 001-production-readiness
@userStory US1
@functionalReq FR-031
@testType unit
"""
def test_authentication():
    """Test user authentication flow."""
    result = authenticate("user", "password")
    assert result == True
```

### Test Class with Tags

```python
class TestWorkspaceList:
    """
    @spec 001-production-readiness
    @userStory US1
    @testType unit
    """

    def test_render_all_workspaces(self, tmp_path):
        """
        @functionalReq FR-031
        """
        workspaces = [
            {"id": "1", "name": "Test 1"},
            {"id": "2", "name": "Test 2"}
        ]
        result = render_workspace_list(workspaces)
        assert len(result) == 2

    def test_empty_state(self):
        """
        @functionalReq FR-034
        @slow
        """
        result = render_workspace_list([])
        assert "no workspaces" in result.lower()
```

### Alternative: Hash Comments

```python
# @spec 001-production-readiness
# @userStory US5
# @testType integration
# @mockDependent
def test_api_integration():
    """Test API integration with mock server."""
    response = mock_api.get("/workspaces")
    assert response.status_code == 200
```

### Async Tests with Multiple Decorators

```python
import pytest

@pytest.mark.smoke
@pytest.mark.asyncio
async def test_async_with_markers():
    """
    @spec 001-production-readiness
    @userStory US1
    @slow
    """
    result = await fetch_data()
    assert result is not None
```

### pytest Fixtures

```python
@pytest.fixture(scope="session")
async def database():
    """
    @spec 001-production-readiness
    Fixture providing async database connection
    """
    async with create_engine() as engine:
        yield engine
```

### pytest Parametrized Tests

```python
import pytest

@pytest.mark.parametrize("input,expected", [
    ("hello", 5),
    ("world", 5),
    ("test", 4),
])
def test_string_length(input, expected):
    """
    @spec 001-production-readiness
    @userStory US2
    @testType unit
    """
    assert len(input) == expected
```

Tags go in the docstring AFTER decorators (including `@pytest.mark.parametrize`).

---

## JavaScript/TypeScript Examples

### Basic Test with Tags

```typescript
/**
 * @spec 001-production-readiness
 * @userStory US1
 * @userStory US5
 * @functionalReq FR-031
 * @testType unit
 */
describe('WorkspaceList Component', () => {
  /**
   * @spec 001-production-readiness
   * @userStory US1
   * @functionalReq FR-031
   */
  it('should render all workspaces in the array', () => {
    const workspaces = [
      { id: '1', name: 'Test 1', path: '/test1' },
      { id: '2', name: 'Test 2', path: '/test2' }
    ];

    render(<WorkspaceList workspaces={workspaces} />);

    expect(screen.getByText('Test 1')).toBeInTheDocument();
    expect(screen.getByText('Test 2')).toBeInTheDocument();
  });

  /**
   * @spec 001-production-readiness
   * @userStory US5
   * @functionalReq FR-034
   */
  it('should show empty state when no workspaces', () => {
    render(<WorkspaceList workspaces={[]} />);
    expect(screen.getByText(/no workspaces/i)).toBeInTheDocument();
  });
});
```

### Async Tests

```typescript
describe('Async Operations', () => {
  /**
   * @spec 001-production-readiness
   * @testType integration
   */
  test('fetches data successfully', async () => {
    await expect(fetchData()).resolves.toBe('peanut butter');
  });

  /**
   * @spec 001-production-readiness
   * @testType integration
   */
  test('handles errors gracefully', async () => {
    await expect(fetchData()).rejects.toThrow('error');
  });
});
```

### Setup/Teardown with Tests

```typescript
describe('Feature Suite', () => {
  beforeEach(() => {
    // Setup before each test
  });

  /**
   * @spec 001-production-readiness
   * @userStory US1
   */
  test('test using setup', () => {
    // Uses beforeEach setup
    expect(true).toBeTruthy();
  });
});
```

### Deeply Nested Describe Blocks

```typescript
describe('Feature Suite', () => {
  describe('Subsystem A', () => {
    describe('Component X', () => {
      /**
       * @spec 001-production-readiness
       * @userStory US3
       * @testType integration
       */
      it('handles edge case correctly', () => {
        // Parser tracks full describePath: ['Feature Suite', 'Subsystem A', 'Component X']
        const result = processEdgeCase();
        expect(result).toBeTruthy();
      });
    });
  });
});
```

Parser tracks the full `describePath` array for nested describe blocks.

---

## Go Examples

### Basic Test with Tags

```go
// @spec 001-production-readiness
// @userStory US1
// @functionalReq FR-031
// @testType unit
func TestAuthentication(t *testing.T) {
    result := Authenticate("user", "password")
    if !result {
        t.Error("Authentication failed")
    }
}
```

### Test with Mock Dependency

```go
// @spec 001-production-readiness
// @userStory US5
// @testType integration
// @mockDependent
func TestAPIIntegration(t *testing.T) {
    mockServer := httptest.NewServer(handler)
    defer mockServer.Close()

    resp, err := http.Get(mockServer.URL + "/workspaces")
    if err != nil {
        t.Fatal(err)
    }
    if resp.StatusCode != 200 {
        t.Errorf("Expected 200, got %d", resp.StatusCode)
    }
}
```

### Table-Driven Test

```go
// @spec 001-production-readiness
// @userStory US2
// @testType unit
func TestSum(t *testing.T) {
    testCases := []struct {
        name     string
        a, b     int
        expected int
    }{
        {"both positive", 1, 2, 3},
        {"one negative", -1, 1, 0},
        {"both zero", 0, 0, 0},
    }

    for _, tc := range testCases {
        t.Run(tc.name, func(t *testing.T) {
            result := Sum(tc.a, tc.b)
            if result != tc.expected {
                t.Fatalf("expected %d, got %d", tc.expected, result)
            }
        })
    }
}
```

### Subtests with t.Run

**⚠️ PARSER LIMITATION**: Subtests created with `t.Run()` are NOT individually detected by the test registry parser. Only the parent test function is tracked.

```go
// @spec 001-production-readiness
// @userStory US4
// @testType integration
func TestFeature(t *testing.T) {
    // Only this parent test is tracked by parser
    // Tags apply to entire test function, not individual subtests

    t.Run("edge case 1", func(t *testing.T) {
        // NOT tracked separately - covered by parent test
    })

    t.Run("edge case 2", func(t *testing.T) {
        // NOT tracked separately - covered by parent test
    })
}
```

### Benchmark Test

```go
// @spec 001-production-readiness
// @userStory US3
// @testType unit
// @slow
func BenchmarkWorkspaceRendering(b *testing.B) {
    workspaces := generateWorkspaces(1000)
    b.ResetTimer()
    for i := 0; i < b.N; i++ {
        RenderWorkspaceList(workspaces)
    }
}
```

---

## Rust Examples

### Basic Test with Tags

```rust
/// @spec 001-production-readiness
/// @userStory US1
/// @functionalReq FR-031
/// @testType unit
#[test]
fn test_authentication() {
    let result = authenticate("user", "password");
    assert_eq!(result, true);
}
```

### Test with Mock Dependency

```rust
/// @spec 001-production-readiness
/// @userStory US5
/// @testType integration
/// @mockDependent
#[test]
fn test_api_integration() {
    let mock_server = MockServer::start();
    let response = Client::new()
        .get(&format!("{}/workspaces", mock_server.url()))
        .send()
        .unwrap();
    assert_eq!(response.status(), 200);
}
```

### Async Test

```rust
/// @spec 001-production-readiness
/// @userStory US2
/// @functionalReq FR-034
/// @testType integration
/// @slow
#[tokio::test]
async fn test_async_workspace_creation() {
    let result = create_workspace("Test Workspace").await;
    assert!(result.is_ok());
}
```

### Test Module with Shared Setup

**⚠️ PARSER LIMITATION**: Module-level doc comments do NOT apply to individual tests. Each test must have its own tags.

```rust
/// Module for workspace tests
/// @spec 001-production-readiness  ← This does NOT apply to tests inside
#[cfg(test)]
mod workspace_tests {
    use super::*;

    /// @spec 001-production-readiness  ← MUST tag each test individually
    /// @userStory US1
    /// @testType unit
    #[test]
    fn test_workspace_creation() {
        let ws = Workspace::new("Test");
        assert_eq!(ws.name, "Test");
    }

    /// @spec 001-production-readiness  ← MUST tag each test individually
    /// @userStory US1
    /// @testType unit
    #[test]
    fn test_workspace_deletion() {
        let ws = Workspace::new("Test");
        assert!(ws.delete().is_ok());
    }
}
```

---

## Common Mistakes

### ⚠️ Blank Lines Between Tags and Test (Language-Specific)

**Parser behavior**: Python and JavaScript parsers skip blank lines/whitespace correctly. However, avoid blank lines for readability and consistency.

```python
# Parser handles this correctly, but avoid for clarity
"""
@spec 001-production-readiness
@userStory US1
"""

def test_authentication():  # ← Blank line: parser skips it
    pass
```

**✅ RECOMMENDED**: No blank lines

```python
"""
@spec 001-production-readiness
@userStory US1
"""
def test_authentication():
    pass
```

### ❌ WRONG: Tags Inside Function Body

```python
def test_authentication():
    """
    @spec 001-production-readiness  # ← Too late, parser won't find this
    """
    pass
```

**✅ CORRECT**: Tags BEFORE or as first statement after decorators

### ❌ WRONG: Tags on describe() Instead of it() (JavaScript)

```javascript
/**
 * @spec 001-production-readiness  ← Parser won't apply this to individual tests
 */
describe('Suite', () => {
  it('test without tags', () => {  // ← Orphaned test
    expect(true).toBe(true);
  });
});
```

**✅ CORRECT**: Tags on each individual `it()` or `test()`

```javascript
describe('Suite', () => {
  /**
   * @spec 001-production-readiness
   */
  it('test with tags', () => {
    expect(true).toBe(true);
  });
});
```

### ❌ WRONG: Go Block Comments Not Supported

```go
/*
 * @spec 001-production-readiness
 * @userStory US1
 */
func TestFeature(t *testing.T) {  // ← Parser won't find block comments
    // ...
}
```

**✅ CORRECT**: Use line comments `//`

```go
// @spec 001-production-readiness
// @userStory US1
func TestFeature(t *testing.T) {
    // ...
}
```

### ❌ WRONG: Regular Comments in Rust (Not Doc Comments)

```rust
// @spec 001-production-readiness  ← Wrong comment type
// @userStory US1
#[test]
fn test_feature() {
    // ...
}
```

**✅ CORRECT**: Use doc comments `///`

```rust
/// @spec 001-production-readiness
/// @userStory US1
#[test]
fn test_feature() {
    // ...
}
```

### ❌ WRONG: Typo in Tag Name

```python
"""
@specs 001  # ← Typo: "specs" instead of "spec"
"""
def test_authentication():
    pass
```

**Result**: Parser ignores misspelled tag, test becomes orphaned (specNumber: null)

### ❌ WRONG: Missing @spec Tag

```python
"""
@userStory US1  # ← No @spec tag
"""
def test_authentication():
    pass
```

**Result**: Orphaned test - will fail validation

---

## Troubleshooting

### Tests Not Detected by Registry

**Symptom**: `test-registry.sh scan` doesn't find your tests

**Check**:
1. File extension matches language (`.py`, `.test.js`, `.test.ts`, `_test.go`, `.rs`)
2. Test function name matches pattern:
   - Python: `test_*` or `Test*` class
   - JavaScript/TypeScript: Uses `describe()`, `it()`, or `test()` calls
   - Go: `Test*` or `Benchmark*` with `*testing.T` signature
   - Rust: Has `#[test]` or `#[tokio::test]` attribute
3. File is in a location that the scanner searches

### Tests Marked as Orphaned

**Symptom**: `test-registry.sh report` shows orphaned tests (no spec ownership)

**Check**:
1. Test has `@spec` tag (not `@specs` or other typo)
2. Tag is in correct comment format for language
3. Comment is BEFORE test function (not inside body)
4. No blank lines between comment and test (if required by language)

### Validation Fails with Tag Errors

**Symptom**: `test-registry.sh validate` reports errors

**Common causes**:
- Malformed spec identifier (must be kebab-case format: `001-production-readiness`, not `001` or `001_production`)
- Tags in wrong comment type (e.g., `//` instead of `///` in Rust)
- Tags on wrong element (e.g., `describe()` instead of `it()`)
- File-level tags expecting inheritance (NOT supported)

### Parser Can't Find Tags After Refactor

**Symptom**: Tags were detected before, but now they're not

**Check**:
1. Did you move tags from correct location to incorrect location?
2. Did you change comment syntax (e.g., docstring to `#` comments)?
3. Did you add blank lines that break the association?
4. Did you move tags inside the function body?

### Go Subtests Not Individually Tracked

**This is expected behavior**: Parser only tracks parent test functions with `Test*` names. Subtests created with `t.Run()` are covered by their parent test's tags.

### Rust Module Tags Not Inherited

**This is expected behavior**: Module-level doc comments don't apply to individual tests. Each test function must have its own tags.

---

## Validation

**Enforced by:**
- `test-registry.sh validate` - Checks all tests have valid metadata tags
- Parser: `.claude/skills/speckit/scripts/parse-test-file-universal.ts`

**Validation rules:**
- All test functions/methods must have metadata comment
- Comment must include `@spec` tag
- `@spec` must be kebab-case format: 3-digit number + hyphen + name (e.g., `001-production-readiness`)
- No orphaned tests (missing spec ownership)

**Run validation:**
```bash
# Scan all tests and populate registry
test-registry.sh scan

# Validate tag compliance
test-registry.sh validate

# Check for orphaned tests
test-registry.sh report
```

---

## Implementation

**Parser:** `.claude/skills/speckit/scripts/parse-test-file-universal.ts` extracts metadata using tree-sitter AST parsing for all supported languages.

**Auto-Tagger:** `.claude/skills/speckit/scripts/add-test-tags-universal.ts` automatically adds metadata tags to existing tests.

**Registry:** `.claude/skills/speckit/scripts/test-registry.sh` manages test tracking.

**Commands:**
- `test-registry.sh scan` - Update registry from test files (all languages)
- `test-registry.sh report` - Show pyramid metrics and health
- `test-registry.sh spec 001` - List tests for specific spec
- `test-registry.sh retire` - Show tests marked with @retirementCandidate
- `test-registry.sh retire --filter <tag>` - Query tests by any metadata tag
- `test-registry.sh validate` - Check tag compliance

**Retire Command Examples:**
```bash
# Show tests explicitly marked for retirement
test-registry.sh retire

# Show tests that depend on mock API
test-registry.sh retire --filter mockDependent

# Show slow tests (execution time >1s)
test-registry.sh retire --filter slow

# Show contract tests
test-registry.sh retire --filter contractTest
```

---

## Test Detection Patterns

Each language uses specific patterns to identify test functions:

| Language | Test Pattern |
|----------|-------------|
| **Python** | Functions starting with `test_` or classes starting with `Test` |
| **JavaScript/TypeScript** | `describe()`, `it()`, `test()` function calls |
| **Go** | Functions starting with `Test` or `Benchmark` with signature `(t *testing.T)` |
| **Rust** | Functions with `#[test]` or `#[tokio::test]` attribute |

---

## Migration Guide

To add tags to existing tests, use the auto-tagger:

```bash
# Dry run (show what would be changed)
bun .claude/skills/speckit/scripts/add-test-tags-universal.ts --dry-run

# Write tags to files
bun .claude/skills/speckit/scripts/add-test-tags-universal.ts --write
```

The auto-tagger infers metadata from:
- File path → `@spec` (e.g., `specs/001-*/tests/` → `001`)
- File path → `@testType` (e.g., `/integration/` → `integration`)
- Imports → `@mockDependent` (detects mock libraries)
- Existing comments → `@userStory`, `@functionalReq` (extracts US1, FR-031 patterns)
