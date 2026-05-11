# Product Brief Template and Command Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace deprecated discover command with product-brief template and specify-product-brief command for creating product-level summaries.

**Architecture:** Product Brief is a product-level document (for NEW products) distinct from feature-level specs. The new command uses matd-specifier agent with general-grill-me skill to interview users and populate /docs/product-brief.md. Specs can optionally reference product-brief as context.

**Tech Stack:** Markdown templates, YAML frontmatter, SpecKit command system, matd-specifier agent

---

## File Structure

**Created:**
- `.speckit-templates/specs/product-brief-template.md` - Template for product briefs
- `spec-kit-multi-agent-tdd/commands/specify-product-brief.md` - New command (renamed from discover.md)

**Modified:**
- `spec-kit-multi-agent-tdd/extension.json` - Update command registry
- `.speckit-templates/README.md` - Add product-brief documentation

**Deleted:**
- `spec-kit-multi-agent-tdd/commands/discover.md` - Renamed to specify-product-brief.md

---

### Task 1: Create Product-Brief Template

**Files:**
- Create: `.speckit-templates/specs/product-brief-template.md`

- [ ] **Step 1: Create the product-brief template file**

```bash
cd /home/minged01/repositories/harness-workplace/harness-tooling
touch .speckit-templates/specs/product-brief-template.md
```

- [ ] **Step 2: Write the complete template with YAML frontmatter and sections**

Content for `.speckit-templates/specs/product-brief-template.md`:

```markdown
---
template: product-brief
type: product-brief
version: "1.0"
status: draft
created: "{{timestamp}}"
---

# Product Brief: {{product_name}}

**Product Name:** {{product_name}}  
**Domain:** {{domain}}  
**Team:** {{team_name}}  
**Created:** {{timestamp}}

## Product Vision & Goals

_What is the overarching vision for this product? What problem does it solve at a high level?_

{{vision}}

**Strategic Goals:**
- {{goal_1}}
- {{goal_2}}
- {{goal_3}}

## Target Users & Personas

_Who will use this product? What are their needs and pain points?_

**Primary Personas:**
- **{{persona_1_name}}**: {{persona_1_description}}
- **{{persona_2_name}}**: {{persona_2_description}}

**User Needs:**
- {{user_need_1}}
- {{user_need_2}}

## Core Value Proposition

_What unique value does this product deliver? Why would users choose this over alternatives?_

{{value_proposition}}

**Key Differentiators:**
- {{differentiator_1}}
- {{differentiator_2}}

## High-Level Features

_What are the main capabilities of this product? (High-level only, detailed specs come later)_

**Core Features:**
1. **{{feature_1_name}}**: {{feature_1_description}}
2. **{{feature_2_name}}**: {{feature_2_description}}
3. **{{feature_3_name}}**: {{feature_3_description}}

**Future Capabilities:**
- {{future_feature_1}}
- {{future_feature_2}}

## Success Metrics

_How will we measure whether this product is successful?_

**Key Performance Indicators:**
- {{kpi_1}}: {{kpi_1_target}}
- {{kpi_2}}: {{kpi_2_target}}
- {{kpi_3}}: {{kpi_3_target}}

**Success Criteria:**
- {{success_criterion_1}}
- {{success_criterion_2}}

## Technical Context

_Links to technical constitution and architectural constraints._

**Technical Constitution:** {{constitution_path|default("docs/architecture/technical-constitution.md")}}

**Technology Constraints:**
- {{tech_constraint_1}}
- {{tech_constraint_2}}

**Architecture References:**
- {{arch_reference_1}}
- {{arch_reference_2}}

## Known Constraints

_What limitations or constraints should be considered during feature development?_

**Business Constraints:**
- {{business_constraint_1}}
- {{business_constraint_2}}

**Technical Constraints:**
- {{technical_constraint_1}}
- {{technical_constraint_2}}

**Organizational Constraints:**
- {{org_constraint_1}}
- {{org_constraint_2}}

---

**Verification Checklist:**
- [ ] All 7 required sections present
- [ ] YAML frontmatter valid (template: product-brief, type: product-brief)
- [ ] Product name, domain, team, and timestamp filled
- [ ] Vision and value proposition clearly defined
- [ ] Target users and personas documented
- [ ] High-level features listed (not detailed specs)
- [ ] Success metrics are measurable
- [ ] Technical context links to constitution
- [ ] Constraints documented
- [ ] No placeholder values remain ({{...}})
```

