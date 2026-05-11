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
