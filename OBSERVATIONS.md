# Observations & Follow-up Items

## Data Accuracy Issues

### Quality assessment metric inconsistency (2025-11-16)
**Observation**: `docmgr_assess_quality` returns contradictory metrics for code block counts.

**Details**:
- **Accuracy criterion**: Reports "Found 9 code blocks across 5 files"
- **Consistency criterion**: Reports "10 code blocks missing language tags"
- **Manual verification**: Actually 9 total blocks, only 1 missing language tag

**Actual counts** (verified manually):
- installation.md: 2 code blocks (both `bash`)
- quick-start.md: 1 code block (`bash`)
- basic-usage.md: 2 code blocks (both `bash`)
- configuration.md: 3 code blocks (all `yaml`)
- index.md: 1 code block (NO language tag)
- **Total**: 9 blocks, 8 with tags, 1 without tags

**Impact**:
- Misleading quality metrics (10x overcounting missing tags)
- Suggests logic error in consistency assessment
- Undermines trust in quality scoring

**Follow-up**:
- [ ] Investigate consistency assessment code in quality.py
- [ ] Check code block counting logic
- [ ] Verify all quality criteria are accurate
- [ ] Add unit tests for quality metrics
