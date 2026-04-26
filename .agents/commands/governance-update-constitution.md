---
description: "Amend an existing TECHNICAL_CONSTITUTION.md section without rewriting approved content."
agent: governance-lead
subtask: true
return:
  - /subtask {agent: governance-lead && as: gov_amend_intake} The user wants to amend section "$ARGUMENTS" of docs/governance/TECHNICAL_CONSTITUTION.md. Read the current file, identify the targeted section, and confirm with the user what should change. Return a structured diff intent.

  - /subtask {agent: governance-constitution-author && as: gov_amend_apply} Apply the diff intent from $RESULT[gov_amend_intake]. Preserve any line tagged "<!-- approved: YYYY-MM-DD -->". Add new content under "## Pending Amendments" if approval is required. Bump the Version field (semver: minor for new section, patch for clarification).

  - /subtask {agent: governance-lead && as: gov_amend_validate} Run governance-validate-artifacts. Report any new errors introduced by the amendment.

  - "Constitution amendment for section '$ARGUMENTS' is staged. Validation report attached. Reply with 'Approve' to mark approved (replaces the Pending Amendments tag with `<!-- approved: $(date +%Y-%m-%d) -->`) or with edits to refine."
---
# Update Technical Constitution: $ARGUMENTS

Use this when an architect, security review, or compliance change needs to
amend a specific constitution section (for example, "Section 1.2 Frontend
Stack" or "Section 4.3 Dependency Management"). Approved sections are preserved
verbatim; new content lands under "Pending Amendments" until the user approves.
