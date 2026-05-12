---
name: dev-speckit-methodology
description: Apply SpecKit/BMAD (Build, Measure, Analyze, Decide) Spec-Driven Development methodology. Use when creating features using executable specifications, following PRIES workflow phases (Constitution, Specify, Refine, Plan, Tasks, Implement), or when user mentions SpecKit, SDD, spec-driven development, or BMAD workflow. Covers requirement specifications, implementation planning, task breakdown, and test-driven execution.
---

# SpecKit Spec-Driven Development Methodology

## Overview

SpecKit implements **Spec-Driven Development (SDD)** - specifications become executable artifacts that generate code, not just guides. This inverts traditional development: specs are the source of truth, code is their expression.

**Key Principle:** Specifications define *what* and *why*. Plans define *how*. Tasks define *when* and *by whom*. Implementation executes the tasks.

## Quick Start

### Prerequisites Check

Before starting any SDD workflow:

```bash
# Verify SpecKit CLI is installed
specify version

# Check if project is initialized
ls .specify/

# Verify integration files exist
ls .claude/commands/speckit.* || ls .gemini/commands/speckit.*
```

If missing, run: `specify init --here --integration <agent>`

### Which Phase Am I In?

```
Do you have .specify/memory/constitution.md?
├─ NO → Phase 0: Run /speckit.constitution
└─ YES
   └─ Do you have a spec.md for this feature?
      ├─ NO → Phase 1: Run /speckit.specify
      └─ YES
         └─ Does spec have [NEEDS CLARIFICATION] markers?
            ├─ YES → Phase 2: Run /speckit.clarify
            └─ NO
               └─ Do you have plan.md?
                  ├─ NO → Phase 3: Run /speckit.plan
                  └─ YES
                     └─ Do you have tasks.md?
                        ├─ NO → Phase 4: Run /speckit.tasks
                        └─ YES → Phase 5: Run /speckit.implement
```

## The PRIES Workflow (5 Core Phases)

### Phase 0: Constitution (Project Principles)

**Purpose:** Define immutable architectural and quality principles

**Command:** `/speckit.constitution`

**Creates:** `.specify/memory/constitution.md`

**Key principles to define:**
- Library-first vs monolith
- Testing approach (TDD, integration-first, contract-first)
- Simplicity gates (max project count, anti-abstraction rules)
- Tech stack constraints
- Security and compliance requirements

**Example:**
```
/speckit.constitution This project follows Library-First principle - all features start as standalone libraries. Strict TDD required. Maximum 3 projects per feature. Integration tests over unit tests. No framework wrapping - use features directly.
```

**Quality checklist:**
- [ ] Principles are immutable, not preferences
- [ ] Gates are enforceable (pass/fail, no gray area)
- [ ] Tech constraints match org reality
- [ ] Test-first mandate is explicit

---

### Phase 1: Specify (Requirements Definition)

**Purpose:** Define WHAT to build and WHY, without implementation details

**Command:** `/speckit.specify`

**Creates:**
- Feature branch (e.g., `001-feature-name`)
- `specs/001-feature-name/spec.md` with user stories, acceptance criteria, success metrics

**Critical rules:**
- ✅ Focus on user needs, business value, desired outcomes
- ❌ NO tech stack mentions
- ❌ NO "how to implement" details
- ❌ NO API designs yet

**Example:**
```
/speckit.specify Build a photo album organizer. Users can create albums grouped by date. Albums displayed in grid. Drag-and-drop to reorder albums. Within albums, photos shown in tile interface. No nested albums. All metadata stored locally.
```

**After spec generation:**
1. Review for `[NEEDS CLARIFICATION]` markers
2. Check that spec focuses on business value, not implementation
3. Verify acceptance criteria are testable

**Quality checklist:**
- [ ] NO `[NEEDS CLARIFICATION]` markers remain
- [ ] NO tech stack mentioned
- [ ] User stories trace to acceptance criteria
- [ ] Success metrics are measurable
- [ ] Out-of-scope is explicit

---

### Phase 2: Refine/Clarify (Specification Quality)

**Purpose:** Resolve ambiguities, validate completeness, fill gaps

**Command:** `/speckit.clarify`

**What it does:**
- Structured Q&A to identify underspecified areas
- Records clarifications in spec
- Validates Review & Acceptance Checklist

**Optional validation command:** `/speckit.checklist`

**Critical checkpoint:** Spec must have NO `[NEEDS CLARIFICATION]` markers before planning

**Example:**
```
/speckit.clarify Focus on data persistence, performance requirements, and edge cases for empty albums
```

---

### Phase 3: Plan (Implementation Strategy)

**Purpose:** Define HOW to implement - tech stack, architecture, dependencies

**Command:** `/speckit.plan`

**Creates:**
- `plan.md` - high-level implementation roadmap
- `research.md` - tech stack validation
- `data-model.md` - entities and relationships
- `contracts/` - API specs, interfaces
- `quickstart.md` - validation scenarios

**Now you specify:**
- Tech stack (frameworks, libraries, languages)
- Architecture patterns (microservices, monolith, serverless)
- Database choices
- API design (REST, GraphQL, gRPC)
- Deployment strategy

**Example:**
```
/speckit.plan Use .NET Aspire with Postgres database. Frontend: Blazor server with drag-drop, real-time updates via SignalR. REST APIs: projects, tasks, notifications. Keep to 3 projects maximum per constitution.
```

**Phase Gates from Constitution:**

Before proceeding, the plan must pass constitutional gates:

1. **Simplicity Gate** - Using ≤3 projects? No future-proofing?
2. **Anti-Abstraction Gate** - Using framework directly (not wrapped)? Single model representation?
3. **Integration-First Gate** - Contracts defined? Contract tests planned?

