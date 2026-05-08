---
description: "Parallel architecture + code review (dual reviewers)"
agents:
  - check  # Architecture reviewer
  - simplify  # Code reviewer
tools:
  - 'filesystem/read'
  - 'filesystem/write'
templates:
  arch_review: templates/arch-review-template.md
  code_review: templates/code-review-template.md
exit_codes:
  0: "Success - review artifacts created"
  1: "Validation failure - implementation notes not found"
  2: "Escalation required - templates missing or permission errors"
---

# Review Workflow (Multi-Agent TDD Phase 5, Step 9)

This command spawns @check (architecture reviewer) and @simplify (code reviewer) agents in parallel to review implementation. Creates arch-review and code-review artifacts with conflict resolution (safety wins).

## Prerequisites

- Implementation complete (GREEN state from step 8)
- Implementation notes artifact exists
- Review templates available (arch-review-template.md, code-review-template.md)
- Configuration file at `.specify/harness-tdd-config.yml` (optional, uses defaults if missing)

## User Input

**Command**: `/speckit.multi-agent.review $FEATURE_ID`

**Arguments**:
- `$FEATURE_ID`: Feature identifier (e.g., 'feat-123')
- `--project-root`: (Optional) Project root directory (defaults to current directory)

## Step 1: Load Configuration

Load harness configuration from `.specify/harness-tdd-config.yml` or use defaults:

**Default configuration includes**:
- Agent names (check for architecture, simplify for code quality)
- Review settings (parallel_review: true, max_cycles: 3)
- Workflow dispatch: `parallel_enabled` (default: false when key missing from config)
- Artifact paths and templates
- Conflict resolution rules (safety wins)

**Config key loaded**:
- `workflow.parallel_enabled` — controls whether agents dispatch in parallel or sequentially (default: `false`)

## Step 2: Find Implementation Notes

Search for implementation notes artifact from step 8 in order of precedence:
1. `docs/features/${FEATURE_ID}-impl-notes.md`
2. `docs/features/${FEATURE_ID}-implementation-notes.md`
3. `.specify/features/${FEATURE_ID}-impl-notes.md`

**If not found**: ❌ Exit 1 with error listing checked locations

**On success**: Read implementation notes for next steps

## Step 3: Find Spec Artifact (Optional)

Search for spec in order of precedence:
1. `docs/features/${FEATURE_ID}.md`
2. `docs/features/${FEATURE_ID}-spec.md`
3. `docs/specs/${FEATURE_ID}-spec.md`
4. `.specify/specs/${FEATURE_ID}.md`

**If not found**: Continue without spec (not required for review)

## Step 4: Extract Feature Name

Extract feature name from implementation notes:
- Look for first H1 heading (`# Feature Name`)
- If not found, convert feature_id to readable name (feat-123 → Feat 123)

## Step 5: Generate Review Artifacts

Create architecture and code review artifacts from templates:

**Template locations**:
- Custom: `.specify/templates/arch-review-template.md`, `code-review-template.md`
- Built-in: `templates/arch-review-template.md`, `code-review-template.md`

**Template variables**:
- `feature_id`: Feature identifier
- `feature_name`: Extracted from implementation notes
- `timestamp`: ISO 8601 UTC timestamp
- `status`: draft (initial state)
- `cycle_number`: 1 (initial review cycle)
- `max_cycles`: 3 (from config)

**Output paths** (from config, defaults shown):
- Architecture review: `docs/features/${FEATURE_ID}-arch-review.md`
- Code review: `docs/features/${FEATURE_ID}-code-review.md`

**On template not found**: ❌ Exit 2 with escalation message

**On permission error**: ❌ Exit 2 with escalation message

## Step 6: Prepare Review Context

Collect review context for both agents:

**Context includes**:
- Feature ID and name
- Implementation notes content
- Spec content (if found in step 3)
- Files changed (implementation files)
- Test files created
- Diff from main branch (git diff)

**Note**: Context preparation described for future automation. Current MVP creates artifacts with templates only.

## Step 7: Invoke Parallel Reviewers

**NOTE**: Execution mode is controlled by `workflow.parallel_enabled` from `.specify/harness-tdd-config.yml`. Default is `false` (sequential) when the key is missing.

**@check agent (architecture review)**:
- Context: implementation files, notes, spec, diff
- Task: Architecture review against safety constraints
- Focus: Design patterns, dependencies, security, scalability
- Verdict: APPROVED | NEEDS_REVISION | BLOCKED

**@simplify agent (code quality review)**:
- Context: implementation files, notes, spec, diff
- Task: Code quality review
- Focus: Complexity, duplication, readability, maintainability
- Verdict: APPROVED | NEEDS_REVISION | BLOCKED

**Conditional dispatch** (based on `workflow.parallel_enabled`):

- **If `parallel_enabled: true`**: Invoke @check and @simplify simultaneously (parallel execution). Wait for both agents to complete before proceeding to Step 8. Both agents receive the same review context.

- **If `parallel_enabled: false`**: Run @check first (architecture review). Wait for @check to complete and record its verdict. Then run @simplify sequentially (code quality review). Wait for @simplify to complete before proceeding to Step 8.

## Step 8: Collect Review Verdicts

Wait for both reviewers to complete (future automation):

**Possible verdicts per agent**:
- `APPROVED`: No issues found, proceed to commit
- `NEEDS_REVISION`: Issues found, fix and re-review
- `BLOCKED`: Critical issues (safety/security), escalate to human

**Conflict resolution rules**:
1. If either agent returns `BLOCKED` → Overall verdict is `BLOCKED`
2. If one returns `NEEDS_REVISION`, other `APPROVED` → Overall verdict is `NEEDS_REVISION`
3. If both return `APPROVED` → Overall verdict is `APPROVED`

