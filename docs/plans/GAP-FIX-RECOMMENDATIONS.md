# Gap Fix Recommendations - Phase 2 Multi-Agent TDD

**Date:** 2026-05-07  
**Based On:** User clarifications + evaluation findings  
**Authority:** CONSTITUTION > PRD > TASK-LIST

---

## Priority 0: Critical Constitutional Violations

### P0-1: Test Immutability Not Enforced (Slice 4)

**Gap:** S4-002 only detects test modifications but doesn't reject them  
**Constitutional Authority:** Lines 90-119 - "@make agent MUST NOT modify test files"  
**User Clarification:** Constitution is authoritative for all gates

**Fix:**
```python
# In commands/implement.py

def validate_implementation_changes(feature_id: str, config: dict) -> tuple[bool, str]:
    """
    Validate @make agent did not modify test files.
    Returns (valid, error_message)
    """
    # Get test file patterns from config
    test_patterns = config.get('test_patterns', {}).get('test_files', ['**/test_*.py', '**/*_test.py'])
    
    # Get changed files from git diff
    result = subprocess.run(
        ['git', 'diff', '--name-only', 'HEAD'],
        capture_output=True, text=True, check=True
    )
    changed_files = result.stdout.strip().split('\n')
    
    # Check if any test files were modified
    for file_path in changed_files:
        if any(fnmatch.fnmatch(file_path, pattern) for pattern in test_patterns):
            return False, (
                f"CONSTITUTIONAL VIOLATION: Test file modified: {file_path}\n"
                f"@make agent MUST NOT modify test files (CONSTITUTION lines 90-119).\n"
                f"Implementation REJECTED. Escalating to human."
            )
    
    return True, ""

# In main execution:
valid, error = validate_implementation_changes(feature_id, config)
if not valid:
    print(error, file=sys.stderr)
    sys.exit(2)  # Exit code 2 = constitutional violation
```

**Acceptance Criteria Update:**
- S4-002 AC#2: Change from "Detect and escalate" → "Reject modifications, fail with exit code 2"
- S4-006: Add test case for test file modification rejection

**Files Changed:**
- `commands/implement.py`: Add validation function, exit on violation
- `tests/test_command_implement.py`: Add test for rejection behavior
- `docs/plans/TASK-LIST-Multi-Agent-TDD.md`: Update S4-002 AC#2

---

### P0-2: File Gate Bypass Clause (Slice 3)

**Gap:** S3-003 AC#3 allows "--bypass-file-gate flag"  
**Constitutional Authority:** Line 178 - "Non-bypassable gates...cannot be disabled"  
**User Clarification:** Human gates don't need enforcement at this stage (retrieval only)

**Fix:**
Remove bypass flag entirely. File gate is constitutional, not human-interactive.

**Files Changed:**
- `docs/plans/TASK-LIST-Multi-Agent-TDD.md`: Remove S3-003 AC#3 entirely
- `commands/test.py`: Confirm no bypass flag exists (already correct in implementation)
- `docs/plans/CONSTITUTION-Multi-Agent-TDD.md`: No changes (already correct)

**Action:** Documentation fix only - implementation already compliant.

---

### P0-3: Integration Test Philosophy (Slice 4)

**Gap:** S4-005 AC#4 "Fail if integration tests don't pass" contradicts CONSTITUTION line 144  
**Constitutional Authority:** "Integration test failures are evidence...not blockers"  
**User Clarification:** Constitution is authority

**Fix:**
```python
# In commands/implement.py

def validate_integration_tests(feature_id: str, config: dict) -> dict:
    """
    Run integration tests and capture evidence.
    Per CONSTITUTION line 144: Failures are evidence, not blockers.
    """
    result = subprocess.run(
        ['pytest', '-v', '--tb=short', 'tests/integration/'],
        capture_output=True, text=True
    )
    
    evidence = parse_test_evidence.parse_pytest_output(result.stdout)
    
    # Return evidence regardless of pass/fail
    return {
        'ran': True,
        'total': evidence.total_tests,
        'passed': evidence.passed,
        'failed': evidence.failed,
        'evidence': evidence,
        'note': 'Integration test failures are evidence, not blockers (CONSTITUTION line 144)'
    }

# Do NOT check return code or exit on failures
```

**Acceptance Criteria Update:**
- S4-005 AC#4: Change from "Fail if integration tests don't pass" → "Capture integration test evidence (pass or fail)"
- S4-005: Add note that failures go in implementation notes artifact, not block workflow

**Files Changed:**
- `commands/implement.py`: Run integration tests, capture evidence, never block
- `templates/implementation-notes-template.md`: Add "Integration Test Evidence" section
- `docs/plans/TASK-LIST-Multi-Agent-TDD.md`: Update S4-005 AC#4
- `tests/test_command_implement.py`: Test that failures don't block (exit code 0)

