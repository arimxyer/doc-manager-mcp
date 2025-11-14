---
name: speckit
description: Structured feature specification and implementation workflow for software projects. Use when planning new features, creating specifications, managing the spec lifecycle (clarify, analyze, archive), or implementing spec-based tasks. Triggers on "spec", "specification", "feature planning", "implement spec", or workflow management requests.
---

# Speckit - Specification-Driven Development Workflow

## Overview

Speckit provides a complete specification-driven development workflow that separates **what** (requirements) from **how** (implementation). Guides through planning, designing, and implementing features using a structured, phase-based approach.

**Core principle**: Write clear, technology-agnostic specifications before implementation to reduce rework and ensure alignment.

## When to Use This Skill

Use speckit when:
- Planning a new feature from scratch
- Creating or updating a feature specification
- Clarifying ambiguous requirements before planning
- Generating implementation tasks from a completed spec
- Analyzing spec/plan/task consistency before implementation
- Implementing features using structured task lists
- Managing the spec lifecycle (archiving completed specs)

**Don't use** for quick fixes, trivial changes, or exploratory coding without upfront planning.

## The Speckit Workflow

Speckit follows a sequential workflow. Each step builds on the previous one:

```
1. references/speckit.specify.md      → Create feature specification
2. references/speckit.clarify.md      → [Optional] Resolve ambiguities
3. references/speckit.plan.md         → Generate implementation plan
4. references/speckit.tasks.md        → Break down into actionable tasks
5. references/speckit.analyze.md      → [Optional] Validate consistency
6. references/speckit.implement.md    → Execute the implementation
7. references/speckit.archive.md      → Archive completed specs
```

Additional commands:
- `references/speckit.constitution.md` - Define project principles
- `references/speckit.checklist.md` - Generate custom quality checklists
- `references/speckit.update.md` - Update speckit framework
- `references/speckit.di.md` - Pre-or-Post spec design requirements template

## Workflow Commands

Each workflow step has detailed instructions in `references/`. Load the appropriate reference doc when executing that step.

### Step 1: Create Specification

**Reference**: `references/speckit.specify.md`

**Purpose**: Transform natural language feature requests into structured, technology-agnostic specifications.

**Instructions**: Load `references/speckit.specify.md` for complete execution instructions.

**Key Points**:
- Focus on **WHAT** users need and **WHY**, not **HOW** to implement
- No tech stack, frameworks, APIs, or code structure
- Success criteria must be measurable and technology-agnostic
- Make informed guesses for unclear details; limit clarifications to 3
- Uses template from `assets/spec-template.md`

**Example**: Load `references/speckit.specify.md` with feature description: "Add user authentication with OAuth2 support"

**Output**: Branch, spec file, and requirements checklist

---

### Step 2: Clarify Ambiguities (Optional)

**Reference**: `references/speckit.clarify.md`

**Purpose**: Resolve underspecified areas through targeted questions (max 5).

**Instructions**: Load `references/speckit.clarify.md` for complete execution instructions.

**Key Points**:
- Scan spec for ambiguities across 10+ categories
- Present questions one at a time with recommended answers
- Immediately integrate each answer into spec
- Update relevant sections (requirements, data model, edge cases)
- Save spec incrementally after each clarification

**Example**: Load `references/speckit.clarify.md` to begin clarification process

**Output**: Updated spec with clarifications integrated

---

### Step 3: Generate Implementation Plan

**Reference**: `references/speckit.plan.md`

**Purpose**: Create detailed technical design from the specification.

**Instructions**: Load `references/speckit.plan.md` for complete execution instructions.

**Key Points**:
- Load spec and constitution (from `memory/constitution.md`)
- Use template from `assets/plan-template.md`
- Generate research.md, data-model.md, contracts/, quickstart.md
- Validate against project principles
- Update agent context with new technologies
- Scripts used: `scripts/setup-plan.sh`, `scripts/update-agent-context.sh`

**Example**: Load `references/speckit.plan.md` to begin planning

**Output**: plan.md with technical approach, plus design artifacts

---

### Step 4: Generate Task Breakdown

**Reference**: `references/speckit.tasks.md`

**Purpose**: Create actionable, dependency-ordered task list.

**Instructions**: Load `references/speckit.tasks.md` for complete execution instructions.

**Key Points**:
- Load all design documents (spec, plan, data-model, contracts)
- Use template from `assets/tasks-template.md`
- Organize tasks by user story (one phase per story)
- Format: `- [ ] [T001] [P] [US1] Description with file path`
- Generate dependency graph and parallel execution examples
- Scripts used: `scripts/check-prerequisites.sh`

**Example**: Load `references/speckit.tasks.md` to generate tasks

**Output**: tasks.md with complete task breakdown

---

### Step 5: Analyze Consistency (Optional)

**Reference**: `references/speckit.analyze.md`

**Purpose**: Validate cross-artifact consistency (read-only analysis).

**Instructions**: Load `references/speckit.analyze.md` for complete execution instructions.

**Key Points**:
- **READ-ONLY**: Does not modify any files
- Detect duplication, ambiguity, underspecification, coverage gaps
- Validate against constitution (violations are CRITICAL)
- Generate findings report with severity (CRITICAL/HIGH/MEDIUM/LOW)
- Provide next actions based on severity
- Scripts used: `scripts/check-prerequisites.sh`

**Example**: Load `references/speckit.analyze.md` to analyze consistency

**Output**: Structured analysis report (no file modifications)

---

### Step 6: Execute Implementation

**Reference**: `references/speckit.implement.md`

**Purpose**: Execute all tasks from tasks.md in dependency order.

