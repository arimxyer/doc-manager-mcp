---
name: speckit.plan
description: (Step 2) Execute the implementation planning workflow using the plan template to generate design artifacts.
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

1. **Setup**: Run `scripts/setup-plan.sh --json` from repo root and parse JSON for FEATURE_SPEC, IMPL_PLAN, SPECS_DIR, BRANCH. For single quotes in args like "I'm Groot", use escape syntax: e.g 'I'\''m Groot' (or double-quote if possible: "I'm Groot").

2. **Load context**: Read FEATURE_SPEC and `memory/constitution.md`. Load IMPL_PLAN template (already copied from `templates/plan-template.md`).

3. **Initialize test registry** (if not exists):
   - Check if `test-registry.json` exists at repo root
   - If missing:
     - Run `scripts/test-registry.sh init` to create empty registry
     - Run `scripts/test-registry.sh scan` to populate from existing tests
     - Report: "Initialized test registry with [N] tests"
   - If exists: Continue to step 4

4. **Load test coverage**:
   - Run `scripts/test-registry.sh export-for-plan --json` from repo root
   - Parse JSON output for existingTests totals and pyramid status
   - Check orphanedTests count:
     - If > 0: Note "Found [N] untagged tests. Consider running: test-registry.sh bootstrap --spec <number>"
     - Brownfield projects benefit from bootstrap before planning

5. **Document testing strategy**: Fill the "Testing Strategy" section in plan.md:
   - Coverage Baseline: Use data from step 4 (total tests, pyramid health)
   - Test Pyramid Targets: Calculate expected distribution (70% unit, 20% integration, 10% e2e)
   - Component Test Coverage: Map spec requirements to test types needed
   - Note if bootstrap is recommended for untagged tests

6. **Execute plan workflow**: Follow the structure in IMPL_PLAN template to:
   - Fill Technical Context (mark unknowns as "NEEDS CLARIFICATION")
   - Fill Constitution Check section from constitution
   - Evaluate gates (ERROR if violations unjustified)
   - Phase 0: Generate research.md (resolve all NEEDS CLARIFICATION)
   - Phase 1: Generate data-model.md, contracts/, quickstart.md
   - Phase 1: Update agent context by running the agent script
   - Re-evaluate Constitution Check post-design

7. **Stop and report**: Command ends after Phase 2 planning. Report branch, IMPL_PLAN path, and generated artifacts.

## Phases

### Phase 0: Outline & Research

1. **Extract unknowns from Technical Context** above:
   - For each NEEDS CLARIFICATION → research task
   - For each dependency → best practices task
   - For each integration → patterns task

2. **Generate and dispatch research agents**:

   ```text
   For each unknown in Technical Context:
     Task: "Research {unknown} for {feature context}"
   For each technology choice:
     Task: "Find best practices for {tech} in {domain}"
   ```

3. **Consolidate findings** in `research.md` using format:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]

**Output**: research.md with all NEEDS CLARIFICATION resolved

### Phase 1: Design & Contracts

**Prerequisites:** `research.md` complete

1. **Extract entities from feature spec** → `data-model.md`:
   - Entity name, fields, relationships
   - Validation rules from requirements
   - State transitions if applicable

2. **Generate API contracts** from functional requirements:
   - For each user action → endpoint
   - Use standard REST/GraphQL patterns
   - Output OpenAPI/GraphQL schema to `/contracts/`

3. **Agent context update**:
   - Run `scripts/update-agent-context.sh claude`
   - These scripts detect which AI agent is in use
   - Update the appropriate agent-specific context file
   - Add only new technology from current plan
   - Preserve manual additions between markers

**Output**: data-model.md, /contracts/*, quickstart.md, agent-specific file

## Key rules

- Use absolute paths
- ERROR on gate failures or unresolved clarifications
