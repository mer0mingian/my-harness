# Phase 2 Updated Plan: Orchestrated Execution Command

**Version:** 1.1 (Updated)  
**Date:** 2026-05-07  
**Status:** Planning  
**Changes:** Added `/speckit.multi-agent.execute` orchestrating command

---

## Executive Summary

Phase 2 implements the **Multi-Agent TDD Workflow commands** with a **streamlined orchestration layer**. Instead of requiring users to run 4 separate commands, the system provides a single `/speckit.multi-agent.execute` command that orchestrates the full pipeline while maintaining specialist agent delegation.

**Key Change from Original Plan:**
- **Original:** Users run 4 commands sequentially: `test → implement → review → commit`
- **Updated:** Users run 1 command: `execute` (which internally orchestrates the 4 subcommands)

---

## Command Architecture

### Layer 1: Subcommands (Specialists)
Individual workflow steps, each delegating to specialist agents:

1. **`/speckit.multi-agent.test`** (Slice 3)
   - Agent: @test specialist
   - Creates: Test design artifact, failing tests
   - Gates: File gate, RED state validation

2. **`/speckit.multi-agent.implement`** (Slice 4)
   - Agent: @make specialist
   - Creates: Implementation, GREEN state
   - Gates: TDD entry (RED before GREEN), integration tests

3. **`/speckit.multi-agent.review`** (Slice 5)
   - Agents: @check + @simplify (parallel)
   - Creates: Arch review + code review artifacts
   - Gates: Review cycles (max 3), conflict resolution

4. **`/speckit.multi-agent.commit`** (Slice 6)
   - Agent: Orchestrator (not specialist)
   - Creates: Workflow summary, git commit, PR
   - Gates: Artifact validation, evidence requirements

### Layer 2: Orchestrator (NEW)
Single command that orchestrates the full pipeline:

**`/speckit.multi-agent.execute`** (Slice 3.5 - NEW)
- **Purpose:** Run full TDD workflow (steps 7-10) in one command
- **Implementation:** Invokes subcommands sequentially
- **Agent:** Orchestrator (manages flow, not implementation)
- **Error Handling:** Halts on gate failures, escalates to human

---

## Updated Phase 2 Roadmap

### Slice 3: Step 7 - Write Tests Workflow (4-5 hours)
**Command:** `/speckit.multi-agent.test <feature-id>`

**Implementation Tasks:**
- S3-001: Create test design artifact template (1 hr)
- S3-002: Implement test command (2.5 hrs)
- S3-003: File gate validation (1.5 hrs)
- S3-004: Failure code detection (2 hrs)
- S3-005: Escalation logic (1 hr)
- S3-006: End-to-end testing (1 hr)

**Deliverables:**
- `spec-kit-multi-agent-tdd/commands/test.py` (or `.sh`)
- File gate enforcement (only test patterns allowed)
- RED state validation with failure codes
- Test design artifact generation

**Acceptance Criteria:**
- [ ] Command spawns @test agent with context
- [ ] Agent writes failing tests (RED state)
- [ ] File gate blocks non-test files
- [ ] Valid failure codes accepted (MISSING_BEHAVIOR, ASSERTION_MISMATCH)
- [ ] Invalid codes escalate (TEST_BROKEN, ENV_BROKEN)
- [ ] Test design artifact created

---

### Slice 3.5: Orchestrator - Execute Command (NEW, 3-4 hours)
**Command:** `/speckit.multi-agent.execute <feature-id> [--mode=auto|interactive]`

**Purpose:** Streamlined invocation of full TDD workflow (steps 7-10).

**Implementation Tasks:**
- S3.5-001: Create execute command scaffold (1 hr)
- S3.5-002: Implement subcommand orchestration (2 hrs)
- S3.5-003: Error handling and gate enforcement (1.5 hrs)
- S3.5-004: Interactive mode integration (1 hr)
- S3.5-005: End-to-end testing (1 hr)

