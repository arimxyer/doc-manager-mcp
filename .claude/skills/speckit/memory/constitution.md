<!--
Sync Impact Report - Constitution v1.0.0
========================================

Version Change: N/A → 1.0.0 (Initial ratification)
Date: 2025-01-14

Modified Principles:
- N/A (initial creation)

Added Sections:
- Core Principles (7 principles: Accuracy/Transparency, Specification Adherence, Fail-Fast Error Handling, Comprehensive Testing, Security First, Frequent Commits, Architectural Integrity)
- Quality Standards (Code, Performance, Documentation)
- Development Workflow (Pre-Implementation, During Implementation, Post-Implementation)
- Governance (Constitution Authority, Compliance, Amendment Process)

Removed Sections:
- N/A (initial creation)

Template Consistency Validation:
✅ plan-template.md - Constitution Check section (line 32) can derive gates from principles
✅ spec-template.md - Success criteria align with test coverage requirements (SC-005)
✅ tasks-template.md - Test pyramid targets (70/20/10) match Principle IV requirement
✅ references/*.md - No agent-specific names found requiring generic guidance

Follow-up TODOs:
- None - all placeholders filled

Rationale for v1.0.0:
- Initial constitution created from CLAUDE.md project instructions and established patterns
- Codifies existing practices: fail-fast error handling, specification adherence, test-driven development
- Establishes NON-NEGOTIABLE principles for production-ready development
- Provides governance framework for future amendments
-->

# doc-manager MCP Server Constitution

## Core Principles

### I. Accuracy and Transparency (NON-NEGOTIABLE)

**Accurate assessments and transparency are the #1 priority in this repository.**

- **MUST NOT** claim a task is complete when it's only partially done
- **MUST NOT** mark a task as completed if tests are failing
- **MUST NOT** skip steps in a task to save time
- **MUST NOT** take shortcuts that deviate from the spec
- **MUST NOT** implement differently than the spec describes
- **MUST NOT** ignore acceptance criteria in spec
- **MUST NOT** hide errors or issues encountered
- **MUST** report the actual state of work, not aspirational state
- **MUST** stop and document gaps if incomplete work is discovered
- **MUST** explain clearly if a task cannot be completed
- **MUST** surface spec errors immediately
- **MUST** execute all steps in a task, even if they seem redundant
- **MUST** test thoroughly before marking tasks complete

**Rationale**: Trust and code quality depend on honest reporting. Shortcuts compound technical debt and break production systems.

### II. Specification Adherence (NON-NEGOTIABLE)

If a spec exists, you **MUST** follow it with NO QUESTIONS ASKED, ONLY EXECUTION.

- **MUST** follow the spec exactly as written - no shortcuts, no deviations
- **MUST** execute every step in the specified order
- **MUST** meet all acceptance criteria before marking tasks complete
- **MUST** implement features as described, not as interpreted

**When you think the spec is wrong:**
1. **STOP implementation immediately**
2. Document the specific issue
3. Ask the user for clarification or correction
4. Wait for spec update and approval
5. **THEN** continue implementation

**MUST NOT**:
- Reinterpret the spec to make it "better"
- Optimize or "improve" the spec on your own
- Skip requirements that seem redundant
- Assume the spec is outdated without confirmation

**Rationale**: Specs represent deliberate planning and design. Time was taken to create them, so time should be taken to execute them faithfully.

### III. Fail-Fast Error Handling (NON-NEGOTIABLE)

All errors **MUST** be explicit and prevent silent failures.

- **MUST NOT** use bare `except:` blocks that hide errors
- **MUST** raise specific exception types with clear messages
- **MUST** fail immediately when errors occur (no silent continues)
- **MUST** propagate errors to callers with context
- **MUST** log errors before raising them
- **MUST** validate inputs and fail early on invalid data
- **MUST** report skipped/failed operations to users

**Rationale**: Silent failures corrupt data, mislead users, and make debugging impossible. Explicit errors enable quick diagnosis and fix.

### IV. Comprehensive Testing (NON-NEGOTIABLE)

All new code **MUST** have tests before being merged.

- **Test Pyramid**: 70% unit, 20% integration, 10% e2e
- **MUST** write tests for all new functions and classes
- **MUST** achieve 100% test pass rate before merging
- **MUST** include edge case and error path testing
- **MUST** tag all tests with metadata (@spec, @testType, @mockDependent)
- **MUST** update tests when changing functionality
- **SHOULD** use test-driven development (tests before implementation)

**Rationale**: Tests are the safety net that enables confident refactoring and prevents regressions.

### V. Security First

Security standards **MUST** be strictly followed.

- **MUST NOT** introduce OWASP Top 10 vulnerabilities
- **MUST NOT** store sensitive data insecurely
- **MUST** validate all user inputs for path traversal, injection attacks
- **MUST** sanitize outputs to prevent XSS
- **MUST** use secure defaults (fail closed, not open)
- **MUST** document security assumptions and threat models
- **SHOULD** perform security review before marking features complete

**Rationale**: Security vulnerabilities put users and systems at risk. Prevention is cheaper than remediation.

### VI. Frequent Commits

Commit **MUST** be made frequently and often when working through spec tasks.

**When to commit:**
- After completing each task
- After completing each phase of a spec
- After any significant milestone or working state
- Before switching to a different task
- When updating relevant spec documentation

**Commit message format:**
```
<type>: <description>

<body explaining changes>

<phase reference if applicable>

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

**Rationale**: Frequent commits enable easy rollback, provide clear audit trail, and allow atomic changes that can be reviewed independently.

### VII. Architectural Integrity

Architectural layers **MUST** never be mixed.

- **MUST** respect separation of concerns (models, tools, utils, constants)
- **MUST NOT** mix business logic with presentation
- **MUST NOT** import higher-level modules from lower-level modules
- **MUST** keep dependencies unidirectional
- **MUST** validate that changes respect existing architecture

**Rationale**: Mixed layers create circular dependencies, make testing difficult, and violate single responsibility principle.

## Quality Standards

### Code Quality

- **MUST** be concise and direct in communication
- **MUST** update documentation when changing dependencies/frameworks
- **MUST** update documentation when changing file organization
- **SHOULD** follow PEP 8 for Python code
- **SHOULD** use type hints for all function signatures

### Performance Standards

- **MUST** avoid O(n²) or worse algorithms where O(n) or O(n log n) is possible
- **SHOULD** cache expensive computations when safe to do so
- **SHOULD** use incremental processing for large datasets
- **MUST** profile before optimizing (no premature optimization)

### Documentation Standards

- **MUST** update relevant documentation when features change
- **MUST** include docstrings for all public functions and classes
- **SHOULD** provide examples in docstrings for complex functions
- **MUST** document assumptions and limitations

## Development Workflow

### Pre-Implementation

1. Read relevant specs and design documents
2. Understand acceptance criteria
3. Review related code for patterns
4. Plan approach before coding

### During Implementation

1. Write tests first (TDD) when possible
2. Implement feature following spec exactly
3. Run tests frequently
4. Commit after each task
5. Update task checkboxes as you progress

### Post-Implementation

1. Verify all tests pass (100% pass rate)
2. Verify all acceptance criteria met
3. Update documentation
4. Security review
5. Mark task complete only when all above done

## Governance

### Constitution Authority

- This constitution **supersedes** all other practices
- When CLAUDE.md conflicts with constitution, constitution wins
- Amendments require explicit user approval
- All specs **MUST** comply with constitution principles

### Compliance

- All code reviews **MUST** verify constitution compliance
- Constitution violations are **CRITICAL** severity
- Specs that violate constitution **MUST** be revised before planning
- Implementation that violates constitution **MUST** be fixed before merging

### Amendment Process

1. Propose amendment with rationale
2. Update constitution with version bump
3. Update dependent artifacts (templates, specs, plans)
4. Document migration path for existing code
5. Ratify with user approval

**Version**: 1.0.0 | **Ratified**: 2025-01-14 | **Last Amended**: 2025-01-14
