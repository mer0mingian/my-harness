---
description: "Create or update product brief using grill-me interview for new products"
agent: matd-specifier
skills:
  - 'general-grill-me'
  - 'stdd-project-summary'
tools:
  - 'filesystem/read'
  - 'filesystem/write'
templates:
  product-brief: .speckit-templates/specs/product-brief-template.md
  constitution: templates/system-constitution-template.md
exit_codes:
  0: "Success - product brief created or updated"
  1: "Validation failure - required inputs missing"
  2: "Escalation required - template missing or write error"
---

# Product Brief Workflow (MATD — Product-Level Discovery)

This command runs a grill-me session to elicit high-level product vision and create a product brief. Use this for NEW products, not individual features (use `/speckit.specify` for feature specs).

**Note:** This command uses the Opus agent (not a dedicated subagent) with the `general-grill-me` skill for deep requirements discovery through relentless questioning.

## Prerequisites

- Product name or concept provided by user
- Template available at `.speckit-templates/specs/product-brief-template.md`

## User Input

`/speckit.matd.specify-product-brief [PRODUCT_NAME]`

**Arguments**:
- `[PRODUCT_NAME]`: Optional product identifier. If not provided, will be determined during grill-me session.

## Step 1: Load Configuration

Load from `.specify/harness-tdd-config.yml` or use defaults:

| Key | Default | Purpose |
|-----|---------|---------|
| `artifacts.root` | `docs` | Root directory for product brief |
| `workflow.agent_timeout` | `30` | Agent task timeout in minutes (default: 30 if key missing) |
| `planning.skill` | `grill-me` | Skill used for discovery questioning |

If config file is missing or unreadable, continue with the defaults above. Log a warning to stderr but do not abort.

## Step 2: Check Existing Product Brief

**Check for existing Product Brief:**

Search for: `docs/product-brief.md`

- If found: mention it to the user — "Product Brief already exists at `docs/product-brief.md`, will merge updates" — then proceed
- If not found: continue (will create from template in Step 5)

## Step 3: Check Existing System Constitution

Search in order:
1. `docs/architecture/technical-constitution.md`
2. `.specify/technical-constitution.md`

- If found: load it silently for reference during grill-me session
- If not found: note that constitution may be created if technical constraints are discussed

## Step 4: Run Grill-Me Session (general-grill-me skill)

Use the `general-grill-me` skill throughout this step.

**Goal:** Reach consensus on product vision, goals, and high-level features through relentless questioning.

**Approach:**
- Ask questions **one at a time**, waiting for user response before continuing
- Reference loaded product brief context (if exists) in your questions
- Track unanswered/deferred questions separately from answered ones
- Continue until you reach consensus with the user OR user signals done (e.g., "that's enough")
- Allow user to defer unknowns — note them as open questions, do not block on them

**Questions must cover all product-brief sections:**

- **Product Vision & Goals** — What is the overarching vision? What strategic goals drive this product?
- **Target Users & Personas** — Who will use this? What are their primary needs?
- **Core Value Proposition** — What unique value does this deliver? Why would users choose this?
- **High-Level Features** — What are the main capabilities? (Not detailed specs — just capabilities)
- **Success Metrics** — How will success be measured? What KPIs matter?
- **Technical Context** — Are there technology constraints? Does a technical constitution exist or need to be created?
- **Known Constraints** — What business, technical, or organizational constraints exist?

**Also extract for System Constitution** (if answers reveal tech constraints or NFRs):

- Tech choices (languages, frameworks, platforms)
- Team skills and maturity levels
- Compliance requirements (GDPR, SOC2, etc.)
- Non-functional requirement (NFR) constraints (latency, availability, throughput)

## Step 5: Generate/Update Product Brief

- Fill `.speckit-templates/specs/product-brief-template.md` with answers gathered in the grill-me session
- If existing Product Brief found (Step 2): merge new information into it — do not overwrite sections that are already complete unless the user provided updates in this session
- Save to: `docs/product-brief.md`
- If save fails: ❌ Exit 2 with message: "Error: failed to write Product Brief to `docs/product-brief.md`"
- If `product-brief-template.md` is missing: ❌ Exit 2 with message: "Error: template not found at `.speckit-templates/specs/product-brief-template.md`"

## Step 6: Generate/Update System Constitution (if needed)

If technical constraints or NFR information were discussed in Step 4:

- Extract tech constraints and NFR information gathered in Step 4
- If constitution exists (Step 3): merge new findings into the existing file silently
- If no constitution exists: create from `templates/system-constitution-template.md`
- Save to: `docs/architecture/technical-constitution.md` (or the existing path found in Step 3)
- If save fails: ❌ Exit 2 with message: "Error: failed to write System Constitution"
- If `system-constitution-template.md` is missing and no existing constitution: ❌ Exit 2

If no technical constraints were discussed, skip this step entirely.

## Step 7: Save Open Questions (if any)

- If any questions were deferred by user during the grill-me session:
  - Save them to: `docs/product-brief-open-questions.md`
  - Format: a simple list with each unanswered question and the context in which it arose
- If no open questions exist: skip this step entirely — do not create an empty file

## Step 8: Report

Show a final summary:

```
✓ Product Brief created/updated at: docs/product-brief.md
✓ System Constitution created/updated at: docs/architecture/technical-constitution.md (if applicable)
⚠ Open questions saved at: docs/product-brief-open-questions.md (only if any)
```

Suggest next step:

> Product Brief is now available as context for feature specifications. When creating feature specs with `/speckit.specify`, the matd-specifier agent can reference this Product Brief for additional context.

## Exit Codes

- **0**: Success — Product Brief created or updated
- **1**: Validation failure — required inputs missing
- **2**: Escalation required — template missing or write error

## Configuration Reference

`.specify/harness-tdd-config.yml` keys used by this command:

```yaml
artifacts:
  root: docs                   # Root dir for Product Brief output

workflow:
  agent_timeout: 30            # Grill-me session timeout in minutes (default: 30)

planning:
  skill: grill-me              # Skill used for discovery
```

## Related Commands

- `/speckit.specify`: Create feature spec (use this for individual features)
- `/speckit.matd.specify-solution-design`: Create architecture design for a feature

## Product Brief vs Feature Spec

**Use Product Brief when:**
- Starting a new product from scratch
- Need high-level vision and goals document
- Defining product-level success metrics
- Documenting target users and personas

**Use Feature Spec when:**
- Adding features to existing products
- Need detailed technical requirements
- Creating testable specifications
- Planning implementation tasks

**Note:** Product Briefs are OPTIONAL. Feature specs can be created independently without a Product Brief.