**Workflow Logic:**
```python
def execute_workflow(feature_id, mode='auto'):
    """
    Orchestrate full TDD workflow by invoking subcommands.
    Each subcommand delegates to specialist agents.
    """
    
    # Step 7: Write Tests
    result = invoke_subcommand('test', feature_id)
    if result.status == 'BLOCKED':
        escalate_to_human("Test generation blocked", result.details)
        return
    
    # Step 8: Implement
    result = invoke_subcommand('implement', feature_id)
    if result.status == 'RED_FAILED':
        escalate_to_human("Tests already passing (no work needed)", result.details)
        return
    if result.status == 'GREEN_FAILED':
        escalate_to_human("Implementation failed to achieve GREEN", result.details)
        return
    
    # Step 9: Review
    result = invoke_subcommand('review', feature_id)
    if result.verdict == 'BLOCKED':
        escalate_to_human("Review blocked by safety constraints", result.details)
        return
    if result.cycles_exceeded:
        escalate_to_human("Review convergence failed after 3 cycles", result.details)
        return
    
    # Step 10: Commit
    result = invoke_subcommand('commit', feature_id)
    if result.status == 'VALIDATION_FAILED':
        escalate_to_human("Artifact validation failed", result.details)
        return
    
    # Success!
    return WorkflowSummary(
        feature_id=feature_id,
        status='COMPLETED',
        commit_sha=result.commit_sha,
        artifacts=result.artifacts
    )
    
    # NOTE: PR creation removed from Phase 2 scope (future enhancement)
```

**Modes:**
- **`auto` (default):** Run all 4 steps sequentially, halt on failures
- **`interactive`:** Prompt user between steps (grill-me integration)
- **`--gate-mode=manual`:** Require human approval at configured gates

**Error Handling:**
- Each subcommand returns status: `SUCCESS | BLOCKED | FAILED`
- Orchestrator halts on `BLOCKED` or `FAILED`
- Escalation includes:
  - Current step that failed
  - Reason (failure code, validation error, etc.)
  - Recommended action (fix test, resolve review, etc.)
  - Partial artifacts generated (for debugging)

**Deliverables:**
- `spec-kit-multi-agent-tdd/commands/execute.py`
- Orchestration logic (subcommand invocation)
- Error handling and escalation
- Workflow summary generation

**Acceptance Criteria:**
- [ ] Command invokes all 4 subcommands sequentially
- [ ] Halts on first gate failure
- [ ] Escalates to human with clear diagnostics
- [ ] Workflow summary created on success
- [ ] Interactive mode prompts between steps (if enabled)
- [ ] Manual gate mode waits for approval

---

### Slice 4: Step 8 - Implement Workflow (4-5 hours)
**Command:** `/speckit.multi-agent.implement <feature-id>`

**Implementation Tasks:**
- S4-001: Create implementation notes template (45 min)
- S4-002: Implement command (2.5 hrs)
- S4-003: TDD entry validation (RED before GREEN) (2 hrs)
- S4-004: GREEN state validation (1.5 hrs)
- S4-005: Integration validation (1.5 hrs)
- S4-006: End-to-end testing (1 hr)

**Deliverables:**
- `spec-kit-multi-agent-tdd/commands/implement.py`
- TDD entry validation (run tests, verify RED)
- GREEN state achievement verification
- Integration test execution
- Implementation notes artifact (optional)

**Acceptance Criteria:**
- [ ] Command reads test design artifact from step 7
- [ ] TDD validation: tests must fail before implementation
- [ ] Agent implements code to achieve GREEN
- [ ] All tests pass after implementation
- [ ] Integration checks run (linting, type checking)
- [ ] RED→GREEN evidence captured

---

### Slice 5: Step 9 - Review Workflow (Parallel Agents) (5-6 hours)
**Command:** `/speckit.multi-agent.review <feature-id>`

**Implementation Tasks:**
- S5-001: Create arch review template (1 hr)
- S5-002: Create code review template (1 hr)
- S5-003: Implement review command (3 hrs)
- S5-004: Conflict resolution logic (2 hrs)
- S5-005: Review cycle management (1.5 hrs)
- S5-006: Verdict enforcement (1 hr)
- S5-007: End-to-end testing (1.5 hrs)

**Deliverables:**
- `spec-kit-multi-agent-tdd/commands/review.py`
- Parallel agent execution (@check + @simplify)
- Conflict resolution (safety wins)
- Review cycle management (max 3)
- Arch review + code review artifacts

**Acceptance Criteria:**
- [ ] Command spawns @check and @simplify in parallel
- [ ] Both reviews complete independently
- [ ] Conflicts detected and resolved (safety wins)
- [ ] Review cycles tracked (max 3)
- [ ] BLOCKED verdict halts workflow
- [ ] Both review artifacts created