**Instructions**: Load `references/speckit.implement.md` for complete execution instructions.

**Key Points**:
- Check checklist status (halt if incomplete unless approved)
- Verify project setup (create ignore files as needed)
- Execute phase-by-phase (setup → tests → core → integration → polish)
- Mark completed tasks [X] in tasks.md
- Respect dependencies (sequential vs. parallel)
- Scripts used: `scripts/check-prerequisites.sh`

**Example**: Load `references/speckit.implement.md` to begin implementation

**Output**: Fully implemented feature with all tasks marked complete

---

### Step 7: Archive Completed Specs

**Reference**: `references/speckit.archive.md`

**Purpose**: Move completed or old specs to specs/archive/.

**Instructions**: Load `references/speckit.archive.md` for complete execution instructions.

**Key Points**:
- List mode: Show all specs with status
- Archive specific: Move specified specs
- Archive completed: Find all completed, confirm, archive
- Dry run: Show what would be archived
- Scripts used: `scripts/archive-specs.sh`

**Example**: Load `references/speckit.archive.md` with arguments like `--completed`

**Output**: Archived specs moved to specs/archive/

---

## Additional Commands

### Constitution Setup

**Reference**: `references/speckit.constitution.md`

**Instructions**: Load `references/speckit.constitution.md` for complete execution instructions.

Define project-wide engineering principles that all specs must adhere to.

### Custom Checklists

**Reference**: `references/speckit.checklist.md`

**Instructions**: Load `references/speckit.checklist.md` for complete execution instructions.

Generate custom quality checklists based on user requirements.
**Template**: Uses `assets/checklist-template.md`

### Update Framework

**Reference**: `references/speckit.update.md`

**Instructions**: Load `references/speckit.update.md` for complete execution instructions.

Check for and apply speckit framework updates from upstream.

---

## Bundled Resources

### scripts/

Automation bash scripts executed by workflow commands:

- **create-new-feature.sh**: Initialize new feature branch and spec structure
- **setup-plan.sh**: Prepare planning environment
- **check-prerequisites.sh**: Validate workflow state and available documents
- **update-agent-context.sh**: Update agent-specific context files with new tech
- **archive-specs.sh**: Archive completed or old spec directories
- **common.sh**: Shared utilities for all scripts
- **test-registry.sh**: Test registry management (init, scan, report, spec, retire, validate, export-for-plan)
- **add-test-tags-universal.ts**: Auto-tag existing tests with metadata
- **parse-test-file-universal.ts**: Parse test files and extract metadata (Python, JS/TS, Go, Rust)

**Usage**: Called automatically by workflow commands with JSON output parsing.

### references/

Detailed workflow instructions loaded as needed:

- **speckit.specify.md**: Step 1 - Create specification
- **speckit.clarify.md**: Step 2 - Clarify ambiguities
- **speckit.plan.md**: Step 3 - Generate implementation plan
- **speckit.tasks.md**: Step 4 - Generate task breakdown
- **speckit.analyze.md**: Step 5 - Analyze consistency
- **speckit.implement.md**: Step 6 - Execute implementation
- **speckit.archive.md**: Step 7 - Archive completed specs
- **speckit.constitution.md**: Define project principles
- **speckit.checklist.md**: Generate custom checklists
- **speckit.update.md**: Update speckit framework
- **speckit.di.md**: Pre-or-Post spec design requirements template guide

**Usage**: Load specific reference when executing that workflow step.

### assets/

Templates used to create output files:

- **spec-template.md**: Feature specification structure (what/why, no how)
- **plan-template.md**: Implementation plan structure (technical design)
- **tasks-template.md**: Task breakdown format (organized by user story)
- **checklist-template.md**: Quality checklist structure
- **agent-file-template.md**: Agent context file template
- **design-improvements-template.md**: Pre-or-Post spec design requirements collection

**Usage**: Loaded and filled by workflow commands to create consistent spec/plan/task files.

### memory/

Persistent project knowledge and principles:

- **constitution.md**: Project engineering principles and standards template

**Usage**: Loaded during planning and analysis to validate specs against project principles. Can be customized per project to define MUST/SHOULD standards.

---

## Quality Standards

**Specification Quality**:
- No implementation details
- Focused on user value
- Testable and unambiguous requirements
- Measurable, technology-agnostic success criteria

**Implementation Quality**:
- All tasks mapped to requirements
- Constitution principles followed
- Ignore files configured
- Progress tracked (checkboxes updated)

**Constitution Adherence**:
- MUST principles are mandatory
- Violations flagged as CRITICAL
- Consistency enforced across artifacts

**Testing Standards**:
- Test pyramid: 70% unit, 20% integration, 10% e2e
- All tests tagged with @spec and metadata (see TEST-METADATA-SCHEMA.md)
- Registry auto-initializes during first plan execution
- Brownfield projects: Use `test-registry.sh bootstrap` to tag existing tests
- Automated tracking via test-registry.sh (integrated in plan/tasks/implement steps)

For comprehensive testing guide, see `references/speckit.testing.md`.

---

## Example Full Workflow

```bash
# 1. Create specification
Load references/speckit.specify.md with feature: "Add user authentication with OAuth2"

# 2. Clarify ambiguities (optional)
Load references/speckit.clarify.md

# 3. Generate implementation plan
Load references/speckit.plan.md

# 4. Create task breakdown
Load references/speckit.tasks.md

# 5. Validate consistency (optional)
Load references/speckit.analyze.md

# 6. Execute implementation
Load references/speckit.implement.md

# 7. Archive when complete
Load references/speckit.archive.md with arguments: "--completed"
```

**Result**: Fully specified, planned, and implemented feature with complete audit trail.
