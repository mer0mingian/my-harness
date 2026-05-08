# Implementation Plan: Multi-Agent TDD Workflow

**Version:** 1.0  
**Date:** 2026-05-07  
**Status:** Planning  
**Target Repository:** harness-tooling (marketplace), harness-sandbox (runtime cleanup)

---

## Executive Summary

This plan delivers a dual-plugin TDD workflow system that extends PRIES steps 7-10 with multi-agent specialization and evidence-based quality gates. The system consists of:

1. **Claude Code Plugin** (`harness-agents`): 5 specialist agent definitions installed to `.claude/agents/`
2. **SpecKit Extension** (`harness-tdd-workflow`): Custom TDD workflow commands, artifact templates, and configuration

**Key Principles:**
- Independence from superpowers (no hard dependency)
- Configurable rigor (teams control artifact mandatory flags)
- Evidence-based completion (test outputs required, not assumptions)
- Constitutional compliance (non-bypassable safety gates)

**Delivery Model:** Vertical slices that each deliver working value to users.

---

## Vertical Slice Breakdown

### Slice 1: Foundation - Agent Definitions & Basic Runtime (3-4 hours)

**User Value:** Team can install specialist agents and spawn them with clear responsibilities.

**Deliverables:**
1. **harness-tooling/.claude-plugin/harness-agents/plugin.json**
   - Declares 5 agent definition files
   - Installs to `.claude/agents/` in workspace

2. **Agent Definition Files** (harness-tooling/.claude-plugin/harness-agents/):
   - `test-specialist.yml` — @test agent (test generation, RED state validation)
   - `dev-specialist.yml` — @make agent (implementation, GREEN state achievement)
   - `arch-specialist.yml` — @check agent (safety constraints, architectural review)
   - `review-specialist.yml` — @simplify agent (complexity reduction)
   - `qa-specialist.yml` — @qa agent (browser/CLI validation)

3. **Runtime Commands:**
   - `/agents.spawn <agent-name> <task-description>` — spawn specialist with context
   - `/agents.assign-task <agent-name> <task-file>` — route task to agent

**Acceptance Criteria:**
- `claude plugin install harness-agents` succeeds
- All 5 agent definitions appear in `.claude/agents/`
- `/agents.spawn test-specialist "Write login tests"` spawns @test agent
- Agent has access to PRIES context and TDD principles

**Dependencies:** None (foundation slice)

**Technical Notes:**
- Agent definitions use YAML frontmatter format
- Each agent has `role`, `capabilities`, `constraints` fields
- Failure codes defined per agent (e.g., @test: MISSING_BEHAVIOR, ASSERTION_MISMATCH)

---

### Slice 2: SpecKit Extension Structure & Configuration (2-3 hours)

**User Value:** Team can install TDD workflow extension and configure artifact behavior.

**Deliverables:**
1. **harness-tooling/.speckit-extensions/harness-tdd-workflow/extension.json**
   - Extension metadata (name, version, description)
   - Declares commands, templates, hooks

2. **Configuration Template:**
   - `harness-tooling/.speckit-extensions/harness-tdd-workflow/harness-tdd-config.yml.template`
   - Documents all configuration options with comments
   - Default values for artifact paths, mandatory flags, gates

3. **Workspace Integration:**
   - Extension creates `.specify/harness-tdd-config.yml` on install
   - Copies artifact templates to `.specify/templates/`

**Acceptance Criteria:**
- `specify extension add harness-tdd-workflow --from ../harness-tooling/.speckit-extensions/harness-tdd-workflow` succeeds
- Config file appears at `.specify/harness-tdd-config.yml`
- All 5 template files copied to `.specify/templates/`
- Team can customize artifact paths and mandatory flags

**Dependencies:** None (parallel with Slice 1)

**Technical Notes:**
- SpecKit extension API: commands declared in extension.json
- Templates use Jinja2-style placeholders: `{{feature_id}}`, `{{feature_name}}`
- Configuration schema validated on extension load

