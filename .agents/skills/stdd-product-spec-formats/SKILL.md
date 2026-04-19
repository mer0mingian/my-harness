---
name: stdd-product-spec-formats
description: Master various formats for defining product requirements and logic-heavy features (Job Stories, Gherkin, EARS, Planguage, Anti-Story).
---
# Product Specification Formats

Master various formats for defining product requirements and logic-heavy features. Use these formats when generating documents inside the `openspec/changes/<change-name>/specs/` directory.

## Core Formats

1. **Job Stories (Situation-Motivation-Outcome)**: Focus on context. `When [Situation], I want to [Motivation], so I can [Expected Outcome].`
2. **Given-When-Then (Gherkin)**: Testable documentation for edge cases.
3. **EARS**: Universal rules. `The [System] shall [Action].`
4. **Planguage**: Non-functional requirements (Scale, Meter, Must, Plan).
5. **Constraint-Based Requirements (Anti-Story)**: Guardrails. `The [System] shall not [Action] during [Condition].`

## Application Strategy

Combine these! Write a Job Story for the overarching goal, use EARS for the core logic rules, and append Gherkin scenarios for edge cases and testing.

## References & Examples

See [references/examples.md](references/examples.md) for concrete examples of each format.
