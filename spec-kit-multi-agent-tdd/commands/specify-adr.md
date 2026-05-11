---
description: "Create Architecture Decision Record using grill-me interview"
agent: matd-architect
skills:
  - 'general-grill-me'
  - 'arch-mermaid-diagrams'
tools:
  - 'filesystem/read'
  - 'filesystem/write'
templates:
  adr: .speckit-templates/specs/adr-template.md
exit_codes:
  0: "Success - ADR created"
  1: "Validation failure - required inputs missing"
  2: "Escalation required - template missing or write error"
---

# ADR Creation Workflow (MATD — Architecture Decision Record)

This command runs a grill-me session to elicit architectural decision context and creates an Architecture Decision Record. Use this for documenting significant architectural choices.

## Prerequisites

- Decision context or problem statement provided by user
- Template available at `.speckit-templates/specs/adr-template.md`

## User Input

`/speckit.matd.specify-adr [DECISION_TITLE]`

**Arguments**:
- `[DECISION_TITLE]`: Optional decision identifier. If not provided, will be determined during grill-me session.

## Step 1: Load Configuration

Load from `.specify/harness-tdd-config.yml` or use defaults:

| Key | Default | Purpose |
|-----|---------|---------|
| `artifacts.root` | `docs` | Root directory for ADRs |
| `adr.directory` | `architecture/decisions` | ADR subdirectory |
| `adr.numbering` | `sequential` | ADR numbering strategy |
| `workflow.agent_timeout` | `30` | Agent task timeout in minutes (default: 30 if key missing) |
| `planning.skill` | `grill-me` | Skill used for discovery questioning |

If config file is missing or unreadable, continue with the defaults above. Log a warning to stderr but do not abort.

## Step 2: Determine ADR Location and Number

**Check for existing ADRs:**

Search paths in order:
1. `docs/architecture/decisions/` (default)
2. `openspec/changes/<feature-id>/adr/` (if feature_id provided via optional `--feature-id` flag)
3. Custom path from config: `{artifacts.root}/{adr.directory}/`

- If ADRs exist: determine next sequential number by parsing existing ADR filenames (e.g., `adr-001-*.md`, `adr-002-*.md` → next is 003)
- If no ADRs exist: start with `001`
- Store as `{adr_number}` (zero-padded 3 digits)

## Step 3: Check Related Context

Search for relevant context (optional, loads if available):

1. **System Constitution**: `docs/architecture/technical-constitution.md` or `.specify/technical-constitution.md`
2. **Product Brief**: `docs/product-brief.md`
3. **Feature Spec** (if `--feature-id` provided): `docs/features/{feature_id}-spec.md`
4. **Related ADRs**: scan ADR directory for related decisions

- If found: load silently for reference during grill-me session
- If not found: proceed without context

## Step 4: Run Grill-Me Session (general-grill-me skill)

Use the `general-grill-me` skill throughout this step.

**Goal:** Reach consensus on the architectural decision through relentless questioning.

**Approach:**
- Ask questions **one at a time**, waiting for user response before continuing
- Reference loaded context (constitution, product brief, related ADRs) in your questions
- Track unanswered/deferred questions separately from answered ones
- Continue until you reach consensus with the user OR user signals done (e.g., "that's enough")
- Allow user to defer unknowns — note them as open questions, do not block on them

**Questions must cover all ADR sections:**

- **Decision Title** — What is the decision being made? Be specific and concise.
- **Context & Problem Statement** — What problem are we solving? What forces are at play?
- **Decision Drivers** — What factors influence this decision? (technical, business, organizational)
- **Considered Options** — What alternatives were considered? (minimum 3 options required)
  - For each option:
    - Description
    - Pros (benefits)
    - Cons (drawbacks/risks)
- **Decision Outcome** — Which option was chosen? Why?
- **Consequences** — What are the positive and negative outcomes?
- **Mitigation Strategies** — How will negative consequences be addressed?
- **Related Documents** — Are there related ADRs, specs, or external references?