---

### Slice 3: Step 7 - Write Tests Workflow (4-5 hours)

**User Value:** @test agent writes failing tests with structured failure codes and file gate enforcement.

**Deliverables:**
1. **Command:** `/speckit.multi-agent.test <feature-id>`
   - Spawns @test agent with PRIES step 7 context
   - Enforces file gate (only test file patterns allowed)
   - Validates RED state with structured failure codes
   - Creates `docs/tests/test-design/{feature_id}-test-design.md`

2. **Test Design Artifact Template:**
   - Test strategy section (unit, integration, edge cases)
   - Acceptance criteria mapping (requirements → test cases)
   - RED state validation (failure codes documented)
   - Escalation paths (NOT_TESTABLE, BLOCKED)
   - Decision routing (next step: implement or escalate)

3. **File Gate Validation:**
   - Only allow file patterns: `tests/**/*.py`, `__tests__/**/*.ts`, `*_test.go`
   - Block implementation file changes in step 7
   - Report violations to user with clear error messages

4. **Failure Code Enforcement:**
   - Valid RED: MISSING_BEHAVIOR, ASSERTION_MISMATCH
   - Invalid (escalate): TEST_BROKEN, ENV_BROKEN
   - Structured output format for evidence capture

**Acceptance Criteria:**
- `/speckit.multi-agent.test feat-123` spawns @test agent
- Agent writes failing tests (RED state)
- Test design artifact created with all sections
- File gate blocks implementation files
- Failure codes validate correctly (MISSING_BEHAVIOR accepted, TEST_BROKEN escalates)
- Agent cannot proceed to step 8 without valid RED state

**Dependencies:** Slice 1 (agent definitions), Slice 2 (templates)

**Technical Notes:**
- File gate uses glob patterns from config
- Failure code detection via regex on test output
- Artifact validation: all template sections must be populated

---

### Slice 4: Step 8 - Implement Workflow (4-5 hours)

**User Value:** @make agent implements code to make tests pass with RED→GREEN evidence.

**Deliverables:**
1. **Command:** `/speckit.multi-agent.implement <feature-id>`
   - Reads test design artifact from step 7
   - Spawns @make agent with TDD entry validation
   - Enforces RED→GREEN cycle (tests must fail before implementation)
   - Creates `docs/implementation/{feature_id}-implementation-notes.md` (optional)

2. **TDD Entry Validation:**
   - Before implementation: run provided tests
   - Verify tests fail (RED state)
   - If tests pass → STOP (no implementation needed or tests broken)
   - Document RED state evidence (test output with failure codes)

3. **Implementation Notes Artifact Template:**
   - Implementation approach description
   - Files modified table
   - RED → GREEN evidence (test outputs before/after)
   - Refactoring description (structural improvements)
   - Integration validation (test suite, linting, type checking)

4. **GREEN State Achievement:**
   - All tests from step 7 must pass
   - No new test failures introduced
   - Integration checks pass (configurable: pytest, ruff, mypy, etc.)

**Acceptance Criteria:**
- `/speckit.multi-agent.implement feat-123` reads test design artifact
- Agent runs tests first, verifies RED state
- If tests already pass, agent halts with explanation
- Agent writes implementation code
- All tests pass (GREEN state)
- Implementation notes artifact created (if enabled)
- RED→GREEN evidence captured in artifact

**Dependencies:** Slice 3 (test design artifact must exist)

**Technical Notes:**
- TDD entry validation runs `pytest` (or configured test command)
- RED/GREEN evidence captured via test runner output
- Integration validation runs configured command list from config
- Refactoring phase runs after GREEN state achieved

---

### Slice 5: Step 9 - Review Workflow (Parallel Agents) (5-6 hours)

**User Value:** @check and @simplify agents run parallel reviews with conflict resolution.