- [ ] **Step 3: Verify template file exists and has correct structure**

```bash
cd /home/minged01/repositories/harness-workplace/harness-tooling
rtk ls -la .speckit-templates/specs/product-brief-template.md
rtk head -20 .speckit-templates/specs/product-brief-template.md
```

Expected: File exists with YAML frontmatter starting with `template: product-brief`

- [ ] **Step 4: Commit the template**

```bash
cd /home/minged01/repositories/harness-workplace/harness-tooling
rtk git add .speckit-templates/specs/product-brief-template.md
rtk git commit -m "feat: add product-brief template for new products"
```

---

### Task 2: Rename and Update Command

**Files:**
- Delete: `spec-kit-multi-agent-tdd/commands/discover.md`
- Create: `spec-kit-multi-agent-tdd/commands/specify-product-brief.md`

- [ ] **Step 1: Create the new command file**

```bash
cd /home/minged01/repositories/harness-workplace/harness-tooling
rtk git mv spec-kit-multi-agent-tdd/commands/discover.md spec-kit-multi-agent-tdd/commands/specify-product-brief.md
```

- [ ] **Step 2: Update YAML frontmatter and command content**

Replace entire content of `spec-kit-multi-agent-tdd/commands/specify-product-brief.md`:

```markdown
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

This command runs a grill-me session to elicit high-level product vision and create a product brief. Use this for NEW products, not individual features (use `/speckit.multi-agent.discover` for feature specs).

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

**Check for existing product brief:**

Search for: `docs/product-brief.md`

- If found: mention it to the user — "Product brief already exists at `docs/product-brief.md`, will merge updates" — then proceed
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
- If existing product brief found (Step 2): merge new information into it — do not overwrite sections that are already complete unless the user provided updates in this session
- Save to: `docs/product-brief.md`
- If save fails: ❌ Exit 2 with message: "Error: failed to write product brief to `docs/product-brief.md`"
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
✓ Product brief created/updated at: docs/product-brief.md
✓ System Constitution created/updated at: docs/architecture/technical-constitution.md (if applicable)
⚠ Open questions saved at: docs/product-brief-open-questions.md (only if any)
```

Suggest next step:

> Product brief is now available as context for feature specifications. When creating feature specs with `/speckit.multi-agent.discover`, the matd-specifier agent can reference this product brief for additional context.

## Exit Codes

- **0**: Success — product brief created or updated
- **1**: Validation failure — required inputs missing
- **2**: Escalation required — template missing or write error

## Configuration Reference

`.specify/harness-tdd-config.yml` keys used by this command:

```yaml
artifacts:
  root: docs                   # Root dir for product brief output

workflow:
  agent_timeout: 30            # Grill-me session timeout in minutes (default: 30)

planning:
  skill: grill-me              # Skill used for discovery
```

## Related Commands

- `/speckit.multi-agent.discover`: Create feature spec (use this for individual features)
- `/speckit.multi-agent.solution-design`: Create architecture design for a feature

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

**Note:** Product briefs are OPTIONAL. Feature specs can be created independently without a product brief.
```

- [ ] **Step 3: Verify command file structure**

```bash
cd /home/minged01/repositories/harness-workplace/harness-tooling
rtk head -30 spec-kit-multi-agent-tdd/commands/specify-product-brief.md
```

Expected: YAML frontmatter with `agent: matd-specifier` and `skills: general-grill-me`

- [ ] **Step 4: Commit the renamed and updated command**

```bash
cd /home/minged01/repositories/harness-workplace/harness-tooling
rtk git add spec-kit-multi-agent-tdd/commands/specify-product-brief.md
rtk git commit -m "feat: rename discover to specify-product-brief for product-level discovery"
```

---

### Task 3: Update Extension Registry

**Files:**
- Modify: `spec-kit-multi-agent-tdd/extension.json`

- [ ] **Step 1: Read current extension.json**

```bash
cd /home/minged01/repositories/harness-workplace/harness-tooling
rtk cat spec-kit-multi-agent-tdd/extension.json
```

- [ ] **Step 2: Update the discover command entry to specify-product-brief**

Locate the `"discover"` entry in the `"commands"` object and replace it with:

```json
    "specify-product-brief": {
      "file": "commands/specify-product-brief.md",
      "description": "Create or update product brief using grill-me interview for new products",
      "usage": "/speckit.matd.specify-product-brief [product-name]",
      "arguments": [
        {
          "name": "product_name",
          "required": false,
          "description": "Optional product identifier (determined during grill-me if not provided)"
        }
      ]
    }