**Quality checklist:**
- [ ] Passes all constitutional gates
- [ ] Tech choices have documented rationale
- [ ] Data model covers all entities from spec
- [ ] Contracts exist for all integrations
- [ ] Test-first ordering is preserved

---

### Phase 4: Task Breakdown

**Purpose:** Convert plan into ordered, executable tasks

**Command:** `/speckit.tasks`

**Creates:** `specs/001-feature-name/tasks.md`

**Task structure:**
- Grouped by user story
- Ordered by dependencies (models → services → endpoints → UI)
- Marked `[P]` for parallel-safe tasks
- File paths specified for each task
- Test-first ordering (tests before implementation)
- Checkpoint validations per story

**Optional pre-implementation analysis:** `/speckit.analyze`

**Quality checklist:**
- [ ] Dependencies are correctly ordered
- [ ] Parallel markers `[P]` are accurate
- [ ] Tests precede implementation
- [ ] Checkpoints exist between stories
- [ ] File paths are specified

---

### Phase 5: Implementation

**Purpose:** Execute all tasks, build the feature

**Command:** `/speckit.implement`

**What it does:**
- Validates prerequisites (constitution, spec, plan, tasks)
- Executes tasks in dependency order
- Respects parallel execution markers
- Follows TDD approach from plan
- Provides progress updates

**Critical rules:**
- ⚠️ Will run local CLI commands (dotnet, npm, docker, etc.)
- ⚠️ Ensure required tools are installed first
- ⚠️ Tests must exist before implementation
- ⚠️ Review browser console for errors not visible in CLI logs

**During implementation:**
- Agent will mark tasks in_progress → completed
- Stop immediately if blocked - don't guess or work around
- Copy runtime errors (browser console) back to agent for fixes

**Quality checklist:**
- [ ] All tasks marked completed
- [ ] Tests pass (run them)
- [ ] Application runs without errors
- [ ] Acceptance criteria validated
- [ ] Ready for merge/PR

---

## Common Patterns

For detailed workflow patterns, see [references/patterns.md](references/patterns.md):
- Adding a feature to existing project
- Parallel exploration (same spec, different stacks)
- Brownfield modernization
- Handling implementation blockers

## Extensions and Workflows

### Community Extensions (Optional Enhancements)

Extensions add capabilities beyond core SDD. Popular categories:

**Process Orchestration:**
- `maqa` - Multi-agent parallel implementation
- `conduct` - Sub-agent delegation
- `fleet` - Full lifecycle orchestration

**Quality Gates:**
- `verify` - Post-implementation validation
- `review` - Comprehensive code review
- `security-review` - Security audits

**Integration:**
- `jira` - Sync to Jira boards
- `github-issues` - Bidirectional issue sync
- `confluence` - Export specs to Confluence

**Search/Install:**
```bash
specify extension search <keyword>
specify extension add <extension-name>
specify extension list
```

### Workflows (Automated Chains)

Workflows automate multi-step SDD sequences with gates:

```bash
# Run full SDD cycle with review gates
specify workflow run speckit \
  -i spec="Build user authentication with OAuth" \
  -i scope=full

# Resume after gate approval
specify workflow resume <run_id>
```

### Presets (Customization)

Presets override templates and commands without forking:

**Use cases:**
- Enforce organizational standards
- Localize to different languages
- Add compliance requirements (HIPAA, SOC2)
- Adapt terminology (Agile, Kanban, JTBD, DDD)

```bash
specify preset search compliance
specify preset add healthcare-compliance
specify preset list
```

## Integration with Git

SpecKit uses git branches for feature isolation:

**Branch naming:** `NNN-feature-name` (e.g., `001-photo-albums`)

**Git workflow:**
```bash
# SpecKit creates branch automatically during /speckit.specify
git status  # Verify you're on feature branch

# During work
git add -A && git commit -m "Implement user story 1"

# After implementation complete
git push origin 001-photo-albums
gh pr create  # Create PR with spec/plan context
```

**Context detection:** SpecKit commands auto-detect active feature from current branch

## Troubleshooting

See [references/troubleshooting.md](references/troubleshooting.md) for solutions to:
- "Command not found: specify"
- "No .specify/ directory found"
- "Constitution not found"
- "Spec has [NEEDS CLARIFICATION] markers"
- "Plan violates constitutional gates"
- "Tasks out of order / missing dependencies"

## Anti-Patterns (What NOT to Do)

❌ **Skip constitution** - Leads to inconsistent decisions across features

❌ **Put tech stack in spec** - Locks spec to implementation, prevents parallel exploration

❌ **Skip clarification** - Results in rework during planning/implementation

❌ **Bypass constitutional gates** - Accumulates technical debt

❌ **Implement before tests** - Violates TDD principle, reduces quality

❌ **Continue when blocked** - Guessing causes deeper problems downstream

❌ **One giant commit** - Use checkpoints per user story instead

## Success Criteria

A feature is complete when:

1. ✅ All artifacts exist (constitution, spec, plan, tasks)
2. ✅ Implementation passes all tests
3. ✅ Acceptance criteria validated
4. ✅ Constitutional principles honored
5. ✅ Feature branch merged or PR created

## Additional References

- [Workflow Patterns](references/patterns.md) - Common implementation patterns
- [Troubleshooting Guide](references/troubleshooting.md) - Solutions to common issues
- [Artifacts Reference](references/artifacts.md) - Complete artifact catalog

**Official Docs:** https://github.github.io/spec-kit/

**Core Workflow:** https://github.com/github/spec-kit/blob/main/spec-driven.md

**Extensions Catalog:** https://speckit-community.github.io/extensions/