**Deliverables:**
1. **Command:** `/speckit.multi-agent.review <feature-id>`
   - Spawns @check and @simplify agents in parallel
   - Each agent creates review artifact independently
   - Conflict resolution: @check safety constraints override @simplify suggestions
   - Creates `docs/reviews/arch-review/{feature_id}-arch-review.md` (mandatory)
   - Creates `docs/reviews/code-review/{feature_id}-code-review.md` (mandatory)

2. **Architecture Review (@check) Template:**
   - Safety constraints section (security, data integrity, backward compatibility)
   - Architectural concerns (design patterns, separation, dependencies)
   - Recommended actions (high/medium/optional priority)
   - Escalations (blockers, tech debt, risky refactors)
   - Verdict rationale (ACCEPTABLE | NEEDS_REVISION | BLOCKED)
   - Conflicts with @simplify (where safety wins)

3. **Code Review (@simplify) Template:**
   - Complexity analysis (cyclomatic, nesting, function length)
   - Code duplication percentage
   - Readability assessment (naming, structure, comments)
   - Recommendations (high/medium/optional priority)
   - Trade-offs documented (performance vs readability)
   - Conflicts with @check (where safety wins)
   - Verdict rationale (ACCEPTABLE | NEEDS_REVISION)

4. **Conflict Resolution Logic:**
   - If @check identifies safety constraint → @simplify defers
   - If @simplify suggests simplification that violates @check constraint → document conflict, keep @check decision
   - Conflicts documented in both review artifacts for transparency

5. **Review Cycle Management:**
   - Max 3 review cycles (configurable)
   - If reviews don't converge after 3 cycles → escalate to human
   - Track cycle count in artifacts

**Acceptance Criteria:**
- `/speckit.multi-agent.review feat-123` spawns both agents in parallel
- @check completes arch review with safety constraints validated
- @simplify completes code review with complexity analysis
- Conflicts documented in both artifacts
- Safety constraints non-bypassable (BLOCKED verdict halts workflow)
- Review cycles tracked, max 3 enforced

**Dependencies:** Slice 4 (implementation must be complete)

**Technical Notes:**
- Parallel agent execution via SpecKit's agent coordination API
- Conflict detection: cross-reference both review artifacts
- Verdict validation: BLOCKED from @check requires human escalation

---

### Slice 6: Step 10 - Commit & Workflow Summary (3-4 hours)

**User Value:** Orchestrator creates comprehensive workflow summary and commits artifacts.

**Deliverables:**
1. **Command:** `/speckit.multi-agent.commit <feature-id>`
   - Validates all mandatory artifacts exist
   - Creates workflow summary artifact
   - Commits all artifacts and code to feature branch
   - Updates spec lifecycle marker: `Status: Implemented`

2. **Workflow Summary Template:**
   - Run metadata (timestamps, duration, status)
   - TDD evidence (test counts, RED→GREEN cycles, coverage)
   - Review outcomes (@check and @simplify verdicts, cycles, conflicts)
   - Unresolved items (blockers, escalations, follow-ups)
   - Artifacts generated (table with paths and statuses)
   - PR information (URL, status, Linear link)
   - Manual overrides (documented with justification)
   - Metrics (cycle time, review cycles, coverage, complexity)
   - Lessons learned
   - Sign-off checklist

3. **Artifact Validation:**
   - Test design artifact exists (mandatory)
   - Arch review artifact exists (mandatory)
   - Code review artifact exists (mandatory)
   - Implementation notes artifact exists (if configured mandatory)
   - Workflow summary artifact created
   - All artifacts conform to templates

4. **Evidence Requirements:**
   - RED state evidence present (test outputs with failure codes)
   - GREEN state evidence present (test outputs with pass status)
   - Integration validation results present (linting, type checking, coverage)

**Acceptance Criteria:**
- `/speckit.multi-agent.commit feat-123` validates all mandatory artifacts
- Workflow summary created with all sections populated
- All artifacts committed to feature branch
- Spec lifecycle updated to `Status: Implemented`
- Evidence requirements validated (RED→GREEN proof exists)
- Command fails if mandatory artifacts missing

