---
template: adr
type: adr
version: "1.0"
status: draft
created: "{{timestamp}}"
---

# ADR-{{adr_number}}: {{decision_title}}

**Status:** {{status}}  
**Date:** {{date}}  
**Decision Maker:** {{decision_maker}}  
**Related Documents:** {{related_docs}}

## Context & Problem Statement

_What is the architectural problem or decision that needs to be made? What are the forces at play (technical, organizational, business)?_

{{context}}

**Key Drivers:**
- {{driver_1}}
- {{driver_2}}
- {{driver_3}}

## Decision Drivers

_What factors influenced this decision? What requirements or constraints shaped the choice?_

- **{{driver_category_1}}**: {{driver_description_1}}
- **{{driver_category_2}}**: {{driver_description_2}}
- **{{driver_category_3}}**: {{driver_description_3}}

## Considered Options

### Option 1: {{option_1_name}}

**Description:** {{option_1_description}}

**Pros:**
- {{option_1_pro_1}}
- {{option_1_pro_2}}

**Cons:**
- {{option_1_con_1}}
- {{option_1_con_2}}

### Option 2: {{option_2_name}}

**Description:** {{option_2_description}}

**Pros:**
- {{option_2_pro_1}}
- {{option_2_pro_2}}

**Cons:**
- {{option_2_con_1}}
- {{option_2_con_2}}

### Option 3: {{option_3_name}}

**Description:** {{option_3_description}}

**Pros:**
- {{option_3_pro_1}}
- {{option_3_pro_2}}

**Cons:**
- {{option_3_con_1}}
- {{option_3_con_2}}

## Decision Outcome

**Chosen Option:** {{chosen_option}}

**Rationale:** {{decision_rationale}}

## Decision Diagram (Optional)

_Visual representation of the decision flow or architecture impact._

```mermaid
graph TD
    A[{{decision_context}}] --> B{Decision Point}
    B -->|Option 1| C[{{option_1_outcome}}]
    B -->|Option 2| D[{{option_2_outcome}}]
    B -->|Chosen: {{chosen_option}}| E[{{chosen_outcome}}]
```

## Consequences

### Positive Consequences

- {{positive_consequence_1}}
- {{positive_consequence_2}}
- {{positive_consequence_3}}

### Negative Consequences

- {{negative_consequence_1}}
- {{negative_consequence_2}}

### Mitigation Strategies

_How will we address the negative consequences?_

- {{mitigation_1}}
- {{mitigation_2}}

## Implementation Notes

_Key considerations for implementing this decision._

{{implementation_notes}}

## Links

- Related ADRs: {{related_adrs}}
- Related Specs: {{related_specs}}
- Reference Documentation: {{reference_docs}}
- Discussion Context: {{discussion_links}}

---

**Verification Checklist:**
- [ ] YAML frontmatter valid (template: adr, type: adr)
- [ ] ADR number assigned (sequential)
- [ ] Decision title is clear and concise
- [ ] Context explains the problem thoroughly
- [ ] At least 3 options considered
- [ ] Decision outcome clearly stated with rationale
- [ ] Positive and negative consequences documented
- [ ] Mitigation strategies provided for negative consequences
- [ ] Related documents linked
- [ ] No placeholder values remain ({{...}})
