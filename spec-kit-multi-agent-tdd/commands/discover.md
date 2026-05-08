---
description: "Discovery phase: generate PRD and System Constitution via grill-me relentless questioning"
skills:
  - 'general-grill-with-docs'
tools:
  - 'filesystem/read'
  - 'filesystem/write'
templates:
  prd: templates/prd-template.md
  constitution: templates/system-constitution-template.md
exit_codes:
  0: "Success - PRD and/or System Constitution created or updated"
  1: "Validation failure - feature_id not provided"
  2: "Escalation required - template missing or write error"
---

# Discovery Workflow (Multi-Agent TDD — PRD & System Constitution)

This command runs a grill-me session to elicit requirements and produce a PRD and System Constitution for the given feature.

## Prerequisites

- `feature_id` provided by user
- Templates available at `templates/prd-template.md` and `templates/system-constitution-template.md`

## User Input

`/speckit.multi-agent.discover $ARGUMENTS`

**Arguments**:
- `$ARGUMENTS`: Feature identifier (e.g., `feat-123`). Required.

## Step 1: Load Configuration

Load from `.specify/harness-tdd-config.yml` or use defaults:

| Key | Default | Purpose |
|-----|---------|---------|
| `artifacts.root` | `docs/features` | Root directory for feature artifacts |
| `workflow.agent_timeout` | `30` | Agent task timeout in minutes (default: 30 if key missing) |
| `planning.skill` | `grill-me` | Skill used for discovery questioning |

If config file is missing or unreadable, continue with the defaults above. Log a warning to stderr but do not abort.

## Step 2: Validate Inputs

- If `$ARGUMENTS` is empty or not provided → ❌ Exit 1 with message: "Error: feature_id is required. Usage: /speckit.multi-agent.discover <feature_id>"
- Set `feature_id` from `$ARGUMENTS` (trim whitespace)
- Confirm `feature_id` is a non-empty string before continuing

## Step 3: Check Existing Artifacts

**Check for existing PRD:**

Search for: `{artifacts.root}/{feature_id}-prd.md`

- If found: mention it to the user — "PRD already exists at `{prd_path}`, will merge updates" — then proceed
- If not found: continue (will create from template in Step 6)

**Check for existing System Constitution:**

Search in order:
1. `docs/architecture/technical-constitution.md`
2. `.specify/technical-constitution.md`

- If found: load it silently for merging (no warning to user)
- If not found: continue (will create from template in Step 7)

## Step 4: Load Context

Load the following for reference during the grill-me session:

1. **Spec artifact** (if exists) — search in order:
   - `docs/features/{feature_id}.md`
   - `docs/features/{feature_id}-spec.md`
   - `.specify/specs/{feature_id}.md`
2. **Existing PRD** (if found in Step 3) — load for merge context
3. **Existing System Constitution** (if found in Step 3) — load for merge context

If none of these exist, proceed with an empty context — the grill-me session will surface everything from scratch.

## Step 5: Run Grill-Me Session (general-grill-with-docs skill)

Use the `general-grill-with-docs` skill throughout this step.

**Goal:** Reach consensus on all PRD sections through relentless questioning.

**Approach:**
- Ask questions **one at a time**, waiting for user response before continuing
- Reference loaded spec/PRD/constitution context in your questions
- Track unanswered/deferred questions separately from answered ones
- Continue until you reach consensus with the user OR user signals done (e.g., "that's enough")
- Allow user to defer unknowns — note them as open questions, do not block on them

**Questions must cover all PRD sections:**

- **What & Why** — What is the feature? What problem does it solve?
- **Business Value** — What measurable outcomes are expected?
- **Measurability** — How will success be measured?
- **Goals & No-Goals** — What is in scope? What is explicitly out of scope?
- **Risks & Stories** — What are the key risks? Which user stories are in scope?
- **Dependencies** — What external systems, teams, or services does this depend on?
- **People** — Who are the stakeholders? Who owns the feature?
- **Metrics** — What KPIs, SLAs, or NFR targets apply?

**Also extract for System Constitution** (if answers reveal tech constraints or NFRs):

- Tech choices (languages, frameworks, platforms)
- Team skills and maturity levels
- Compliance requirements (GDPR, SOC2, etc.)
- Non-functional requirement (NFR) constraints (latency, availability, throughput)

## Step 6: Generate/Update PRD

- Fill `templates/prd-template.md` with answers gathered in the grill-me session
- If existing PRD found (Step 3): merge new information into it — do not overwrite sections that are already complete unless the user provided updates in this session
- Save to: `{artifacts.root}/{feature_id}-prd.md`
- If save fails: ❌ Exit 2 with message: "Error: failed to write PRD to `{prd_path}`"
- If `prd-template.md` is missing: ❌ Exit 2 with message: "Error: template not found at `templates/prd-template.md`"

## Step 7: Generate/Update System Constitution

- Extract tech constraints and NFR information gathered in Step 5
- If constitution exists (Step 3): merge new findings into the existing file silently
- If no constitution exists: create from `templates/system-constitution-template.md`
- Save to: `docs/architecture/technical-constitution.md` (or the existing path found in Step 3)
- If save fails: ❌ Exit 2 with message: "Error: failed to write System Constitution"
- If `system-constitution-template.md` is missing and no existing constitution: ❌ Exit 2

## Step 8: Save Open Questions

- If any questions were deferred by user during the grill-me session:
  - Save them to: `{artifacts.root}/{feature_id}-open-questions.md`
  - Format: a simple list with each unanswered question and the context in which it arose
- If no open questions exist: skip this step entirely — do not create an empty file

## Step 9: Validate Artifacts (post-generation)

Run validation after all artifacts are written. This is a **post-generation** check only — warn on issues, do not block the workflow.

```bash
python3 scripts/validate_artifact_structure.py {prd_path} {constitution_path}
```

- If the script exits 0: all good, continue to Step 10
- If the script finds issues: warn the user and escalate to human with diagnostics (do not fail silently)
- Exit code 2 from the validator means escalate: present the diagnostics to the user

## Step 10: Report

Show a final summary:

```
✓ PRD created/updated at: {prd_path}
✓ System Constitution created/updated at: {constitution_path}
⚠ Open questions saved at: {artifacts.root}/{feature_id}-open-questions.md  (only if any)
```

Suggest next step:

> Run `/speckit.multi-agent.solution-design {feature_id}` to create an architecture design.

## Exit Codes

- **0**: Success — PRD and/or System Constitution created or updated
- **1**: Validation failure — feature_id not provided (`$ARGUMENTS` empty)
- **2**: Escalation required — template missing or write error

## Configuration Reference

`.specify/harness-tdd-config.yml` keys used by this command:

```yaml
artifacts:
  root: docs/features          # Root dir for PRD and open-questions output

workflow:
  agent_timeout: 30            # Grill-me session timeout in minutes (default: 30)

planning:
  skill: grill-me              # Skill used for discovery
```

## Related Commands

- `/speckit.multi-agent.solution-design`: Create architecture design (next step after discovery)
- `/speckit.multi-agent.test`: Generate failing tests for a specified feature
- `/speckit.multi-agent.implement`: Implement feature code (RED → GREEN)