**Dependencies:** Slice 5 (reviews must be complete)

**Technical Notes:**
- Artifact validation via file existence checks and template schema validation
- Evidence validation via regex parsing of artifact content
- Git commit includes all artifacts: `git add docs/ && git commit -m "feat: [feature-id] workflow artifacts"`

---

### Slice 7: Grill-Me Integration (Interactive Planning) (3-4 hours)

**User Value:** Teams can use interactive planning mode with Matt Pocock's grill-me skill.

**Deliverables:**
1. **Command:** `/speckit.multi-agent.plan --mode=interactive`
   - Loads grill-me skill if available (optional dependency)
   - Falls back to standard planning if grill-me not installed
   - Creates plan artifact with TDD-specific sections

2. **Grill-Me Integration:**
   - Prompts user with clarifying questions about test scenarios
   - Explores edge cases interactively
   - Documents decisions in plan artifact
   - Links plan to spec for traceability

3. **Configuration:**
   - `planning.skill: "grill-me"` in harness-tdd-config.yml
   - `planning.interactive_by_default: true` enables by default
   - `planning.fallback_mode: "standard"` if grill-me unavailable

**Acceptance Criteria:**
- `/speckit.multi-agent.plan --mode=interactive` loads grill-me skill
- Interactive Q&A session runs for test scenarios
- Plan artifact created with decisions documented
- Fallback to standard planning if grill-me not found
- No hard dependency on grill-me (graceful degradation)

**Dependencies:** Slices 1-6 (workflow must be functional before adding planning enhancement)

**Technical Notes:**
- Grill-me skill loaded via skill discovery API
- Interactive mode uses stdin/stdout for user prompts
- Plan artifact format compatible with SpecKit's plan command

---

### Slice 8: Configuration & Customization (2-3 hours)

**User Value:** Teams can customize artifact behavior, gates, and templates.

**Deliverables:**
1. **Configuration Documentation:**
   - `harness-tooling/docs/TDD-WORKFLOW-CONFIG.md`
   - Explains all configuration options
   - Examples for common customization scenarios

2. **Artifact Customization:**
   - Toggle mandatory flags per artifact
   - Customize artifact paths (team structure)
   - Override templates with company-specific versions

3. **Gate Customization:**
   - Toggle auto vs manual gates
   - Configure max review cycles
   - Define custom failure codes

4. **Example Configurations:**
   - Minimal setup (only mandatory artifacts)
   - Full rigor setup (all artifacts mandatory, strict gates)
   - Corporate setup (custom templates, manual gates)

**Acceptance Criteria:**
- Configuration guide covers all options in harness-tdd-config.yml
- Teams can toggle implementation notes from optional to mandatory
- Teams can change artifact paths to match their directory structure
- Teams can swap default templates with custom versions
- All customizations validated on extension load (schema validation)

**Dependencies:** Slices 1-6 (base workflow must exist before customization)

**Technical Notes:**
- Configuration schema defined in JSON Schema format
- Validation runs on extension install and config file change
- Template discovery via file path resolution from config

---

### Slice 9: Cleanup - Remove PRIES Plugin & Merge Phase 5 (2-3 hours)

**User Value:** Clean up deprecated PRIES plugin and consolidate phase 5 work into main branch.

**Deliverables:**
1. **Remove PRIES Plugin:**
   - Delete `harness-tooling/.speckit-extensions/pries-workflow/`
   - Remove PRIES references from marketplace README
   - Archive PRIES plugin docs to `harness-tooling/archive/pries-plugin/`

2. **Merge Phase 5 Worktree:**
   - Review harness-sandbox phase 5 worktree changes
   - Merge completed parts into main branch
   - Resolve conflicts with updated documentation
   - Close phase 5 worktree

3. **Archive Decision Documentation:**
   - Document why PRIES plugin deprecated (superpowers dependency, rigidity)
   - Document migration path (PRIES → harness-tdd-workflow)
   - Preserve PRIES design decisions in ADR

