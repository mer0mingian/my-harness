# SpecKit Templates - Team Population Guide

This directory contains company-specific templates for SpecKit-driven development workflows. Teams should populate these directories with Markdown templates that align with company standards and practices.

## Directory Structure

```
.speckit-templates/
├── constitution/       # Constitutional principles templates
├── specs/             # Specification templates
├── plans/             # Implementation plan templates
├── tasks/             # Task breakdown templates
├── qa/                # QA validation report templates
└── archive/           # Archival index templates
```

## Template Guidelines

### Constitution Templates (`constitution/`)

**Purpose**: Define project principles, technical standards, and company requirements for agent-workspaces.

**Expected Files**:
- `stepstone-constitution-template.md` - Company-wide constitutional template

**Should Include**:
- Project principles and values
- Technical standards and patterns
- Quality requirements
- Security and compliance requirements
- Team collaboration guidelines
- Decision-making frameworks

**Variables**:
- `{system_name}` - Name of the system/workspace
- `{domain}` - Business domain
- `{team_name}` - Owning team

---

### Specification Templates (`specs/`)

**Purpose**: Lightweight, feature-focused specifications for individual features. This is the native SpecKit format.

**Expected Files**:
- `spec-template.md` - Lightweight Feature Specification (SpecKit native format)
- `product-brief-template.md` - Comprehensive Product Brief (product-level, not feature-level)
- `adr-template.md` - Architecture Decision Record

---

#### Feature Spec Template (`spec-template.md`)

**Format**: Native SpecKit lightweight specification

**Scope**: Individual feature within a product

**Sections** (8 required):
1. **What & Why** - Feature definition and problem statement
2. **Business Value** - Value to users/business, expected outcomes
3. **Measurability** - Success metrics and measurement methods
4. **Goals & No-goals** - Scope boundaries (in-scope vs out-of-scope)
5. **Risks & Stories** - Technical/organizational risks, affected user stories
6. **Dependencies** - Prerequisites and blockers
7. **People** - Product Owner, Tech Lead, Stakeholders
8. **Metrics** - Success measurement criteria

**Variables**:
- `{feature_id}` - Unique feature identifier
- `{feature_name}` - Feature title
- `{timestamp}` - Creation timestamp
- `{what_why_placeholder}` - Feature definition
- `{business_value_placeholder}` - Business value statement
- `{measurability_placeholder}` - Success metrics
- `{goal_1}`, `{goal_2}` - In-scope goals
- `{no_goal_1}`, `{no_goal_2}` - Out-of-scope items
- `{risk_1}`, `{risk_2}` - Identified risks
- `{story_1_description}`, `{story_2_description}` - User stories
- `{dependency_1}`, `{dependency_2}` - Prerequisites
- `{product_owner}`, `{tech_lead}`, `{stakeholders}` - People
- `{metric_1}`, `{metric_2}` - Success metrics

**When to Use**:
- Adding features to existing products
- Need lightweight, focused specifications
- Creating testable requirements
- Planning implementation tasks

**Note**: This is the NATIVE SpecKit format — lightweight and feature-focused. For comprehensive product-level documentation, use Product Brief Template below.

---

#### ADR Template (`adr-template.md`)

**Purpose**: Document significant architectural decisions

**ADR Template Should Include**:
- Decision title and status (with ADR number)
- Context and problem statement
- Decision drivers (factors influencing the decision)
- Considered options (minimum 3 alternatives with pros/cons)
- Decision outcome (chosen option with rationale)
- Consequences (positive and negative impacts)
- Mitigation strategies (addressing negative consequences)
- Related documents and links

**ADR Creation**:
- Use `/speckit.matd.specify-adr` command to create standalone ADRs
- ADRs are numbered sequentially (adr-001, adr-002, etc.)
- Default location: `docs/architecture/decisions/`
- Can also be feature-specific: `openspec/changes/<feature-id>/adr/`

---

### Product Brief Template (`specs/`)

**Purpose**: Comprehensive product-level vision and goals for NEW products. This is product-level, NOT feature-level.

**Format**: Comprehensive product documentation (formerly PRD template)

**Scope**: Entire product, not individual features

**Expected Files**:
- `product-brief-template.md` - Product-level vision, goals, and constraints

**Sections** (7 required):
1. **Product Vision & Goals** - Overarching vision, strategic goals
2. **Target Users & Personas** - Primary personas, user needs, pain points
3. **Core Value Proposition** - Unique value, key differentiators
4. **High-Level Features** - Core capabilities (high-level only, NOT detailed specs)
5. **Success Metrics** - KPIs, success criteria, measurement methods
6. **Technical Context** - Technical constitution links, technology constraints, architecture references
7. **Known Constraints** - Business, technical, organizational constraints

