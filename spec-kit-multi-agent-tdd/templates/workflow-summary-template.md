# Workflow Summary: {{feature_name}}

**Feature ID:** {{feature_id}}  
**Status:** {{status}}  
**Created:** {{timestamp}}  
**Completed:** {{completion_timestamp}}

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
- **Cycles:** {{arch_review_cycles}}
- **Final Verdict:** APPROVED

### Code Review (Step 9)
- **Path:** `docs/reviews/code-review/{{feature_id}}-code-review.md`
- **Reviewer:** @review
- **Status:** APPROVED
- **Cycles:** {{code_review_cycles}}
- **Final Verdict:** APPROVED

## Review Metrics

**Architecture Review:**
- Total cycles: {{arch_review_cycles}}
- Blockers identified: {{arch_blockers_count}}
- Concerns raised: {{arch_concerns_count}}
- Final status: APPROVED

**Code Review:**
- Total cycles: {{code_review_cycles}}
- Blockers identified: {{code_blockers_count}}
- Concerns raised: {{code_concerns_count}}
- Final status: APPROVED

**Convergence:**
- Deadlock detected: `[YES | NO]`
- Human escalation required: `[YES | NO]`

## Implementation Summary

**Files Changed:**
- Modified: {{files_modified_count}}
- Created: {{files_created_count}}
- Deleted: {{files_deleted_count}}

**Test Coverage:**
- Total tests: {{test_count}}
- Test files: {{test_file_count}}
- Coverage: {{coverage_percentage}}%

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

**Commit Hash:** {{commit_hash}}

**Commit Message:**
```
{{commit_message}}
```

**Branch:** {{branch_name}}

**Pull Request:** {{pr_url}} _(if applicable)_

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

**Workflow Duration:** {{duration_minutes}} minutes  
**Review Efficiency:** {{review_efficiency_score}}/10  
**Agent Coordination:** {{coordination_score}}/10

**Workflow Status:** `[COMPLETED | ESCALATED | FAILED]`