**Acceptance Criteria:**
- PRIES plugin removed from harness-tooling marketplace
- PRIES docs archived with deprecation notice
- Phase 5 worktree merged into harness-sandbox main branch
- No conflicts in documentation after merge
- ADR documents PRIES deprecation rationale

**Dependencies:** Slices 1-8 (new workflow must be functional before removing old one)

**Technical Notes:**
- Git worktree removal: `git worktree remove phase5-pries-workflow`
- Archive structure: `harness-tooling/archive/pries-plugin/{extension.json,README.md,docs/}`

---

### Slice 10: Update Requirements, Tasks, Roadmap Docs (3-4 hours)

**User Value:** Documentation reflects new dual-plugin architecture instead of PRIES.

**Deliverables:**
1. **Technical-Requirements.md Updates:**
   - Remove PRIES-specific requirements
   - Add dual-plugin requirements (harness-agents + harness-tdd-workflow)
   - Update artifact requirements (5 artifacts instead of PRIES artifacts)
   - Update quality gate requirements (TDD, review, evidence-based)

2. **Task-List.md Updates:**
   - Replace PRIES tasks with dual-plugin installation tasks
   - Add agent definition tasks
   - Add SpecKit extension configuration tasks
   - Update testing tasks to reflect new workflow

3. **Roadmap.md Updates:**
   - Replace PRIES phases with dual-plugin phases
   - Update dependencies (multi-agent workflow depends on agent definitions)
   - Update success criteria (5 artifacts created, quality gates enforced)

**Acceptance Criteria:**
- Technical-Requirements.md no longer references PRIES
- All requirements trace to dual-plugin architecture
- Task-List.md includes tasks for both plugins
- Roadmap.md reflects new implementation phases
- All cross-references between docs updated

**Dependencies:** Slice 9 (PRIES must be removed first)

**Technical Notes:**
- Search/replace pattern: `PRIES` → `harness-tdd-workflow`
- Traceability maintained: REQ-ID references preserved
- Version bump: v1.0 → v2.0 for breaking change

---

### Slice 11: Remove Superpowers & Update Sandbox Docs (2-3 hours)

**User Value:** Sandbox documentation reflects independence from superpowers.

**Deliverables:**
1. **Remove Superpowers References:**
   - Audit harness-sandbox docs for superpowers mentions
   - Remove installation instructions for superpowers
   - Remove superpowers skill references
   - Document that TDD workflow is superpowers-independent

2. **Update Sandbox CLAUDE.md:**
   - Remove superpowers from common commands
   - Add dual-plugin installation instructions
   - Update workflow description (PRIES → harness-tdd-workflow)
   - Document agent definitions in `.claude/agents/`

3. **Update Sandbox README:**
   - Remove superpowers prerequisites
   - Add harness-agents and harness-tdd-workflow to marketplace integration section
   - Update quickstart to use dual-plugin workflow

**Acceptance Criteria:**
- No references to superpowers in harness-sandbox documentation
- CLAUDE.md documents dual-plugin architecture
- README reflects new marketplace integration
- Installation guide updated (superpowers removed, dual-plugin added)

**Dependencies:** Slices 1-8 (new workflow must be documented)

**Technical Notes:**
- Grep audit: `rg -i superpowers harness-sandbox/docs/`
- Cross-repo consistency: harness-tooling and harness-sandbox aligned

---

## Implementation Sequence

**Parallel Tracks:**
- Track A (Foundation): Slice 1 → Slice 3 → Slice 4 → Slice 5 → Slice 6
- Track B (Infrastructure): Slice 2 (can run parallel with Slice 1)
- Track C (Enhancement): Slice 7 (runs after Slice 6)
- Track D (Cleanup): Slice 9 → Slice 10 → Slice 11 (runs after Slice 8)
- Track E (Documentation): Slice 8 (runs after Slice 6)