**Variables**:
- `{product_name}` - Name of the product
- `{domain}` - Business domain
- `{vision}` - Product vision statement
- `{team_name}` - Owning team
- `{timestamp}` - Creation timestamp
- `{goal_1}`, `{goal_2}`, `{goal_3}` - Strategic goals
- `{persona_1_name}`, `{persona_1_description}` - User personas
- `{value_proposition}` - Core value proposition
- `{differentiator_1}`, `{differentiator_2}` - Key differentiators
- `{feature_1_name}`, `{feature_1_description}` - High-level features
- `{kpi_1}`, `{kpi_1_target}` - Success metrics
- `{tech_constraint_1}`, `{tech_constraint_2}` - Technology constraints

**When to Use**:
- Creating a NEW product (not a feature)
- Need comprehensive product-level vision document
- Establishing success metrics for entire product
- Defining target users and value proposition

**Integration with Feature Specs**:
- Product briefs are OPTIONAL — feature specs can exist independently
- When product brief exists, matd-specifier agent can reference it as additional context during feature spec creation
- Use `/speckit.matd.specify-product-brief` to create product brief
- Feature specs (spec-template.md) are created separately for individual features

**Comparison: Product Brief vs Feature Spec**

| Aspect | Product Brief | Feature Spec |
|--------|--------------|--------------|
| **Scope** | Product-level | Feature-level |
| **Depth** | Comprehensive | Lightweight |
| **Format** | Formerly PRD | Native SpecKit |
| **Sections** | 7 sections | 8 sections |
| **Focus** | Vision, strategy, users | What/Why, goals, metrics |
| **Use Case** | New products | Individual features |
| **Command** | `/speckit.matd.specify-product-brief` | (SpecKit native) |

---

### Implementation Plan Templates (`plans/`)

**Purpose**: Guide implementation strategy with multi-repo awareness.

**Expected Files**:
- `implementation-plan-template.md` - Full implementation plan template

**Should Include**:
- Implementation phases and milestones
- Multi-Repo Branching section (affected component repos)
- Task breakdown preview
- Dependencies and risks
- Testing strategy
- Rollout plan

**Variables**:
- `{plan_title}` - Plan title
- `{affected_repos}` - List of component repos impacted
- `{dependencies}` - External dependencies

---

### Task Breakdown Templates (`tasks/`)

**Purpose**: Granular task breakdown with agent assignment support.

**Expected Files**:
- `task-breakdown-template.md` - Task list with acceptance criteria

**Should Include**:
- Task list with IDs
- Acceptance criteria per task
- Agent assignment recommendations
- File patterns affected
- Testing requirements
- Definition of done

**Variables**:
- `{task_title}` - Task breakdown title
- `{assigned_agents}` - Recommended agent assignments
- `{file_patterns}` - File patterns per task

---

### QA Validation Templates (`qa/`)

**Purpose**: Standardized QA validation reporting and test strategy documentation.

**Expected Files**:
- `test-strategy-template.md` - Project-level test strategy and test pyramid
- `browser-qa-template.md` - Browser-based QA validation (optional)
- `cli-qa-template.md` - CLI-based QA validation (optional)

---

#### Test Strategy Template (`test-strategy-template.md`)

**Purpose**: Define project-level testing approach, test pyramid ratios, patterns, and coverage targets.

**Format**: Comprehensive test strategy document

**Scope**: Project or product-level (not feature-specific)

**Sections** (12 required):
1. **Testing Philosophy & Principles** - Core testing philosophy, principles, quality gates
2. **Test Pyramid Strategy** - Unit:Integration:E2E ratios, layer definitions, execution time targets
3. **Test Patterns & Conventions** - Naming conventions, organization, common patterns, anti-patterns
4. **Tools & Frameworks** - Testing stack (unit, integration, e2e, mocking, coverage, CI/CD tools)
5. **Coverage Targets** - Line/branch/function coverage targets, enforcement strategy, exemptions
6. **CI/CD Integration** - Pipeline structure, test execution per stage, failure handling
7. **Performance & Load Testing Strategy** - Performance testing approach, load scenarios, benchmarks
8. **Security Testing Approach** - Static/dynamic analysis, dependency scanning, compliance
9. **Test Data Management** - Test data strategy, generation, privacy, environment-specific data
10. **Testing Workflow** - Developer workflow, TDD cycle (Red-Green-Refactor)
11. **Review & Maintenance** - Test review process, flaky test management, maintenance schedule
12. **Metrics & Reporting** - Key metrics, reporting cadence, dashboard location

