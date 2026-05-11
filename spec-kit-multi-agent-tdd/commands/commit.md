---
description: "Validate evidence artifacts and create workflow summary before git commit"
tools:
  - 'filesystem/read'
  - 'filesystem/write'
  - 'bash/execute'
scripts:
  load_config: lib/config.py
  find_artifact: lib/artifacts.py
  generate_summary: lib/templates.py
exit_codes:
  0: "Success - workflow summary created, ready for commit"
  1: "Validation failure - missing required artifacts from previous steps"
  2: "Escalation required - missing template or permission error"
---

# Commit Workflow (Multi-Agent TDD Phase 6)

This command validates all evidence artifacts from the Multi-Agent TDD workflow and generates a workflow summary artifact before git commit.

## Prerequisites

- All workflow steps completed:
  - Test Design artifact (Step 7)
  - Implementation Notes artifact (Step 8)
  - Architecture Review artifact (Step 9)
  - Code Review artifact (Step 9)
- Configuration file at `.specify/harness-tdd-config.yml` (optional, uses defaults if missing)
- Jinja2 template engine installed

## User Input

**Command**: `/speckit.matd.commit $FEATURE_ID [--project-root PATH]`

**Arguments**:
- `$FEATURE_ID`: Feature identifier (e.g., 'feat-123')
- `--project-root`: (Optional) Project root directory (default: current directory)

## Step 1: Load Configuration

Load harness configuration from `.specify/harness-tdd-config.yml` or use defaults:

**Default configuration**:
```yaml
version: '1.0'
artifacts:
  root: 'docs/features'
  types:
    spec: 'spec'
    test_design: 'test-design'
    impl_notes: 'impl-notes'
    arch_review: 'arch-review'
    code_review: 'code-review'
    workflow_summary: 'workflow-summary'
```

**Config keys loaded**:
- `workflow.agent_timeout` — agent task timeout in minutes (default: 30 if key missing)
- `jira.auto_create_stories` — when `true` and `jira.local_mode: true`, call `auto_create_story_structure` for the feature before validation (default: false); when `false`, skip silently
- `jira.local_mode` — enable local Jira structure management (default: false)

**Auto-create story structure** (when `jira.auto_create_stories: true` and `jira.local_mode: true`):
- Call `auto_create_story_structure(feature_id, epic_id, story_id)` from `lib/jira_local.py`
- `epic_id` and `story_id` are read from config keys `jira.epic_id` and `jira.story_id`
- If file already exists, no error is raised (idempotent)
- If `jira.auto_create_stories: false`, this step is skipped silently

**Artifact paths constructed as**:
- Pattern: `{artifacts.root}/{feature_id}-{artifact_type}.md`
- Example: `docs/features/feat-123-test-design.md`

## Step 2: Find Required Artifacts

Locate all required artifacts for validation:

**Required artifacts**:
1. **Test Design** (Step 7): `{feature_id}-test-design.md`
2. **Implementation Notes** (Step 8): `{feature_id}-impl-notes.md`
3. **Architecture Review** (Step 9): `{feature_id}-arch-review.md`
4. **Code Review** (Step 9): `{feature_id}-code-review.md`

**Validation**:
- Each artifact path constructed from config
- Check file exists at expected location
- Collect missing artifacts

**On failure**: List all missing artifacts → ❌ Exit 1 with error

**Example failure output**:
```
✗ Validation failure: Missing required artifacts
  - Test Design (Step 7)
  - Code Review (Step 9)

Run previous workflow steps to create missing artifacts.
```

## Step 3: Generate Workflow Summary

Create workflow summary artifact from template. Complete this step within ${agent_timeout} minutes (default: 30). If the summary cannot be generated within the time limit, output partial results with what has been completed, then escalate to human with the list of remaining artifacts to include.

**Output path**: `{artifacts.root}/{feature_id}-workflow-summary.md`

**Template location** (checked in order):
1. Custom: `.specify/templates/workflow-summary-template.md`
2. Built-in: `templates/workflow-summary-template.md`

