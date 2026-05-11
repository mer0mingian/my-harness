---
description: "Stage 1: Feature Specification"
agent: matd-orchestrator
subtask: true
return:
  # 1. Specifier initializes the feature directory and defines the goal
  - /subtask {agent: matd-specifier && as: spec_init} Define project summary in @docs/business/product_summary.md and initialize OpenSpec directory for "$ARGUMENTS".
  
  # 2. Specifier drafts the requirements
  - /subtask {agent: matd-specifier && as: spec_draft} Create `proposal.md` and `specs/requirements.md` using Job Stories, EARS, and Gherkin for "$ARGUMENTS".
  
  # 3. Critical Thinker Red Teams the requirements
  - /subtask {agent: matd-critical-thinker && as: spec_audit} Critically review the requirements in $RESULT[spec_draft]. Identify ambiguities, missing edge cases, or logical inconsistencies.
  
  # 4. Specifier finalizes the artifacts
  - /subtask {agent: matd-specifier} Address the gaps identified in $RESULT[spec_audit] and finalize the OpenSpec artifacts.
  
  # 5. User approval gate
  - "Stage 1 (Specification) for '$ARGUMENTS' is complete. OpenSpec artifacts are ready. Please review the proposal and user stories. Reply with 'Approved' to continue to Stage 2 (Solution Design)."
---
# Feature Specification: $ARGUMENTS

Initiating the specification sequence. I will delegate directory initialization and drafting to the Specifier, and validation to the Critical Thinker.