---

### Slice 6: Step 10 - Commit & Workflow Summary (3-4 hours)
**Command:** `/speckit.multi-agent.commit <feature-id>`

**Implementation Tasks:**
- S6-001: Create workflow summary template (1.5 hrs)
- S6-002: Implement commit command (2.5 hrs)
- S6-003: Artifact validation (1.5 hrs)
- S6-004: Evidence validation (1.5 hrs)
- S6-005: Git commit logic (1 hr)
- S6-006: End-to-end testing (1 hr)

**Deliverables:**
- `spec-kit-multi-agent-tdd/commands/commit.py`
- Artifact validation (all mandatory present)
- Evidence validation (RED→GREEN proof)
- Git commit creation
- Workflow summary artifact

**Acceptance Criteria:**
- [ ] Command validates all mandatory artifacts exist
- [ ] Evidence requirements validated (test outputs)
- [ ] Workflow summary created with all sections
- [ ] Git commit includes all artifacts
- [ ] Spec lifecycle updated to `Status: Implemented`

---

## Command Invocation Examples

### Original Approach (Still Supported)
```bash
# Step-by-step workflow
specify multi-agent test feat-123
specify multi-agent implement feat-123
specify multi-agent review feat-123
specify multi-agent commit feat-123
```

### New Streamlined Approach (Recommended)
```bash
# Single command for full workflow
specify multi-agent execute feat-123

# Interactive mode (with grill-me prompts)
specify multi-agent execute feat-123 --mode=interactive

# Manual gating (wait for approval between steps)
specify multi-agent execute feat-123 --gate-mode=manual
```

---

## Updated Phase 2 Timeline

**CRITICAL UPDATE (2026-05-07):** Architectural correction required before Phase 2 completion.

**Issue:** Commands implemented as Python scripts, incompatible with SpecKit architecture (must be markdown).

**Correction:** 12.5 hours to convert Python commands → markdown + helper scripts + hooks

See: [ARCHITECTURAL-CORRECTION-PLAN.md](../../spec-kit-multi-agent-tdd/docs/archive/ARCHITECTURAL-CORRECTION-PLAN.md)

**Revised Timeline:**
- Slice 3: 4-5 hours (test command) - ✅ DONE (needs conversion)
- Slice 3.5: 3-4 hours (execute command) - ✅ DONE (needs conversion)
- Slice 4: 4-5 hours (implement command) - ✅ DONE (needs conversion)
- **Architectural Correction: 12.5 hours** - ⚠️ BLOCKING
  - Phase 1-3: Create helper scripts + hooks (6.5h)
  - Phase 4: Convert 5 commands to markdown (6h)
- Slice 5: 5-6 hours (review command) - 🔄 PARTIAL (needs completion + conversion)
- Slice 6: 3-4 hours (commit command) - 🔄 PARTIAL (needs completion + conversion)
- **Total: 33-37 hours** (was 20-24 hrs before correction)

**Critical Path:** Architectural correction → Complete Slice 5-6 → Phase 2 done

---

## Benefits of Execute Command

**For Users:**
1. **Simplified invocation:** One command instead of four
2. **Automatic error handling:** Halts at first failure, clear diagnostics
3. **Progress visibility:** Shows current step, artifacts generated
4. **Partial completion:** Artifacts saved even if workflow fails mid-step

**For Orchestrator:**
1. **Maintains specialist delegation:** Each subcommand still uses specialist agents
2. **Constitutional compliance:** All gates enforced (non-bypassable)
3. **Error recovery:** Clear escalation paths, no silent failures
4. **Audit trail:** Workflow summary includes all step outcomes

**For Teams:**
1. **Easier onboarding:** New developers use one command
2. **Consistent workflows:** Reduces human error (skipping steps)
3. **CI/CD integration:** Single command in automation pipelines
4. **Interactive mode:** Grill-me integration for planning during execution

---

## Implementation Strategy for Slice 3.5

