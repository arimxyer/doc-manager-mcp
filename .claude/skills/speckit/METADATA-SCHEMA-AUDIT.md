# metadata-schema.md Audit Report

**Date**: 2025-11-19
**Auditor**: Claude Code
**Scope**: Validate metadata-schema.md against real test framework patterns

## Research Summary

Comprehensive research conducted on:
- Python: pytest (fixtures, markers, async), unittest
- JavaScript/TypeScript: Jest, Vitest (describe/it, async, nested)
- Go: testing package (table-driven, subtests, benchmarks)
- Rust: #[test], #[tokio::test], #[cfg(test)] modules

## Critical Finding: Docstring/Comment Placement Rules

| Language | CORRECT | Current Schema | Status |
|----------|---------|----------------|--------|
| **Python** | Docstring AFTER decorators | Shows this ✅ | ✅ CORRECT |
| **JavaScript/TypeScript** | JSDoc BEFORE function | Shows this ✅ | ✅ CORRECT |
| **Go** | Comment BEFORE function | Shows this ✅ | ✅ CORRECT |
| **Rust** | Doc comment /// BEFORE attributes | Shows this ✅ | ✅ CORRECT |

**Verdict**: Basic placement rules are correct ✅

---

## Missing Patterns

### 1. Python - Async Tests with Multiple Decorators ❌

**What's missing**: Example with stacked pytest markers

**Should add**:
```python
@pytest.mark.smoke
@pytest.mark.asyncio
async def test_with_multiple_markers():
    """
    @spec 001
    @userStory US1
    """
    result = await fetch_data()
    assert result is not None
```

### 2. Python - pytest Fixtures ❌

**What's missing**: How to tag fixtures vs tests

**Should add**:
```python
@pytest.fixture(scope="session")
async def database():
    """
    @spec 001
    Fixture for database connection
    """
    async with create_engine() as engine:
        yield engine
```

### 3. JavaScript/TypeScript - Async Tests ❌

**What's missing**: async/await test examples

**Should add**:
```javascript
/**
 * @spec 001
 * @testType integration
 */
test('fetches data successfully', async () => {
    await expect(fetchData()).resolves.toBe('peanut butter');
});
```

### 4. JavaScript/TypeScript - beforeEach/afterEach ❌

**What's missing**: Setup/teardown patterns

**Should add**:
```javascript
describe('Suite', () => {
    /**
     * Setup before each test
     */
    beforeEach(() => {
        // setup
    });

    /**
     * @spec 001
     */
    test('test with setup', () => {
        // test uses beforeEach setup
    });
});
```

### 5. Go - Table-Driven Tests ❌

**What's missing**: Proper table-driven test pattern

**Current schema shows** (line 254-267): Benchmark example
**Should ALSO add**: Table-driven test example

```go
// @spec 001
// @testType unit
func TestSum(t *testing.T) {
    testCases := []struct {
        name     string
        a, b     int
        expected int
    }{
        {"both positive", 1, 2, 3},
        {"one negative", -1, 1, 0},
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

### 6. Go - Subtests (t.Run) with Tag Inheritance ❌

**What's missing**: How tags apply to subtests

**Should add**:
```go
// @spec 001
// @userStory US1
func TestFeature(t *testing.T) {
    // Main test tags apply to all subtests

    t.Run("edge case 1", func(t *testing.T) {
        // Inherits @spec 001, @userStory US1
    })

    t.Run("edge case 2", func(t *testing.T) {
        // Also inherits parent tags
    })
}
```

### 7. Rust - Async Tests with tokio ❌

**What's missing**: tokio::test example

**Current schema shows** (line 314-318): Has #[tokio::test] ✅
**But missing**: Explanation that doc comment goes BEFORE #[tokio::test]

**Should clarify**:
```rust
/// Tests async data fetching
/// @spec 001
/// @testType integration
#[tokio::test]  // Doc comment BEFORE attribute
async fn test_fetch_data() {
    let data = fetch_data().await;
    assert!(data.is_some());
}
```

### 8. Rust - Test Modules (#[cfg(test)]) ❌

**What's missing**: How to tag tests inside test modules

**Current schema shows** (line 322-346): Has test module example ✅
**But missing**: Clarification on whether module-level tags apply

**Should clarify**:
```rust
/// Module for user tests
/// @spec 001  ← Does this apply to all tests in module?
#[cfg(test)]
mod tests {
    /// Specific test
    /// @spec 001  ← Or do individual tests need tags?
    #[test]
    fn test_user_login() {
        // ...
    }
}
```

---

## Misleading/Ambiguous Sections

### 1. File-Level Tag Inheritance (Lines 54-56, 120-143, 189-211)

**Current text**: "File-level tags apply to all tests in that file"

**Problem**: This is ambiguous and potentially incorrect depending on language:
- **Python**: Module-level docstring tags do NOT automatically apply to test functions
- **JavaScript**: Top-level JSDoc does NOT apply to tests inside describe()
- **Go**: No file-level comment mechanism for tags
- **Rust**: Module-level doc comments don't apply to individual tests

**Actual behavior**:
- Parser scans each individual test function
- Tags must be on the test function itself
- No inheritance from file/module level

**Recommendation**: Remove or clarify "file-level tag inheritance" section. It's misleading.

### 2. Alternative Python Comment Syntax (Lines 107-118)

**Current example**:
```python
# @spec 001
# @userStory US5
# @testType integration
# @mockDependent
def test_api_integration():
    """Test API integration with mock server."""
    pass