---

## Priority 1: Missing PRD Features (Adjusted for User Clarifications)

### P1-1: Local Jira Structure (Replaces Linear Integration)

**Gap:** No artifact persistence for team sync  
**User Clarification:** Create local folder structure (Epic/Task), enhance later for Jira sync

**Fix:**
```bash
# Directory structure in project root
.specify/
├── epics/
│   ├── epic-001-user-authentication/
│   │   ├── EPIC.md                    # Epic metadata (Jira Epic fields)
│   │   ├── story-001-login-flow.md    # Jira story
│   │   └── story-002-password-reset.md
│   └── epic-002-payment-processing/
│       └── story-003-stripe-integration.md
└── harness-tdd-config.yml

# EPIC.md format
---
epic_id: epic-001
epic_key: AUTH-001  # Future Jira Epic key
title: User Authentication
status: In Progress
stories:
  - story-001
  - story-002
---

# Epic: User Authentication
[Description, acceptance criteria, value statement]

# story-001-login-flow.md format
---
story_id: story-001
story_key: AUTH-101  # Future Jira Story key
epic: epic-001
title: Implement login flow
status: In Progress
feature_id: feat-auth-login  # Links to .specify/specs/ artifact
---

# Story: Implement login flow
[User story, acceptance criteria]

## Workflow Artifacts
- Spec: `docs/features/feat-auth-login.md`
- Test Design: `docs/features/feat-auth-login-test-design.md`
- Implementation Notes: `docs/features/feat-auth-login-impl-notes.md`
- Reviews: `docs/features/feat-auth-login-arch-review.md`, `...-code-review.md`
- Workflow Summary: `docs/features/feat-auth-login-workflow-summary.md`
```

**Implementation:**
- Add `lib/jira_local.py` with functions:
  - `create_epic_folder(epic_id, title) -> Path`
  - `create_story_file(epic_id, story_id, title, feature_id) -> Path`
  - `update_story_status(story_id, status)`
  - `link_artifacts_to_story(story_id, artifacts: list[Path])`

**Files Changed:**
- `lib/jira_local.py`: New file for local Jira structure
- `commands/commit.py`: Call `link_artifacts_to_story()` after commit
- `harness-tdd-config.yml.template`: Add `jira.local_mode: true`
- `docs/plans/TASK-LIST-Multi-Agent-TDD.md`: Update S6-006 to include local structure

**Note:** Team sync with actual Jira is Phase 3+ enhancement (API calls, webhook listeners, etc.)

---

### P1-2: PR Creation (Delegated to Orchestrator)

**Gap:** PRD lines 157-180 mention PR creation  
**User Clarification:** Orchestrator (Slice 3.5) handles PR, not commit command

**Fix:**
Remove PR creation from S6-005. Orchestrator calls Bitbucket API after successful commit.

```python
# In commands/execute.py (Slice 3.5)

def create_pull_request(feature_id: str, workflow_summary_path: Path) -> dict:
    """
    Create Bitbucket pull request after successful workflow.
    Uses Bitbucket REST API (not gh cli).
    """
    # Read workflow summary for PR description
    with open(workflow_summary_path, encoding='utf-8') as f:
        summary_content = f.read()
    
    # Extract commit SHA from git log
    result = subprocess.run(
        ['git', 'log', '-1', '--format=%H'],
        capture_output=True, text=True, check=True
    )
    commit_sha = result.stdout.strip()
    
    # Get current branch
    result = subprocess.run(
        ['git', 'branch', '--show-current'],
        capture_output=True, text=True, check=True
    )
    source_branch = result.stdout.strip()
    
    # Construct PR title from first commit line
    result = subprocess.run(
        ['git', 'log', '-1', '--format=%s'],
        capture_output=True, text=True, check=True
    )
    pr_title = result.stdout.strip()
    
    # Construct PR description with artifact links
    pr_description = f"""
{summary_content}

---
**Artifacts:**
{generate_artifact_links(feature_id)}

**Workflow Evidence:**
- RED State: Validated
- GREEN State: Achieved
- Reviews: Completed (arch + code)
"""
    
    # Call Bitbucket API (requires BITBUCKET_TOKEN env var)
    # Implementation deferred to S3.5-002
    
    return {
        'pr_url': f'https://bitbucket.org/team/repo/pull-requests/123',
        'pr_id': 123,
        'source_branch': source_branch,
        'target_branch': 'main'
    }
```

**Files Changed:**
- `commands/execute.py`: Add `create_pull_request()` after step 10 success
- `commands/commit.py`: Remove any PR creation logic (focus on git commit only)
- `docs/plans/TASK-LIST-Multi-Agent-TDD.md`: Move PR creation from S6-005 → S3.5-002
- `docs/plans/PRD-Multi-Agent-TDD-Workflow.md`: Clarify PR creation is orchestrator responsibility