### Subcommand Invocation Pattern
```python
# spec-kit-multi-agent-tdd/commands/execute.py

import subprocess
from pathlib import Path
from typing import Dict, Any

def invoke_subcommand(cmd: str, feature_id: str, **kwargs) -> Dict[str, Any]:
    """
    Invoke a workflow subcommand.
    
    Args:
        cmd: Subcommand name (test, implement, review, commit)
        feature_id: Feature identifier
        **kwargs: Additional command arguments
    
    Returns:
        Command result with status, artifacts, errors
    """
    # Build command
    cmd_path = Path(__file__).parent / f"{cmd}.py"
    args = ['python', str(cmd_path), feature_id]
    
    # Add optional flags
    for key, value in kwargs.items():
        args.extend([f'--{key}', str(value)])
    
    # Execute
    result = subprocess.run(
        args,
        capture_output=True,
        text=True,
        cwd=Path.cwd()
    )
    
    # Parse output (JSON response from subcommand)
    return {
        'status': parse_status(result.stdout),
        'artifacts': parse_artifacts(result.stdout),
        'errors': result.stderr if result.returncode != 0 else None
    }
```

### Gate Enforcement
All existing gate logic from subcommands is preserved:
- File gate (Slice 3)
- RED state validation (Slice 3)
- TDD entry validation (Slice 4)
- GREEN state validation (Slice 4)
- Review verdict enforcement (Slice 5)
- Artifact validation (Slice 6)
- Evidence validation (Slice 6)

The execute command **does not bypass** any gates; it simply orchestrates subcommand invocation.

---

## Updated Success Criteria

Phase 2 is complete when:

1. **All 5 commands functional:**
   - [ ] `/speckit.multi-agent.test` (Slice 3)
   - [ ] `/speckit.multi-agent.execute` (Slice 3.5) — **NEW**
   - [ ] `/speckit.multi-agent.implement` (Slice 4)
   - [ ] `/speckit.multi-agent.review` (Slice 5)
   - [ ] `/speckit.multi-agent.commit` (Slice 6)

2. **Execute command orchestrates full workflow:**
   - [ ] Invokes all 4 subcommands sequentially
   - [ ] Halts on first gate failure
   - [ ] Escalates with clear diagnostics
   - [ ] Workflow summary created on success

3. **All quality gates enforce:**
   - [ ] File gate (test only)
   - [ ] RED state validation
   - [ ] TDD entry validation (RED before GREEN)
   - [ ] Review verdict enforcement (BLOCKED halts)
   - [ ] Artifact validation (mandatory present)
   - [ ] Evidence validation (RED→GREEN proof)

4. **All artifacts created:**
   - [ ] Test design (Step 7)
   - [ ] Implementation notes (Step 8, optional)
   - [ ] Arch review (Step 9)
   - [ ] Code review (Step 9)
   - [ ] Workflow summary (Step 10)

5. **End-to-end workflow executes:**
   - [ ] `specify multi-agent execute feat-123` completes successfully
   - [ ] All artifacts generated
   - [ ] Git commit created
   - [ ] PR created (if configured)

---

## Migration Notes

**Backward Compatibility:**
- Individual subcommands (`test`, `implement`, `review`, `commit`) remain available
- Teams can choose step-by-step or orchestrated approach
- Configuration works for both approaches

**Recommended Usage:**
- **Development:** Use `execute` command for full workflow
- **Debugging:** Use individual commands when troubleshooting specific steps
- **CI/CD:** Use `execute` command in automation pipelines

---

## Next Steps

1. **Implement Slice 3** (test command) — foundation for workflow
2. **Implement Slice 3.5** (execute command) — orchestration layer
3. **Implement Slice 4** (implement command) — TDD cycle
4. **Implement Slice 5** (review command) — parallel review agents
5. **Implement Slice 6** (commit command) — finalization
6. **End-to-end testing** with execute command

---

## Related Documents

- [TASK-LIST-Multi-Agent-TDD.md](TASK-LIST-Multi-Agent-TDD.md) — Granular task breakdown
- [ROADMAP-Multi-Agent-TDD.md](ROADMAP-Multi-Agent-TDD.md) — Timeline and dependencies
- [PLAN-Multi-Agent-TDD-Implementation.md](PLAN-Multi-Agent-TDD-Implementation.md) — Original vertical slices
- [CONSTITUTION-Multi-Agent-TDD.md](CONSTITUTION-Multi-Agent-TDD.md) — Non-bypassable principles
- [ARTIFACT-SUMMARY.md](ARTIFACT-SUMMARY.md) — Artifact templates and configuration
