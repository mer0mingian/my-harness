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

**Purpose**: Various specification formats for requirements definition.

**Expected Files**:
- `prd-template.md` - Product Requirements Document
- `tech-req-template.md` - Technical Requirements Specification
- `adr-template.md` - Architecture Decision Record

**PRD Template Should Include**:
- Feature overview and business value
- User stories and personas
- Acceptance criteria
- Success metrics
- Dependencies and assumptions

**Tech-Req Template Should Include**:
- Technical requirements and constraints
- System architecture impact
- Component-level requirements
- Performance requirements
- Security considerations

**ADR Template Should Include**:
- Decision title and status
- Context and problem statement
- Decision drivers
- Considered options
- Decision outcome and consequences

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

**Purpose**: Standardized QA validation reporting.

**Expected Files**:
- `browser-qa-template.md` - Browser-based QA validation
- `cli-qa-template.md` - CLI-based QA validation

**Browser QA Template Should Include**:
- Test URLs and routes
- UI element validation checklist
- Screenshot placeholders
- Accessibility checks
- Responsive design validation

**CLI QA Template Should Include**:
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
    prd:
      path: specs/prd-template.md
    tech-req:
      path: specs/tech-req-template.md
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
- Review [Technical-Requirements.md](../../harness-sandbox/Technical-Requirements.md) for template requirements
- Consult team's architectural decision records (ADRs)

---

## Related Documentation

- [SpecKit Documentation](https://github.github.io/spec-kit/)
- [Superpowers Skills](https://github.com/obra/superpowers)
- [harness-sandbox README](../../harness-sandbox/README.md)
- [Agentic Workflow Guide](../../harness-sandbox/Agentic-Workflow.md)