**Note:** Bitbucket API integration uses:
- REST API: `POST /repositories/{workspace}/{repo_slug}/pullrequests`
- Auth: `BITBUCKET_TOKEN` environment variable
- SDK: `pip install atlassian-python-api` (supports Bitbucket Cloud + Server)

---

### P1-3: Gate Mode Parameter (Simplified)

**Gap:** PRD lines 186-190 mention `--gate-mode=[strict|standard|relaxed]`  
**User Clarification:** Human gates retrieve feedback, don't enforce

**Fix:**
Simplify to boolean flag: `--skip-human-feedback` (default: false)

```python
# In all commands (test.py, implement.py, review.py, commit.py)

def request_human_feedback(stage: str, context: dict, skip: bool = False) -> Optional[str]:
    """
    Request human feedback at workflow stage.
    Returns feedback string or None if skipped.
    """
    if skip:
        return None
    
    print(f"\n{'='*60}")
    print(f"HUMAN FEEDBACK REQUESTED: {stage}")
    print(f"{'='*60}")
    for key, value in context.items():
        print(f"{key}: {value}")
    print("\nProvide feedback (or press Enter to continue): ", end='')
    
    feedback = input().strip()
    return feedback if feedback else None

# Example usage in test.py:
feedback = request_human_feedback(
    stage="Test Design Review",
    context={
        'feature_id': feature_id,
        'test_count': len(evidence.results),
        'red_state': 'VALID' if valid_red else 'INVALID'
    },
    skip=args.skip_human_feedback
)

if feedback:
    # Append feedback to test design artifact
    with open(test_design_path, 'a', encoding='utf-8') as f:
        f.write(f"\n\n## Human Feedback\n{feedback}\n")
```

**Files Changed:**
- `lib/human_feedback.py`: New module with `request_human_feedback()`
- `commands/test.py`: Add feedback request before artifact generation
- `commands/implement.py`: Add feedback request after GREEN state
- `commands/review.py`: Add feedback request after parallel reviews
- `commands/commit.py`: Add feedback request before git commit
- `harness-tdd-config.yml.template`: Add `workflow.skip_human_feedback: false`

**Note:** Constitutional gates (file gate, test immutability) are NEVER skipped. Only human feedback retrieval is optional.

---

## Priority 2: Template and Documentation

### P2-1: Artifact Directory Pattern Reconciliation

**Gap:** Multiple patterns for artifact storage across documents

**Fix:**
Standardize on single pattern:

```yaml
# In harness-tdd-config.yml.template

artifacts:
  root: "docs/features"      # All workflow artifacts here
  naming: "{feature_id}-{artifact_type}.md"
  
  types:
    spec: "spec"                          # feat-123-spec.md
    test_design: "test-design"            # feat-123-test-design.md
    impl_notes: "impl-notes"              # feat-123-impl-notes.md (optional)
    arch_review: "arch-review"            # feat-123-arch-review.md
    code_review: "code-review"            # feat-123-code-review.md
    workflow_summary: "workflow-summary"  # feat-123-workflow-summary.md

# Alternative locations (searched in order):
search_paths:
  - "docs/features"
  - "docs/specs"
  - ".specify/specs"
```

**Files Changed:**
- `harness-tdd-config.yml.template`: Add artifacts section
- `lib/artifact_paths.py`: New module with path resolution logic
- All commands: Use `artifact_paths.resolve(feature_id, artifact_type)` instead of hardcoded paths

---

### P2-2: Evidence Validation Schema

**Gap:** No formal schema for evidence requirements in Slice 6

**Fix:**
```python
# In lib/evidence_validator.py

from dataclasses import dataclass
from typing import Optional

@dataclass
class EvidenceRequirements:
    """Constitutional evidence requirements (CONSTITUTION lines 120-144)"""
    
    # Test Evidence (Step 7)
    test_design_artifact: bool = True      # Mandatory
    red_state_proof: bool = True           # pytest output showing failures
    failure_codes: list[str] = None        # MISSING_BEHAVIOR or ASSERTION_MISMATCH
    
    # Implementation Evidence (Step 8)
    impl_notes_artifact: bool = False      # Optional per CONSTITUTION line 125
    red_validation: bool = True            # Tests failed before implementation
    green_proof: bool = True               # pytest output showing all pass
    integration_evidence: bool = True      # Integration test results (pass or fail)
    
    # Review Evidence (Step 9)
    arch_review_artifact: bool = True      # Mandatory
    code_review_artifact: bool = True      # Mandatory
    conflict_resolution: bool = True       # If conflicts occurred
    review_cycles: Optional[int] = None    # Max 3
    
    # Commit Evidence (Step 10)
    workflow_summary: bool = True          # Mandatory
    git_commit_sha: bool = True            # Commit created
    all_artifacts_linked: bool = True      # All paths validated

def validate_evidence(feature_id: str, config: dict) -> tuple[bool, list[str]]:
    """
    Validate all constitutional evidence requirements met.
    Returns (valid, missing_items)
    """
    missing = []
    
    # Check Step 7 evidence
    test_design_path = artifact_paths.resolve(feature_id, 'test_design')
    if not test_design_path.exists():
        missing.append("Test design artifact (mandatory)")
    else:
        # Validate RED state proof in artifact
        content = test_design_path.read_text(encoding='utf-8')
        if 'RED State Validation' not in content:
            missing.append("RED state evidence in test design")
        if 'MISSING_BEHAVIOR' not in content and 'ASSERTION_MISMATCH' not in content:
            missing.append("Valid failure codes in test design")
    
    # Check Step 8 evidence
    # ... (similar validation for implementation, review, commit)
    
    return len(missing) == 0, missing
```

