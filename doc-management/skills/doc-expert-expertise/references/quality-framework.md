# Quality Assessment Framework

Comprehensive guide to evaluating documentation against 7 professional criteria.

## The 7 Quality Criteria

### 1. Relevance

**Definition**: Documentation addresses current user needs and use cases.

**Scoring**:
| Score | Criteria |
|-------|----------|
| Good | Covers all current features, addresses common questions, up-to-date examples |
| Fair | Most features covered, some outdated sections, minor gaps |
| Poor | Missing major features, significantly outdated, doesn't match current usage |

**Evaluation Questions**:
- Does it cover features users actually use?
- Are examples based on current API/behavior?
- Does it address frequently asked questions?
- Is deprecated content clearly marked or removed?

**Common Issues**:
- Documenting removed features
- Examples using old API patterns
- Missing documentation for new features
- Not addressing common user pain points

---

### 2. Accuracy

**Definition**: Documentation reflects the actual state of the codebase.

**Scoring**:
| Score | Criteria |
|-------|----------|
| Good | All types, parameters, returns match code exactly |
| Fair | Minor discrepancies, mostly accurate |
| Poor | Significant mismatches, misleading information |

**Evaluation Questions**:
- Do parameter types match function signatures?
- Do return types match actual returns?
- Are exception/error cases documented correctly?
- Do code examples actually work?

**Common Issues**:
- Parameter type mismatches (str vs dict)
- Missing or incorrect return types
- Undocumented exceptions
- Code examples that don't compile/run

**Verification Method**:
- Cross-reference with source code
- Run `docmgr_validate_docs` with `validate_symbols=true`

---

### 3. Purposefulness

**Definition**: Documentation has clear goals and defined target audience.

**Scoring**:
| Score | Criteria |
|-------|----------|
| Good | Clear audience, stated goals, appropriate depth |
| Fair | Implicit audience, goals unclear but inferable |
| Poor | No clear audience, unfocused content, inconsistent depth |

**Evaluation Questions**:
- Who is this documentation for?
- What should they be able to do after reading?
- Is the depth appropriate for the audience?
- Is there a clear structure/progression?

**Common Issues**:
- Mixing beginner and advanced content
- No clear learning path
- Missing "who is this for" context
- Inconsistent assumed knowledge

---

### 4. Uniqueness

**Definition**: No redundant or conflicting information.

**Scoring**:
| Score | Criteria |
|-------|----------|
| Good | Single source of truth, no duplication |
| Fair | Minor duplication, consistent information |
| Poor | Significant duplication, conflicting information |

**Evaluation Questions**:
- Is the same information documented in multiple places?
- If duplicated, is it consistent?
- Are there conflicting instructions?
- Is there a single source of truth?

**Common Issues**:
- Same API documented in multiple files
- Conflicting installation instructions
- Outdated duplicates not updated
- Copy-paste documentation drift

---

### 5. Consistency

**Definition**: Aligned terminology, formatting, and style throughout.

**Scoring**:
| Score | Criteria |
|-------|----------|
| Good | Uniform style, consistent terminology, standard formatting |
| Fair | Mostly consistent, minor variations |
| Poor | Inconsistent style, mixed terminology, varying formats |

**Evaluation Questions**:
- Is terminology used consistently?
- Are code blocks formatted the same way?
- Do headings follow a consistent pattern?
- Are similar concepts documented similarly?

**Common Issues**:
- Mixed terminology ("function" vs "method" vs "procedure")
- Inconsistent code block languages
- Varying heading structures
- Different date/version formats

---

### 6. Clarity

**Definition**: Precise language and clear navigation.

**Scoring**:
| Score | Criteria |
|-------|----------|
| Good | Clear language, easy to find information, good examples |
| Fair | Generally clear, some confusing sections |
| Poor | Unclear language, hard to navigate, missing examples |

**Evaluation Questions**:
- Can users find what they need quickly?
- Are explanations easy to understand?
- Are there helpful examples?
- Is jargon explained or avoided?

**Common Issues**:
- Overly technical language without explanation
- Missing code examples
- Poor navigation structure
- Ambiguous instructions

---

### 7. Structure

**Definition**: Logical organization and hierarchy.

**Scoring**:
| Score | Criteria |
|-------|----------|
| Good | Logical flow, appropriate hierarchy, good categorization |
| Fair | Reasonable structure, some organizational issues |
| Poor | Disorganized, unclear hierarchy, poor categorization |

**Evaluation Questions**:
- Is information logically organized?
- Does the hierarchy make sense?
- Can users follow a natural progression?
- Are related topics grouped together?

**Common Issues**:
- Random organization
- Too flat or too deep hierarchy
- Related topics scattered across files
- No clear information architecture

---

## Overall Assessment

**Calculating Overall Score**:
- **Excellent**: All criteria Good
- **Good**: No Poor scores, majority Good
- **Fair**: No more than 1 Poor, majority Fair or better
- **Poor**: 2+ Poor scores OR critical accuracy issues

**Priority Order** (for fixing):
1. Accuracy - Incorrect docs are worse than no docs
2. Relevance - Out-of-date docs mislead users
3. Clarity - Confusing docs frustrate users
4. Structure - Hard to navigate docs waste time
5. Consistency - Inconsistency looks unprofessional
6. Uniqueness - Duplication causes maintenance burden
7. Purposefulness - Unclear focus reduces effectiveness

---

## Quality Gate Thresholds

**For baseline update**:
- No "Poor" scores required
- All "Fair" or better acceptable

**For release**:
- Accuracy must be "Good"
- No "Poor" scores
- Recommend all criteria "Fair" or better

**For feedback loop**:
- Focus on "Poor" scores first
- Max 3 iterations before escalation
- Provide specific file:line feedback
