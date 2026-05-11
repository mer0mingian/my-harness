# Workflow Summary: {{feature_name}}

**Feature ID:** {{feature_id}}  
**Status:** {{status|default("draft")}}  
**Created:** {{timestamp}}  
**Completed:** {{completion_timestamp|default("N/A")}}

## Workflow Overview

**Feature Specification:**
- Spec location: _path/to/spec.md_
- Requirements count: _X_
- Acceptance criteria: _X_

**Workflow Steps Completed:**
- [x] Step 0: Interactive Planning (optional)
- [x] Step 7: Write Tests
- [x] Step 8: Implement
- [x] Step 9: Review (Architecture + Code)
- [x] Step 10: Commit & Document

## Artifact Trail

_Links to all artifacts created during workflow:_

### Test Design (Step 7)
- **Path:** `docs/tests/test-design/{{feature_id}}-test-design.md`
- **Agent:** @test
- **Status:** COMPLETED
- **RED State:** Valid (MISSING_BEHAVIOR confirmed)

### Implementation Notes (Step 8)
- **Path:** `docs/implementation/{{feature_id}}-implementation-notes.md`
- **Agent:** @implement
- **Status:** COMPLETED
- **GREEN State:** All tests passing

### Architecture Review (Step 9)
- **Path:** `docs/reviews/arch-review/{{feature_id}}-arch-review.md`
- **Reviewer:** @arch
- **Status:** APPROVED
- **Cycles:** {{arch_review_cycles|default(1)}}
- **Final Verdict:** APPROVED

### Code Review (Step 9)
- **Path:** `docs/reviews/code-review/{{feature_id}}-code-review.md`
- **Reviewer:** @review
- **Status:** APPROVED
- **Cycles:** {{code_review_cycles|default(1)}}
- **Final Verdict:** APPROVED

## Review Metrics

**Architecture Review:**
- Total cycles: {{arch_review_cycles|default(1)}}
- Blockers identified: {{arch_blockers_count|default(0)}}
- Concerns raised: {{arch_concerns_count|default(0)}}
- Final status: APPROVED

**Code Review:**
- Total cycles: {{code_review_cycles|default(1)}}
- Blockers identified: {{code_blockers_count|default(0)}}
- Concerns raised: {{code_concerns_count|default(0)}}
- Final status: APPROVED

**Convergence:**
- Deadlock detected: `[YES | NO]`
- Human escalation required: `[YES | NO]`

## Implementation Summary

**Files Changed:**
- Modified: {{files_modified_count|default(0)}}
- Created: {{files_created_count|default(0)}}
- Deleted: {{files_deleted_count|default(0)}}

**Test Coverage:**
- Total tests: {{test_count|default(0)}}
- Test files: {{test_file_count|default(0)}}
- Coverage: {{coverage_percentage|default(0)}}%

**Key Components:**
- _Component1_ - _brief description_
- _Component2_ - _brief description_

## Quality Assurance

**Constitutional Compliance:**
- [x] Test Design artifact created (mandatory)
- [x] Valid RED state confirmed
- [x] GREEN state achieved
- [x] Architecture review completed (mandatory)
- [x] Code review completed (mandatory)
- [x] All quality gates passed

**Gate Results:**
- RED state validation: PASSED
- Architecture review: APPROVED
- Code review: APPROVED
- Test execution: ALL PASSING

## Technical Debt

_Items deferred to future work:_
- [ ] _Deferred item 1_ (from: arch review, priority: medium)
- [ ] _Deferred item 2_ (from: code review, priority: low)

## Escalations

_Any issues escalated to humans:_
- _None_ | _List of escalations with resolution_

## Commit Information

**Commit Hash:** {{commit_hash|default("N/A")}}

**Commit Message:**
```
{{commit_message|default("N/A")}}
```

**Branch:** {{branch_name|default("N/A")}}

**Pull Request:** {{pr_url|default("N/A")}} _(if applicable)_

## Lessons Learned

_Observations from this workflow cycle:_
- **What went well:** _successes_
- **What could improve:** _challenges_
- **Process insights:** _learnings_

## Next Steps

_Recommended follow-up actions:_
- [ ] Deploy to staging
- [ ] User acceptance testing
- [ ] Documentation updates
- [ ] Performance testing

---

**Workflow Duration:** {{duration_minutes|default(0)}} minutes  
**Review Efficiency:** {{review_efficiency_score|default(0)}}/10  
**Agent Coordination:** {{coordination_score|default(0)}}/10

**Workflow Status:** `[COMPLETED | ESCALATED | FAILED]`
