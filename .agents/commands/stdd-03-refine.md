---
description: "Stage 3: Technical Refinement"
agent: daniels-workflow-orchestrator
subtask: true
return:
  # 1. Architect drafts the delivery plan
  - /subtask {agent: daniels-architect-agent && as: draft_plan} Create delivery plan for "$ARGUMENTS" in @docs/tasks/ and update @docs/delivery_plan.md.
  
  # 2. Critical Thinking Red Teams the plan
  - /subtask {agent: daniels-critical-thinking-agent && as: audit_report} Critically review the plan in $RESULT[draft_plan]. Ensure tasks are 2-15 mins, sequential logic is sound, and every task has clear verification criteria.
  
  # 3. QA establishes the test-first safety net
  - /subtask {agent: daniels-qa-agent && as: test_suite} Based on user stories in $RESULT[draft_plan], create exhaustive e2e/integration tests in @tests/ covering all corner cases. Verify they fail.
  
  # 4. Orchestrator prepares the git environment
  - /subtask {agent: daniels-workflow-orchestrator} Determine git strategy (branching vs worktrees) for $RESULT[draft_plan] and prepare the workspace.
  
  # 5. Summary and approval gate
  - "Refinement for '$1' complete. Plan audited by Red Team, Git setup ready, and E2E tests created. Please review the plan in @docs/tasks/ and tests in @tests/. Reply with 'Approved' to start Stage 4 (Implementation)."
---
# Technical Refinement: $ARGUMENTS

Initiating the refinement sequence. I will delegate plan drafting to the Architect, validation to Critical Thinking, and test creation to QA.