**Template variables**:
- `feature_id`: Feature identifier
- `feature_name`: Extracted from spec or defaults to feature_id
- `timestamp`: ISO 8601 UTC timestamp
- `status`: "draft"
- `test_design_path`: Path to test design artifact
- `impl_notes_path`: Path to implementation notes artifact
- `arch_review_path`: Path to architecture review artifact
- `code_review_path`: Path to code review artifact

**Template engine**: Jinja2 with StrictUndefined

**On template not found**: ❌ Exit 2 with escalation

**Example escalation output**:
```
✗ Escalation required: Template directory not found: /path/to/templates

The workflow summary template is missing or cannot be accessed.
Template should be at: /path/to/.specify/templates/workflow-summary-template.md
```

## Step 4: Write Workflow Summary

Write rendered template to output path:

**Actions**:
1. Create parent directory if needed (mkdir -p)
2. Write content with UTF-8 encoding
3. Verify file created successfully

**On permission error**: ❌ Exit 2 with escalation

## Step 5: Display Success Message

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

## Git Commit (Manual Step)

After workflow summary generated, create git commit manually:

**Stage artifacts**:
```bash
git add docs/features/${FEATURE_ID}-*.md
```

**Commit message format**:
```bash
git commit -m "feat(${FEATURE_ID}): implement feature with TDD workflow

- Test design: ${TEST_COUNT} tests
- Implementation: GREEN state achieved
- Reviews: Arch + Code approved
- Evidence: RED→GREEN validated

Workflow summary: docs/features/${FEATURE_ID}-workflow-summary.md"
```

**Next steps after commit**:
1. Review workflow summary
2. Create pull request
3. Link to workflow summary in PR description

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

### Success (all artifacts validated)

```
✓ Success!
  Workflow Summary: /path/to/docs/features/feat-auth-login-workflow-summary.md

Artifacts validated:
  - Test Design: /path/to/docs/features/feat-auth-login-test-design.md
  - Implementation Notes: /path/to/docs/features/feat-auth-login-impl-notes.md
  - Architecture Review: /path/to/docs/features/feat-auth-login-arch-review.md
  - Code Review: /path/to/docs/features/feat-auth-login-code-review.md

Next steps:
  1. Review workflow summary: /path/to/docs/features/feat-auth-login-workflow-summary.md
  2. Run git commit with appropriate message
  3. Create pull request for review
```

### Validation Failure (missing artifacts)

```
✗ Validation failure: Missing required artifacts
  - Implementation Notes (Step 8)
  - Code Review (Step 9)

Run previous workflow steps to create missing artifacts.
```

### Escalation Required (missing template)

```
✗ Escalation required: Template directory not found: /path/to/spec-kit-multi-agent-tdd/templates

The workflow summary template is missing or cannot be accessed.
Template should be at: /path/to/.specify/templates/workflow-summary-template.md
```

## Configuration Reference

`.specify/harness-tdd-config.yml`:

```yaml
version: '1.0'
artifacts:
  root: 'docs/features'
  types:
    spec: 'spec'
    test_design: 'test-design'
    impl_notes: 'impl-notes'
    arch_review: 'arch-review'
    code_review: 'code-review'
    workflow_summary: 'workflow-summary'
```

**Configuration options**:
- `artifacts.root`: Base directory for all artifacts
- `artifacts.types.*`: Suffix for each artifact type
- Paths constructed as: `{root}/{feature_id}-{type}.md`

## Related Commands

- `/speckit.matd.test`: Generate failing tests (RED state)
- `/speckit.matd.implement`: Implement feature to GREEN state
- `/speckit.matd.review`: Review architecture and code
- `/speckit.matd.validate`: Validate full feature lifecycle

## Implementation Notes

**Current behavior**:
- Validates all required artifacts exist
- Generates workflow summary from template
- Provides git commit guidance
- Manual commit step required

**Template requirements**:
- Jinja2 template engine
- Template variables documented in Step 3
- StrictUndefined mode (fails on missing variables)

**Future enhancements**:
- Automatic git commit option
- PR creation automation
- Integration with CI/CD pipelines
- Spec lifecycle update (Planned → Implemented)