**Variables**:
- `{project_name}` - Project identifier
- `{timestamp}` - Creation timestamp
- `{test_lead}` - Test strategy owner
- `{testing_philosophy}` - Core testing philosophy
- `{unit_ratio}`, `{integration_ratio}`, `{e2e_ratio}` - Test pyramid distribution percentages
- `{test_pyramid_rationale}` - Rationale for chosen distribution
- `{unit_scope}`, `{integration_scope}`, `{e2e_scope}` - Scope definitions per layer
- `{unit_tool}`, `{integration_tool}`, `{e2e_tool}` - Testing tools per layer
- `{line_coverage_target}`, `{branch_coverage_target}` - Coverage targets
- `{ci_pipeline_structure}` - CI/CD pipeline structure
- `{performance_testing_approach}` - Performance testing strategy
- `{security_static_approach}`, `{security_dynamic_approach}` - Security testing approaches
- `{test_data_strategy}` - Test data management strategy
- `{tdd_cycle_description}` - TDD workflow description
- And many more template variables for comprehensive coverage

**When to Use**:
- Starting a new project or product
- Need to define overall testing approach
- Establishing test pyramid ratios
- Defining quality gates and coverage targets
- Setting up CI/CD testing pipeline

**Command**: `/speckit.matd.specify-test-strategy [project-name]`

**Integration with Test Designs**:
- Test strategy is OPTIONAL but recommended
- When test strategy exists, matd-qa agent can reference it for test pyramid guidance during feature test creation
- Feature test designs can be created independently without a test strategy

---

**Browser QA Template Should Include** (optional):
- Test URLs and routes
- UI element validation checklist
- Screenshot placeholders
- Accessibility checks
- Responsive design validation

**CLI QA Template Should Include** (optional):
- Test commands to execute
- Expected outputs
- API endpoint validation
- Build output verification
- Performance checks

---

### Archive Index Templates (`archive/`)

**Purpose**: Standardize post-merge archival entries.

**Expected Files**:
- `archive-index-template.md` - Archived specification index entry

**Should Include**:
- Spec ID and completion date
- Summary of changes
- PR links (workspace + components)
- Test coverage metrics
- QA validation results
- Lessons learned

**Variables**:
- `{spec_id}` - Specification ID
- `{completion_date}` - Merge/completion date
- `{pr_links}` - Pull request URLs

---

## Template Format Standards

### Markdown Structure

All templates should use consistent Markdown formatting:

```markdown
# {Title}

**Spec ID**: {spec_id}  
**Author**: {author}  
**Date**: {date}  
**Status**: {status}

## Section 1

Content...

## Section 2

Content...
```

### Variable Syntax

Use curly braces for template variables:
- `{variable_name}` - Simple variable
- `{variable_name:default_value}` - Variable with default
- `<!-- {variable_name} -->` - Comment-style variable for optional sections

### Frontmatter (Optional)

Templates may include YAML frontmatter for metadata:

```yaml
---
template: constitution
version: 1.0
category: governance
tags: [principles, standards]
---
```

---

## Integration with SpecKit

Templates are referenced in workspace `.specify/template-config.yml`:

```yaml
catalog:
  source: ../harness-tooling/.speckit-templates
  type: local

templates:
  constitution:
    path: constitution/stepstone-constitution-template.md
  specs:
    spec:
      path: specs/spec-template.md
    adr:
      path: specs/adr-template.md
```

When SpecKit creates artifacts, it:
1. Loads the appropriate template from this directory
2. Prompts for variable values
3. Substitutes variables in the template
4. Saves the populated artifact to the workspace

---

## Best Practices

### Template Maintenance

- Version templates in git alongside marketplace content
- Review and update templates quarterly
- Collect feedback from teams using templates
- Document template changes in changelog

### Variable Design

- Keep variables simple and self-explanatory
- Provide examples in comments
- Use consistent naming across templates
- Document all variables in template header

### Company Standards

- Align templates with company architecture patterns
- Include compliance requirements where applicable
- Reference company design systems and style guides
- Link to internal documentation and resources

---

## Getting Started

1. **Review Existing Templates**: Check if similar templates exist in other repos
2. **Draft Template**: Create Markdown file with structure and variables
3. **Test Template**: Use in SpecKit workflow to verify variable substitution
4. **Document Variables**: Add variable documentation to template header
5. **Commit and Tag**: Version control with semantic versioning
6. **Update Config**: Reference new template in workspace template-config.yml

---

## Support

For questions or issues with templates:
- Check [Agentic-Workflow.md](../../harness-sandbox/Agentic-Workflow.md) for workflow context
- Review the technical constitution for project-wide technical standards
- Consult team's architectural decision records (ADRs)

---

## Related Documentation

- [SpecKit Documentation](https://github.github.io/spec-kit/)
- [Superpowers Skills](https://github.com/obra/superpowers)
- [harness-sandbox README](../../harness-sandbox/README.md)
- [Agentic Workflow Guide](../../harness-sandbox/Agentic-Workflow.md)