```

**Problem**: Research shows pytest and test-registry parser likely expect **docstrings**, not `#` comments.

**Question for validation**: Does `parse-test-file-universal.ts` actually parse `#` comments for Python, or only docstrings?

**Recommendation**: Verify parser behavior. If it only parses docstrings, remove this example.

---

## Missing Critical Information

### 1. WRONG Examples ❌

**What's missing**: Examples of INCORRECT placement that will cause parser to fail

**Should add section**: "Common Mistakes" with ❌ WRONG examples:
- Blank line between tags and test
- Tags inside function body
- Tags on wrong element (describe vs it)
- Typos in tag names

### 2. Edge Case: Blank Lines ❌

**What's missing**: Explicit rule about blank lines

**Should add**:
> ⚠️ **CRITICAL**: No blank lines between metadata comment and test function. Blank lines break the association.

### 3. Parser Behavior Clarification ❌

**What's missing**: How parser finds tests

**Should add**:
- Python: Scans for `test_*` functions and `Test*` classes
- JavaScript/TypeScript: Scans for `it()`, `test()`, `describe()` calls
- Go: Scans for `Test*` functions with `*testing.T` signature
- Rust: Scans for functions with `#[test]` or `#[tokio::test]` attributes

### 4. Tag Format Validation ❌

**What's missing**: What happens if tags are malformed

**Should add**:
- Typo in tag name → Parser ignores, test becomes orphaned
- Wrong value format → Parser ignores or mis-parses
- Missing @spec → Test becomes orphaned (specNumber: null)

---

## Parser Validation Needed

These examples need validation against `parse-test-file-universal.ts`:

1. **Python `#` comments** (line 110): Does parser support this, or only docstrings?
2. **File-level tags** (line 122): Does parser actually inherit tags from module docstring?
3. **Rust module tags** (line 328): Do module-level doc comments apply to tests inside?
4. **JavaScript describe() tags** (line 193): Do file-level JSDoc tags apply to tests inside describe()?

**Action**: Review parser code to confirm actual behavior.

---

## Recommended Structure

Current structure:
1. Overview
2. Language support matrix
3. Tag definitions
4. Test type classification
5. Tag inheritance (misleading?)
6. Examples per language
7. Validation
8. Implementation
9. Test detection patterns
10. Migration guide

**Proposed restructure**:
1. Overview
2. **Critical Placement Rules** (NEW - MUST READ FIRST)
3. Language support matrix
4. Tag definitions
5. Test type classification
6. **Python Examples** (expanded with async, fixtures)
7. **JavaScript/TypeScript Examples** (expanded with async, setup/teardown)
8. **Go Examples** (expanded with table-driven, subtests)
9. **Rust Examples** (expanded with async, modules)
10. **Common Mistakes** (NEW - WRONG examples)
11. **Edge Cases** (NEW - blank lines, decorators, attributes)
12. Validation
13. Troubleshooting (NEW)
14. Implementation
15. Test detection patterns
16. Migration guide

---

## Priority Actions

### High Priority (Must Fix)

1. **Add WRONG examples** - Show what NOT to do
2. **Clarify/remove file-level tag inheritance** - Currently misleading
3. **Add async test examples** - Missing for all languages
4. **Add blank line warning** - Critical for parser success

### Medium Priority (Should Add)

1. **Add table-driven test examples** (Go)
2. **Add beforeEach/afterEach examples** (JavaScript)
3. **Add pytest fixture examples** (Python)
4. **Add subtest examples** (Go)

### Low Priority (Nice to Have)

1. **Add test module organization** (Rust)
2. **Add parallel test examples** (Go)
3. **Add benchmark examples** (all languages)

---

## Next Steps

1. ✅ Complete research (done)
2. ⏳ Audit current schema (this document)
3. ⏳ Validate parser behavior against claimed features
4. ⏳ Create comprehensive update (not appendage - proper integration)
5. ⏳ Test updated schema with real test files
6. ⏳ Update related documentation (speckit.testing.md, implement.md)

---

## Summary

**Current metadata-schema.md status**: 7/10
- ✅ Basic placement rules are correct
- ✅ Tag definitions are clear
- ✅ Has examples for all 4 languages
- ❌ Missing async test patterns
- ❌ Missing WRONG examples
- ❌ File-level inheritance is misleading
- ❌ Missing critical edge cases
- ❌ No troubleshooting section

**Recommendation**: Comprehensive rewrite (not appendage) to integrate research findings properly.
