<!--
Sync Impact Report - Constitution v1.2.0
========================================

Version Change: 1.1.0 → 1.2.0
Date: 2025-11-19

Modified Principles:
- Principle IV: Comprehensive Testing Following TDD Principles
  - Clarified TDD wording: "failing tests" → "tests before implementation (TDD red-green-refactor cycle)"
  - Removed "when applicable" from Development Workflow (line 201) to enforce NON-NEGOTIABLE status
  - Expanded with 5 subsections: TDD, Test Pyramid Distribution, Test Metadata and Registry, Test Retirement, Quality Gates
  - Added test registry integration (validate, scan, bootstrap commands)
  - Added pyramid health enforcement (HEALTHY/WARN/CRITICAL states)
  - Added test retirement workflow (retire AFTER replacement, common triggers)
  - Clarified metadata tags: @spec required, others optional with specific purposes
  - Added quality gates (block phase completion on validation failure, CRITICAL pyramid status)

Added Sections:
- Principle IV subsections: TDD, Test Pyramid Distribution, Test Metadata and Registry, Test Retirement, Quality Gates

Removed Sections:
- None

Template Consistency Validation:
✅ plan-template.md - Constitution Check section can derive test registry gates from Principle IV
✅ spec-template.md - Success criteria align with 70/20/10 pyramid and quality gates (SC-005)
✅ tasks-template.md - Test pyramid targets match expanded Principle IV requirements
✅ speckit.testing.md - All test registry commands, retirement workflow, and pyramid enforcement now codified in constitution

Follow-up TODOs:
- ✅ Updated speckit.plan.md (reference workflow) to include quality gates and TDD red-green-refactor terminology
- ✅ Updated speckit.tasks.md (reference workflow) to include quality gate checkpoint tasks and blocking conditions
- ✅ Updated speckit.specify.md (reference workflow) to include test registry validation in success criteria examples

Rationale for v1.2.0:
- Bridges gap between constitution and comprehensive testing workflow (speckit.testing.md)
- Codifies test registry as mandatory infrastructure (not optional tooling)
- Enforces pyramid health through quality gates (prevents inverted pyramids)
- Establishes test retirement as continuous practice (prevents test bloat)
- Clarifies metadata tag requirements (reduces ambiguity about "MUST tag all tests")
- Aligns TDD workflow terminology with industry standard (red-green-refactor)
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

### IV. Comprehensive Testing Following TDD Principles (NON-NEGOTIABLE)

All new code **MUST** have tests before being merged.

#### Test-Driven Development (TDD)

- **MUST** write tests before implementation (TDD red-green-refactor cycle)
- **MUST** write tests for all newly defined functions and classes before implementing them
- **MUST** cover all acceptance criteria with tests
- **MUST** achieve 100% test pass rate before moving onto the next phase and marking tasks complete in a phase section
- **MUST** achieve 100% test pass rate before marking the entire spec complete
- **MUST** include edge case and error path testing
- **MUST** update tests when changing functionality

#### Test Pyramid Distribution

- **Target Ratio**: 70% unit, 20% integration, 10% e2e
- **MUST** maintain pyramid health (HEALTHY status: ±10% of targets)
- **MUST** address WARN status (inverted pyramid) before phase completion
- **MUST** block phase completion if pyramid status is CRITICAL (e2e >20%)
- **SHOULD** add unit tests or retire excessive integration/e2e tests to fix pyramid

#### Test Metadata and Registry

- **MUST** tag all tests with @spec number (required for test registry tracking)
- **SHOULD** use optional tags when applicable:
  - @testType (unit|integration|e2e) - only if path inference incorrect
  - @mockDependent - flags tests using mocks (retirement candidates)
  - @slow - tests taking >1 second (optimization candidates)
  - @retirementCandidate - explicitly marks for planned removal
  - @contractTest - API contract tests (affected by API changes)
  - @userStory, @functionalReq - traceability tags
- **MUST** run `test-registry.sh validate` before marking phase complete
- **MUST** run `test-registry.sh scan` after adding/retiring tests to update registry
- **MUST** bootstrap existing tests before planning in brownfield projects:
  ```bash
  test-registry.sh bootstrap --spec <number>
  ```

#### Test Retirement

- **MUST** retire obsolete tests when replacement coverage exists
- **MUST** retire tests AFTER replacement works, never before
- **SHOULD** retire in same phase that makes tests obsolete
- **MUST** document retirement reason in commit message
- **Common retirement triggers**:
  - @mockDependent tests after migrating to real dependencies
  - @slow tests replaced with faster alternatives
  - @contractTest tests for deprecated API versions
  - Duplicate coverage or deprecated features

#### Quality Gates

- **MUST** block phase completion if:
  - Test validation fails (`test-registry.sh validate`)
  - Pyramid status is CRITICAL
  - Test pass rate <100%
  - New tests missing @spec tags
- **SHOULD** block if pyramid status degrades from HEALTHY to WARN

**Rationale**: Tests are the safety net that enables confident refactoring and prevents regressions. The test pyramid ensures fast, reliable test suites. Test retirement prevents bloat and maintenance burden.

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

1. Write tests first (TDD)
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

**Version**: 1.2.0 | **Ratified**: 2025-11-19 | **Last Amended**: 2025-11-19
