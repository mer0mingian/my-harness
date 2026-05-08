---
description: "Stage 4: Implementation"
agent: matd-orchestrator
subtask: true
return:
  # 1. QA establishes the test-first safety net (Isolated Task)
  - /subtask {agent: matd-qa && as: qa_tests} Create exhaustive e2e/integration tests in @tests/ covering all user stories for this feature. Confirm they fail.
  
  # 2. Dev implements the logic using TDD
  - /subtask {agent: matd-dev && loop: { max: 20, until: "all tests pass" } && as: implementation_results} Implement the feature tasks using TDD. Make the E2E tests pass without editing them.
  
  # 3. QA performs peer review of the solution
  - /subtask {agent: matd-qa && as: final_review} Review the implementation in $RESULT[implementation_results]. Verify behavioral correctness and code quality.
  
  # 4. Architect finalizes the PR
  - /subtask {agent: matd-architect && as: pr_details} Merge task solutions, update `learnings_and_decisions.md`, and create a Pull Request with a comprehensive summary.
  
  # 5. Final Gate
  - "Stage 4 (Implementation) is complete! The feature has been implemented, verified by QA, and a PR has been created: $RESULT[pr_details]. Reply with 'Done' to close the workflow."
---
# Implementation Phase

Initiating the execution sequence. I will coordinate the QA and Dev agents to ensure a test-driven implementation followed by a rigorous audit and PR creation.