**Critical Path:** Slice 1 → Slice 3 → Slice 4 → Slice 5 → Slice 6 (TDD workflow core)

**Total Estimated Effort:** 35-42 hours (single developer)

**Real Duration with Parallelization:** ~25-30 hours (2-3 developers)

---

## Success Criteria

Implementation is successful when:

1. **Both plugins installable:**
   - `claude plugin install harness-agents` works
   - `specify extension add harness-tdd-workflow` works

2. **Full workflow executes:**
   - `/speckit.multi-agent.test` → `/speckit.multi-agent.implement` → `/speckit.multi-agent.review` → `/speckit.multi-agent.commit`
   - All 5 artifacts created
   - Quality gates enforce (TDD, evidence, review)

3. **Configuration works:**
   - Teams can toggle artifact mandatory flags
   - Teams can customize artifact paths
   - Teams can override templates

4. **Clean migration:**
   - PRIES plugin removed
   - Phase 5 worktree merged
   - Documentation updated (no PRIES references, no superpowers references)

5. **Constitutional compliance:**
   - Non-bypassable gates enforced (TDD, evidence, safety)
   - Human authority preserved (manual overrides documented)

---

## Risk Mitigation

### High-Risk Areas

1. **SpecKit Extension API Compatibility:**
   - **Risk:** API may not support all features (parallel agents, conflict resolution)
   - **Mitigation:** Prototype Slice 5 early, fall back to sequential reviews if needed

2. **Agent Coordination:**
   - **Risk:** Parallel @check and @simplify agents may conflict in unexpected ways
   - **Mitigation:** Clear conflict resolution rules documented, test with real examples

3. **Evidence Capture:**
   - **Risk:** Test output parsing may fail for different frameworks (pytest, Jest, Go)
   - **Mitigation:** Configurable regex patterns, framework-specific output parsers

### Medium-Risk Areas

1. **Grill-Me Integration:**
   - **Risk:** Grill-me skill may not be available or compatible
   - **Mitigation:** Graceful degradation to standard planning

2. **Template Customization:**
   - **Risk:** Teams may break templates with invalid Jinja2 syntax
   - **Mitigation:** Template validation on load, clear error messages

---

## Rollback Plan

If implementation fails at any slice:

1. **Slices 1-2:** Uninstall plugins, no harm (foundation only)
2. **Slices 3-6:** Uninstall extension, fall back to manual TDD workflow
3. **Slices 7-8:** Disable features via config, core workflow still works
4. **Slices 9-11:** PRIES plugin remains in archive, can be restored

**Critical Rollback Trigger:** If quality gates cannot be enforced (bypass discovered), halt implementation and escalate.

---

## Next Steps After This Plan

1. **Review Plan with Team:**
   - Validate slice breakdown (user value per slice)
   - Confirm configuration approach (YAML schema, template system)
   - Approve constitutional principles (non-bypassable gates)

2. **Create Task List:**
   - Break each slice into granular tasks
   - Estimate effort per task
   - Identify task dependencies

3. **Create Roadmap:**
   - Map tasks to timeline
   - Identify parallel execution opportunities
   - Define milestones and deliverables

4. **Execute Slice 1:**
   - Implement agent definitions
   - Test agent spawning
   - Validate against acceptance criteria

---

## Related Documents

- [PRD-Multi-Agent-TDD-Workflow.md](PRD-Multi-Agent-TDD-Workflow.md) — Product requirements
- [CONSTITUTION-Multi-Agent-TDD.md](CONSTITUTION-Multi-Agent-TDD.md) — Constitutional principles
- [ARTIFACT-SUMMARY.md](ARTIFACT-SUMMARY.md) — Artifact details and configuration
- [Technical-Requirements.md](Technical-Requirements.md) — Current requirements (to be updated in Slice 10)
- [Task-List.md](Task-List.md) — Current tasks (to be updated in Slice 10)
- [Roadmap.md](Roadmap.md) — Current roadmap (to be updated in Slice 10)