**Files Changed:**
- `lib/evidence_validator.py`: New module with validation logic
- `commands/commit.py`: Call `validate_evidence()` before commit
- `tests/test_evidence_validator.py`: Comprehensive tests for all evidence types

---

## Summary of Changes by Slice

### Slice 3 (Complete - Minor Fixes)
- **P0-2**: Remove bypass flag from docs (already correct in code)
- **P2-1**: Update to use `artifact_paths.resolve()`

### Slice 4 (Not Yet Implemented - Design Changes)
- **P0-1**: Add test immutability rejection in S4-002
- **P0-3**: Change integration test handling in S4-005 (evidence, not blocker)
- **P1-3**: Add human feedback request in S4-002
- **P2-1**: Use standardized artifact paths

### Slice 5 (Not Yet Implemented - Design Changes)
- **P1-3**: Add human feedback request in S5-003
- **P2-1**: Use standardized artifact paths

### Slice 6 (Not Yet Implemented - Design Changes)
- **P1-1**: Add local Jira structure creation in S6-002
- **P1-2**: Remove PR creation (moved to orchestrator)
- **P1-3**: Add human feedback request in S6-002
- **P2-2**: Add evidence validation in S6-003
- **P2-1**: Use standardized artifact paths

### Slice 3.5 (Not Yet Implemented - New Slice)
- **P1-2**: Add PR creation to S3.5-002 (after successful workflow)
- Implement execute.py orchestrator per PHASE2-UPDATED-Execute-Command.md

---

## Implementation Order

**Immediate (Before Continuing):**
1. Fix P0-2 in TASK-LIST (doc change only)
2. Create `lib/artifact_paths.py` (used by all commands)
3. Create `lib/jira_local.py` (used by commit command)
4. Create `lib/human_feedback.py` (used by all commands)
5. Create `lib/evidence_validator.py` (used by commit command)
6. Update `harness-tdd-config.yml.template` with new sections

**During Slice 4 Implementation:**
1. Implement P0-1 (test immutability rejection)
2. Implement P0-3 (integration test evidence)
3. Implement P1-3 (human feedback)

**During Slice 6 Implementation:**
1. Implement P1-1 (local Jira structure)
2. Implement P2-2 (evidence validation)

**During Slice 3.5 Implementation:**
1. Implement P1-2 (PR creation via Bitbucket API)

---

## Testing Strategy

All fixes require tests:

**Unit Tests:**
- `tests/test_artifact_paths.py` (path resolution)
- `tests/test_jira_local.py` (epic/story creation)
- `tests/test_human_feedback.py` (input capture)
- `tests/test_evidence_validator.py` (all evidence types)

**Integration Tests:**
- `tests/integration/test_test_immutability.sh` (P0-1: reject test modifications)
- `tests/integration/test_integration_evidence.sh` (P0-3: failures don't block)
- `tests/integration/test_jira_structure.sh` (P1-1: epic/story files created)

**Verification:**
- All tests pass before marking slice complete
- Manual verification of human feedback prompts (if not skipped)
- Manual verification of Bitbucket PR creation (requires token)

---

## Related Documents Updated

- [TASK-LIST-Multi-Agent-TDD.md](TASK-LIST-Multi-Agent-TDD.md) — Acceptance criteria corrections
- [PRD-Multi-Agent-TDD-Workflow.md](PRD-Multi-Agent-TDD-Workflow.md) — PR creation clarification
- [CONSTITUTION-Multi-Agent-TDD.md](CONSTITUTION-Multi-Agent-TDD.md) — No changes (already correct)
- [PHASE2-UPDATED-Execute-Command.md](PHASE2-UPDATED-Execute-Command.md) — Restored from git, PR creation added

---

## Questions for User

None - all clarifications provided. Ready to proceed with implementation.
