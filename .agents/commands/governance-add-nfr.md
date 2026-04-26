---
description: "Add a new NFR to NFR_CATALOG.md using EARS notation and ISO/IEC 25010 categories."
agent: governance-lead
subtask: true
return:
  - /subtask {agent: governance-lead && as: gov_nfr_intake} The user wants to add an NFR for "$ARGUMENTS". Confirm the ISO 25010 category, the EARS template type (ubiquitous, event-driven, state-driven, unwanted, optional-feature), the measurable threshold, the test strategy, and the priority. Read the existing docs/governance/NFR_CATALOG.md to find the next free ID for the chosen category.

  - /subtask {agent: governance-nfr-specialist && as: gov_nfr_apply} Using $RESULT[gov_nfr_intake], append the new NFR block to docs/governance/NFR_CATALOG.md. Update the NFR Validation Matrix appendix with the new ID and its test owner.

  - /subtask {agent: governance-lead && as: gov_nfr_validate} Run governance-validate-artifacts. Confirm the new ID does not collide and that the EARS keyword is present.

  - "NFR added for '$ARGUMENTS'. Validation report attached. Update any user stories or ADRs that should reference the new NFR ID."
---
# Add NFR: $ARGUMENTS

Adds a single NFR to `docs/governance/NFR_CATALOG.md` while preserving the
catalog's stable IDs and ISO/IEC 25010 grouping. Pass a short subject like
"WebSocket fan-out latency" or "GDPR data export" as `$ARGUMENTS`.