**Priority**: Safety wins (BLOCKED > NEEDS_REVISION > APPROVED)

## Step 9: Handle Review Cycles

If overall verdict is `NEEDS_REVISION`:

**Review cycle management**:
- Max cycles: 3 (configurable in harness-tdd-config.yml)
- Track current cycle in artifacts
- On each cycle:
  1. Developer fixes issues
  2. Re-invoke /speckit.multi-agent.review
  3. Increment cycle_number in artifacts
  4. Repeat until APPROVED or BLOCKED

**If max cycles exceeded**:
- Overall verdict becomes `BLOCKED`
- Escalate to human for review
- ❌ Exit 2 with escalation details

## Step 10: Update Review Artifacts

Update artifacts with review results:

**Architecture review artifact** (`${FEATURE_ID}-arch-review.md`):
- Verdict (APPROVED, NEEDS_REVISION, BLOCKED)
- Architecture findings
- Safety/security issues (if any)
- Recommendations
- Cycle number

**Code review artifact** (`${FEATURE_ID}-code-review.md`):
- Verdict (APPROVED, NEEDS_REVISION, BLOCKED)
- Code quality findings
- Complexity issues (if any)
- Refactoring suggestions
- Cycle number

## Exit Codes

- **0**: Success
  - Review artifacts created
  - Both agents completed (verdict: APPROVED or NEEDS_REVISION)
- **1**: Validation failure
  - Implementation notes not found
- **2**: Escalation required
  - Templates missing
  - Permission errors writing artifacts
  - BLOCKED verdict from either agent
  - Max review cycles exceeded

## Output Examples

### Success (artifacts created)

```
✓ Success!
  Arch Review: /path/to/docs/features/feat-123-arch-review.md
  Code Review: /path/to/docs/features/feat-123-code-review.md

Next steps:
  1. Invoke @check and @simplify agents in parallel
  2. Review their findings in the artifacts
  3. Resolve any conflicts (phase S5-004)
  4. Proceed to commit (phase S5-006)
```

### Validation Failure (implementation notes missing)

```
✗ Validation failure: Implementation notes not found for feature: feat-123
Checked locations:
  - docs/features/feat-123-impl-notes.md
  - docs/features/feat-123-implementation-notes.md
  - .specify/features/feat-123-impl-notes.md

✗ Validation failure: Check implementation notes exist
```

### Escalation Required (template missing)

```
✗ Escalation required: Architecture review template not found: templates/arch-review-template.md

✗ Escalation required: Check template files and permissions
```

## Configuration Reference

`.specify/harness-tdd-config.yml`:

```yaml
version: '1.0'
agents:
  arch_reviewer: check
  code_reviewer: simplify

artifacts:
  arch_review:
    path: 'docs/features/{feature_id}-arch-review.md'
    template: '.specify/templates/arch-review-template.md'
    mandatory: true
  code_review:
    path: 'docs/features/{feature_id}-code-review.md'
    template: '.specify/templates/code-review-template.md'
    mandatory: true

review:
  parallel_review: true
  max_cycles: 3
  conflict_resolution: 'safety_wins'  # BLOCKED > NEEDS_REVISION > APPROVED
```

## Conflict Resolution Examples

### Both agents approve
- @check: `APPROVED`
- @simplify: `APPROVED`
- **Overall**: `APPROVED` → Proceed to commit

### One needs revision
- @check: `APPROVED`
- @simplify: `NEEDS_REVISION` (found code complexity issues)
- **Overall**: `NEEDS_REVISION` → Fix and re-review

### Architecture blocked (safety wins)
- @check: `BLOCKED` (security vulnerability found)
- @simplify: `APPROVED`
- **Overall**: `BLOCKED` → Escalate to human

### Both need revision
- @check: `NEEDS_REVISION` (design concerns)
- @simplify: `NEEDS_REVISION` (quality issues)
- **Overall**: `NEEDS_REVISION` → Fix both and re-review

## Related Commands

- `/speckit.multi-agent.implement`: Generate implementation notes (step 8)
- `/speckit.multi-agent.commit`: Commit changes after review (step 10)
- `/speckit.multi-agent.validate`: Validate full feature lifecycle

## Implementation Notes

**Current (Phase 2-3)**:
- Artifact generation automated
- Template rendering via Jinja2
- Manual agent invocation required
- Conflict resolution described (not automated)

**Future (Phase 4+)**:
- Direct parallel agent spawning via Claude Code Agent API
- Automated verdict collection and conflict resolution
- Review cycle management automation
- Integration with git workflow

## Review Cycle Workflow

```
Cycle 1:
  /speckit.multi-agent.review feat-123
  → @check: NEEDS_REVISION
  → @simplify: APPROVED
  → Overall: NEEDS_REVISION
  → Developer fixes architecture issues

Cycle 2:
  /speckit.multi-agent.review feat-123
  → @check: APPROVED
  → @simplify: NEEDS_REVISION (new issues found)
  → Overall: NEEDS_REVISION
  → Developer fixes code quality issues

Cycle 3:
  /speckit.multi-agent.review feat-123
  → @check: APPROVED
  → @simplify: APPROVED
  → Overall: APPROVED
  → Proceed to commit
```

## Escalation Scenarios

### Max cycles exceeded
```
Cycle 1: NEEDS_REVISION
Cycle 2: NEEDS_REVISION
Cycle 3: NEEDS_REVISION
→ Max cycles (3) exceeded
→ Overall verdict: BLOCKED
→ Escalate to human
```

### Critical safety issue
```
Cycle 1:
  @check: BLOCKED (SQL injection vulnerability)
  @simplify: APPROVED
→ Overall verdict: BLOCKED
→ Escalate to human immediately
```
