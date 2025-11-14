# Design Improvements Template

## Purpose

The design improvements template (`assets/design-improvements-template.md`) is a **pre or post specification artifact** used to gather and organize visual/UX requirements before creating a formal feature specification.

## When to Use

Use this template when:
- Planning or refinning design-focused features (layout, typography, colors, interactions)
- Collecting visual improvement requirements from stakeholders
- Documenting UI/UX tweaks before formalizing them into a spec, or afterwards when you are refining the result of the completed spec.
- Need structured collection of design changes across multiple components

**This can be used as a a pre-spec tool** - use it BEFORE running `speckit.specify.md`.

**Or a post-spec tool** - or it can be used AFTER the spec has been completed.

## How It Fits the Workflow

```
[Gather Design Requirements] → [Create Formal Spec] → [Plan] → [Tasks] → [Implement] → [Gather Design Enhancements] 
     ↓                              ↓                                                               ↓
design-improvements.md         speckit.specify.md                                          design-improvements.md
```

**Typical flow:**
1. Copy `assets/design-improvements-template.md` to project root
2. Fill in design requirements by category (layout, typography, colors, etc.)
3. Reference this file when creating the formal spec via `speckit.specify.md` - if being used as a pre-spec template.
4. Continue through normal speckit workflow (plan → tasks → implement)

## Template Structure

The template organizes design improvements into categories:

1. **Layout & Spacing** - Component positioning, margins, padding
2. **Typography & Text** - Fonts, sizes, weights, line heights
3. **Colors & Theming** - Color palette, contrast, theme adjustments
4. **Interactive Elements** - Buttons, inputs, hover states, focus states
5. **Component-Specific** - Per-component visual improvements
6. **Responsive & Accessibility** - Mobile/tablet layouts, a11y improvements
7. **Other Improvements** - Misc visual/UX enhancements

Each section includes:
- **Current State** - What exists now
- **Proposed Change** - What should change
- **Rationale** - Why this matters
- **Visual Reference** - Screenshots/pointers (optional)
- **Affected Files** - Components that need updates

## Usage Instructions

### Step 1: Copy Template

```bash
cp .claude/skills/speckit/assets/design-improvements-template.md design-improvements-[spec-stage].md
```

If the design improvements are pre-spec, then copy the template document in as `design-improvements-pre-spec.md`. If the design improvements are post-spec, then copy the template document in as `design-improvements-post-spec.md`.

### Step 2: Fill Requirements

Fill in each relevant section with design requirements. Not all sections need to be used.

**Example:**
```markdown
## 3. Colors & Theming

### 3.1 Segment Background Colors
**Current State:**
- All segments use default background

**Proposed Change:**
- Add subtle background color variations per segment type
- Use theme-aware colors (light/dark mode support)

**Rationale:**
- Improves visual hierarchy
- Makes segment types more distinguishable at a glance

**Affected Files:**
- src/components/SegmentEditor.tsx
- src/styles/segments.css
```

### Step 3: Reference When Creating Spec

When running `speckit.specify.md`, reference the completed design improvements document:

```markdown
Feature: Visual improvements to segment editor UI

Based on requirements gathered in design-improvements.md, implement the following visual enhancements...
```

### Step 4: Continue Normal Workflow

Once the formal spec is created:
- Run `speckit.plan.md` to create technical implementation plan
- Run `speckit.tasks.md` to generate task breakdown
- Run `speckit.implement.md` to execute tasks

## Best Practices

**DO:**
- Be specific about what changes and why
- Include file paths for affected components
- Reference visual examples when available
- Document current state accurately
- Group related changes by category

**DON'T:**
- Include implementation details (save for plan.md)
- Skip the rationale - always explain why
- Create overly broad changes without specifics
- Use this for functional/behavioral changes (use regular spec for that)

## Integration with Speckit Workflow

The design improvements template is **optional** and **complementary** to the main speckit workflow:

- **Not required** for all specs - only use when gathering design requirements
- **Not part of automated workflow** - manually copy and fill as needed
- **Referenced during spec creation** - helps create more complete specifications
- **Lives outside specs/** - typically in project root during requirement gathering

## Example Workflow

```bash
# 1. Start gathering design requirements
cp .claude/skills/speckit/assets/design-improvements-template.md design-improvements-pre-spec.md

# 2. Fill in design requirements
# (Work with stakeholders, document current/proposed states)

# 3. Create formal specification (referencing design-improvements.md)
# Load references/speckit.specify.md with feature description

# 4. Continue normal workflow
# Load references/speckit.plan.md
# Load references/speckit.tasks.md
# Load references/speckit.implement.md

# 5. Archive design improvements doc (optional)
mv design-improvements.md specs/001-feature-name/design-improvements.md
```

## Template Location

**Path**: `.claude/skills/speckit/assets/design-improvements-template.md`

**File Type**: Markdown template

**Size**: Comprehensive template with all design categories pre-structured

## Related Commands

- `references/speckit.specify.md` - Create formal spec (references design improvements)
- `references/speckit.plan.md` - Generate implementation plan from spec
- `assets/spec-template.md` - Main specification template

---

**Remember**: This can be used as a pre-spec or a post-spec collection tool, not a replacement for formal specifications. Use it to organize design thinking before entering the structured speckit workflow.