```

Remove the old `"discover"` entry completely.

- [ ] **Step 3: Validate JSON structure**

```bash
cd /home/minged01/repositories/harness-workplace/harness-tooling
rtk python3 -m json.tool spec-kit-multi-agent-tdd/extension.json > /dev/null && echo "JSON valid" || echo "JSON invalid"
```

Expected: "JSON valid"

- [ ] **Step 4: Commit the extension registry update**

```bash
cd /home/minged01/repositories/harness-workplace/harness-tooling
rtk git add spec-kit-multi-agent-tdd/extension.json
rtk git commit -m "chore: update extension registry for specify-product-brief command"
```

---

### Task 4: Update Template README

**Files:**
- Modify: `.speckit-templates/README.md`

- [ ] **Step 1: Read current README to find insertion point**

```bash
cd /home/minged01/repositories/harness-workplace/harness-tooling
rtk grep -n "### Specification Templates" .speckit-templates/README.md
```

Expected: Line number where spec templates section starts

- [ ] **Step 2: Add product-brief section after spec templates section**

Insert after the "### Specification Templates (`specs/`)" section (around line 41):

```markdown
### Product Brief Template (`specs/`)

**Purpose**: High-level product vision and goals for NEW products. Different from feature specs — this is product-level, not feature-level.

**Expected Files**:
- `product-brief-template.md` - Product-level vision, goals, and constraints

**Product Brief Template Should Include**:
- Product vision and strategic goals
- Target users and personas
- Core value proposition and differentiators
- High-level feature capabilities (not detailed specs)
- Success metrics and KPIs
- Technical context and constitution references
- Business, technical, and organizational constraints

**When to Use**:
- Creating a NEW product (not a feature)
- Need product-level vision document
- Establishing success metrics for entire product
- Defining target users and value proposition

**Variables**:
- `{product_name}` - Name of the product
- `{domain}` - Business domain
- `{vision}` - Product vision statement
- `{team_name}` - Owning team
- `{timestamp}` - Creation timestamp

**Integration with Specs**:
- Product briefs are OPTIONAL — specs can exist independently
- When product brief exists, matd-specifier agent can reference it as additional context during feature spec creation
- Use `/speckit.matd.specify-product-brief` to create product brief
- Use `/speckit.multi-agent.discover` to create feature specs

---
```

- [ ] **Step 3: Update the spec template section to clarify difference**

Locate the **Spec Template Should Include** section and add this note at the end:

```markdown

