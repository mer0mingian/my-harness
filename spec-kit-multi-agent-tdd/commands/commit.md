---
description: "Validate evidence artifacts and create workflow summary before git commit using SpecKit"
tools:
  - 'bash/execute'
requires:
  - speckit
exit_codes:
  0: "Success - workflow summary created, ready for commit"
  1: "Validation failure - missing required artifacts from previous steps"
  2: "Escalation required - template error or SpecKit failure"
---

# Commit Workflow (Multi-Agent TDD Phase 6)

This command validates all evidence artifacts from the Multi-Agent TDD workflow and generates a workflow summary artifact before git commit.

## Prerequisites

- All workflow steps completed (Test Design, Implementation Notes, Architecture Review, Code Review)
- SpecKit CLI installed and configured
- Configuration file at `.specify/harness-tdd-config.yml` (optional, uses defaults)

## User Input

**Command**: `/speckit.matd.commit $FEATURE_ID [--project-root PATH]`

**Arguments**:
- `$FEATURE_ID`: Feature identifier (e.g., 'feat-123')
- `--project-root`: (Optional) Project root directory (default: current directory)

## Step 1: Load Configuration

SpecKit loads configuration from `.specify/harness-tdd-config.yml` or uses defaults.

**Key configuration**:
- `artifacts.root`: Base directory for artifacts (default: `docs/features`)
- `workflow.agent_timeout`: Task timeout in minutes (default: 30)
- Artifact paths: `{artifacts.root}/{feature_id}-{artifact_type}.md`

## Step 2: Validate Required Artifacts

Validate all required artifacts using SpecKit:

**SpecKit validation command**:
```bash
specify artifact list --feature-id "$feature_id" --required --quiet
```

**Required artifacts** (validated by SpecKit):
1. **Test Design** (Step 7): `{feature_id}-test-design.md`
2. **Implementation Notes** (Step 8): `{feature_id}-impl-notes.md`
3. **Architecture Review** (Step 9): `{feature_id}-arch-review.md`
4. **Code Review** (Step 9): `{feature_id}-code-review.md`

**On failure**: SpecKit returns non-zero exit code → ❌ Exit 1 with error

**Example failure output**:
```
✗ Validation failure: Missing required artifacts for feature: feat-123

Run this command to see which artifacts are missing:
  specify artifact list --feature-id feat-123 --required
```

## Step 3: Generate Workflow Summary

Create workflow summary artifact using SpecKit template rendering. Complete this step within ${agent_timeout} minutes (default: 30). If the summary cannot be generated within the time limit, output partial results with what has been completed, then escalate to human with the list of remaining artifacts to include.

**SpecKit render command**:
```bash
specify artifact render workflow-summary \
  --feature-id "$feature_id" \
  --template workflow-summary-template.md \
  --output "docs/features/${feature_id}-summary.md"
```

**Output path**: `{artifacts.root}/{feature_id}-workflow-summary.md`

**Template location** (SpecKit resolves in order):
1. Custom: `.specify/templates/workflow-summary-template.md`
2. Built-in: SpecKit default template

**Template variables** (auto-populated by SpecKit):
- `feature_id`: Feature identifier
- `feature_name`: Extracted from spec or defaults to feature_id
- `timestamp`: ISO 8601 UTC timestamp
- `status`: "draft"
- `test_design_path`: Path to test design artifact
- `impl_notes_path`: Path to implementation notes artifact
- `arch_review_path`: Path to architecture review artifact
- `code_review_path`: Path to code review artifact

**On template not found or render failure**: ❌ Exit 2 with escalation

**Example failure output**:
```
✗ ERROR: Failed to generate workflow summary

Check that the template exists and is valid:
  .specify/templates/workflow-summary-template.md
```

## Step 4: Display Success Message

Print confirmation with artifact paths and next steps.

**Success output example**:
```
✓ Success!
  Workflow Summary: /path/to/docs/features/feat-123-workflow-summary.md

Artifacts validated:
  - Test Design: /path/to/docs/features/feat-123-test-design.md
  - Implementation Notes: /path/to/docs/features/feat-123-impl-notes.md
  - Architecture Review: /path/to/docs/features/feat-123-arch-review.md
  - Code Review: /path/to/docs/features/feat-123-code-review.md

Next steps:
  1. Review workflow summary: /path/to/docs/features/feat-123-workflow-summary.md
  2. Run git commit with appropriate message
  3. Create pull request for review
```

## Step 5: Git Commit (Manual Step)

After workflow summary generated, create git commit manually:

**Stage artifacts**:
```bash
git add docs/features/${FEATURE_ID}-*.md src/ tests/
```

**Commit message format**:
```bash
git commit -m "feat(${FEATURE_ID}): implement feature with TDD workflow

- Test design: ${TEST_COUNT} tests
- Implementation: GREEN state achieved
- Reviews: Arch + Code approved
- Evidence: RED→GREEN validated

Workflow summary: docs/features/${FEATURE_ID}-workflow-summary.md

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

**Next steps after commit**:
1. Review workflow summary
2. Create pull request
3. Link to workflow summary in PR description

**Note on documentation updates**:
C4 diagrams and Code Graph Context (CGC) index updates are automated via GitHub Actions on PR merge to main/live branches. See `.github/workflows/auto-docs.yml` for automated documentation pipeline. Manual execution of `deepwiki generate` or `cgc index` is not required.

## Exit Codes

- **0**: Success
  - All required artifacts found
  - Workflow summary generated
  - Ready for git commit
- **1**: Validation failure
  - Missing one or more required artifacts
  - Cannot proceed without completing previous steps
- **2**: Escalation required
  - Template not found or inaccessible
  - Permission error writing workflow summary
  - System error (jinja2 not installed, etc.)

## Output Examples

**Success**:
```
✓ Success!
  Workflow Summary: docs/features/feat-123-workflow-summary.md

Next steps: Review summary, git commit, create PR
```

**Validation Failure**:
```
✗ Missing required artifacts for feature: feat-123
Run: specify artifact list --feature-id feat-123 --required
```

**Template Error**:
```
✗ Failed to generate workflow summary
Check template: .specify/templates/workflow-summary-template.md
```

## Configuration Reference

See `.specify/harness-tdd-config.yml` for artifact paths and workflow settings. SpecKit manages artifact type resolution automatically.

## Related Commands

- `/speckit.matd.test`: Generate failing tests (RED state)
- `/speckit.matd.implement`: Implement feature to GREEN state
- `/speckit.matd.review`: Review architecture and code
- `/speckit.matd.validate`: Validate full feature lifecycle

## Implementation Notes

**Current behavior**:
- Uses SpecKit queries for artifact validation (no custom loops)
- Uses SpecKit template rendering for workflow summary generation
- Provides git commit guidance
- Manual commit step required
- Documentation updates automated via GitHub Actions (not manual hooks)

**SpecKit integration**:
- `specify artifact list --required`: Validates all required artifacts exist
- `specify artifact render`: Generates workflow summary from template
- No custom validation loops or manual template rendering
- No post-commit hooks (deepwiki, cgc) — handled by CI/CD

**Future enhancements**:
- Automatic git commit option
- PR creation automation
- Spec lifecycle update (Planned → Implemented)