**Also extract for decision diagram** (if answers reveal decision flow):
- Key decision points
- Alternative paths
- Chosen outcome and its implications

## Step 5: Generate ADR

- Fill `.speckit-templates/specs/adr-template.md` with answers gathered in the grill-me session
- Assign ADR number from Step 2: `{adr_number}`
- Generate decision slug from title: lowercase, hyphenated (e.g., "Use PostgreSQL for Data Storage" → `use-postgresql-for-data-storage`)
- Save to: `{adr_directory}/adr-{adr_number}-{decision_slug}.md`
- If save fails: ❌ Exit 2 with message: "Error: failed to write ADR to `{adr_path}`"
- If `adr-template.md` is missing: ❌ Exit 2 with message: "Error: template not found at `.speckit-templates/specs/adr-template.md`"

## Step 6: Create Decision Diagram (if applicable)

If the decision involves architectural flow or component relationships:

- Use `arch-mermaid-diagrams` skill to create a decision diagram
- Include in the ADR under "Decision Diagram" section
- Diagram types based on context:
  - Flowchart: decision flow and outcomes
  - Component diagram: architecture impact
  - Sequence diagram: interaction changes

If no diagram is needed, leave the section with the placeholder diagram or remove it.

## Step 7: Save Open Questions (if any)

- If any questions were deferred by user during the grill-me session:
  - Append them to: `{adr_path}` in a new section `## Open Questions`
  - Format: a simple list with each unanswered question and the context in which it arose
- If no open questions exist: skip this step entirely

## Step 8: Report

Show a final summary:

```
✓ ADR created at: {adr_path}
  ADR Number: {adr_number}
  Decision: {decision_title}
  Status: draft
```

Suggest next steps:

> ADR is now available for review. Consider:
> - Sharing with team for feedback before finalizing
> - Linking related specs or implementation plans
> - Updating status to "accepted" once decision is final

## Exit Codes

- **0**: Success — ADR created
- **1**: Validation failure — required inputs missing
- **2**: Escalation required — template missing or write error

## Configuration Reference

`.specify/harness-tdd-config.yml` keys used by this command:

```yaml
artifacts:
  root: docs                          # Root dir for ADR output

adr:
  directory: architecture/decisions   # ADR subdirectory (relative to artifacts.root)
  numbering: sequential               # ADR numbering strategy (sequential, timestamp, uuid)

workflow:
  agent_timeout: 30                   # Grill-me session timeout in minutes (default: 30)

planning:
  skill: grill-me                     # Skill used for discovery
```

## Related Commands

- `/speckit.matd.specify-solution-design`: Create solution design with multi-alternative ADR comparison
- `/speckit.matd.specify-product-brief`: Create product brief (provides context for ADRs)
- `/speckit.specify`: Create feature spec (can reference ADRs)

## ADR vs Solution Design ADR

**Use Standalone ADR when:**
- Documenting a single architectural decision
- Decision is project-wide or system-level (not feature-specific)
- Need to capture decision rationale for future reference
- Decision affects multiple features or components

**Use Solution Design ADR when:**
- Comparing 3+ solution alternatives for a specific feature
- Need detailed C1/C2/C3 diagrams for each alternative
- Decision is tightly coupled to feature implementation
- Part of MATD workflow (discover → solution-design → test → implement)

**Key Differences:**
- Standalone ADR: single decision, 3+ options, grill-me interview
- Solution Design ADR: multi-alternative comparison, C4 diagrams, orchestrated c4-* agents

## ADR Numbering Conventions

**Sequential (default):**
- Format: `adr-001-decision-slug.md`, `adr-002-decision-slug.md`
- Benefits: easy to reference, clear ordering
- Drawback: merge conflicts in multi-team scenarios

**Timestamp:**
- Format: `adr-20250511-decision-slug.md`
- Benefits: no conflicts, date context
- Drawback: ordering requires parsing dates

**UUID:**
- Format: `adr-a1b2c3d4-decision-slug.md`
- Benefits: zero conflicts, decentralized
- Drawback: harder to reference, no ordering

Configure via `adr.numbering` in config file.