**Note**: Feature specs are for individual features within a product. For product-level documentation, see Product Brief Template section above.
```

- [ ] **Step 4: Verify README has both sections**

```bash
cd /home/minged01/repositories/harness-workplace/harness-tooling
rtk grep "### Product Brief Template" .speckit-templates/README.md
rtk grep "Feature specs are for individual features" .speckit-templates/README.md
```

Expected: Both patterns found

- [ ] **Step 5: Commit README updates**

```bash
cd /home/minged01/repositories/harness-workplace/harness-tooling
rtk git add .speckit-templates/README.md
rtk git commit -m "docs: document product-brief template and clarify spec vs product-brief"
```

---

### Task 5: Verification

**Files:**
- All files created/modified in previous tasks

- [ ] **Step 1: Verify product-brief template exists and has correct structure**

```bash
cd /home/minged01/repositories/harness-workplace/harness-tooling
rtk test -f .speckit-templates/specs/product-brief-template.md && echo "Template exists" || echo "Template missing"
rtk grep "template: product-brief" .speckit-templates/specs/product-brief-template.md && echo "Frontmatter valid" || echo "Frontmatter invalid"
```

Expected: "Template exists" and "Frontmatter valid"

- [ ] **Step 2: Verify command file has correct agent reference**

```bash
cd /home/minged01/repositories/harness-workplace/harness-tooling
rtk grep "agent: matd-specifier" spec-kit-multi-agent-tdd/commands/specify-product-brief.md && echo "Agent reference correct" || echo "Agent reference missing"
rtk grep "general-grill-me" spec-kit-multi-agent-tdd/commands/specify-product-brief.md && echo "Skill reference correct" || echo "Skill reference missing"
```

Expected: "Agent reference correct" and "Skill reference correct"

- [ ] **Step 3: Verify extension.json has valid structure and no discover references**

```bash
cd /home/minged01/repositories/harness-workplace/harness-tooling
rtk python3 -m json.tool spec-kit-multi-agent-tdd/extension.json > /dev/null && echo "JSON valid" || echo "JSON invalid"
rtk grep -c '"discover"' spec-kit-multi-agent-tdd/extension.json || echo "No discover references (expected)"
rtk grep "specify-product-brief" spec-kit-multi-agent-tdd/extension.json && echo "New command registered" || echo "Command missing"
```

Expected: "JSON valid", "No discover references", "New command registered"

- [ ] **Step 4: Verify README documents product-brief**

```bash
cd /home/minged01/repositories/harness-workplace/harness-tooling
rtk grep "### Product Brief Template" .speckit-templates/README.md && echo "Section exists" || echo "Section missing"
rtk grep "OPTIONAL" .speckit-templates/README.md && echo "Optional status documented" || echo "Missing note"
```

Expected: "Section exists" and "Optional status documented"

- [ ] **Step 5: Run full verification and create summary**

```bash
cd /home/minged01/repositories/harness-workplace/harness-tooling
echo "=== Verification Summary ==="
echo "1. Product-Brief Template:"
rtk ls -lh .speckit-templates/specs/product-brief-template.md
echo ""
echo "2. Specify-Product-Brief Command:"
rtk ls -lh spec-kit-multi-agent-tdd/commands/specify-product-brief.md
echo ""
echo "3. Extension Registry:"
rtk grep -A5 "specify-product-brief" spec-kit-multi-agent-tdd/extension.json
echo ""
echo "4. Git Status:"
rtk git status --short
```

- [ ] **Step 6: Create final commit if any uncommitted changes remain**

```bash
cd /home/minged01/repositories/harness-workplace/harness-tooling
rtk git status --short
# If any uncommitted changes exist, commit them
rtk git add -A
rtk git commit -m "chore: finalize product-brief template and command implementation" || echo "No additional changes to commit"
```

---

## Self-Review

**Spec Coverage Check:**
- ✅ Task 1: Product-brief template created with all required sections (Vision, Users, Value Prop, Features, Metrics, Tech Context, Constraints)
- ✅ Task 2: Command renamed from discover.md to specify-product-brief.md with updated YAML frontmatter and matd-specifier agent reference
- ✅ Task 3: Extension.json updated with new command entry, old discover entry removed
- ✅ Task 4: Template README updated with product-brief section and clarification of spec vs product-brief
- ✅ Task 5: Comprehensive verification steps ensure all files exist with correct structure

**Placeholder Scan:**
- ✅ No "TBD", "TODO", or "implement later" placeholders
- ✅ All code blocks contain actual content (template markdown, JSON updates, bash commands)
- ✅ All file paths are absolute and exact
- ✅ All verification commands have expected output documented

**Type Consistency:**
- ✅ Template uses consistent variable syntax: `{{variable_name}}`
- ✅ YAML frontmatter structure matches existing templates (spec-template.md, system-constitution-template.md)
- ✅ Command structure matches existing command pattern (discover.md)
- ✅ Extension.json structure matches existing command entries

---

## Post-Implementation Notes

**What Changed:**
- Deprecated `discover.md` command → renamed to `specify-product-brief.md`
- New template: `product-brief-template.md` for product-level documentation
- Updated extension registry to use new command name
- Documentation clarifies product-brief (product-level) vs spec (feature-level)

**Integration Points:**
- matd-specifier agent already has required skills (general-grill-me, stdd-project-summary)
- Product brief is OPTIONAL — specs work independently
- When product brief exists at `docs/product-brief.md`, matd-specifier can reference it during spec creation

**Next Steps:**
- Test command execution: `/speckit.matd.specify-product-brief test-product`
- Verify matd-specifier agent correctly loads and uses general-grill-me skill
- Validate template variable substitution works correctly
- Consider adding example product-brief.md in documentation
