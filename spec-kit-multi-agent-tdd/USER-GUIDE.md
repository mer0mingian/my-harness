# SpecKit Multi-Agent TDD — User Guide

**Version:** 1.0  
**Date:** 2026-05-08  
**Status:** Production Ready

---

## Quick Start

The SpecKit Multi-Agent TDD extension adds AI-powered discovery, solution design, and test-driven development workflows to GitHub's SpecKit.

### Installation

1. **Install SpecKit** (if not already installed):
   ```bash
   claude plugin install github/spec-kit
   ```

2. **Install this extension**:
   ```bash
   # Extension auto-installs via workspace .harness.yml
   # Or manually: specify extension add harness-tdd-workflow --from /path/to/harness-tooling/spec-kit-multi-agent-tdd
   ```

3. **Initialize in your project**:
   ```bash
   specify init . --integration claude
   ```

4. **Configure** (optional):
   Copy `harness-tdd-config.yml.template` to `.specify/harness-tdd-config.yml` and customize agent assignments and artifact paths.

---

## Typical Workflow

### 1. Discovery Phase — Understand the Feature

**Create specification:**
```bash
/speckit.specify "Add user authentication with JWT tokens"
```

**Deep discovery** (optional, recommended for complex features):
```bash
/speckit.multi-agent.discover feat-001
```

This uses the "grill-me" technique — the AI asks you detailed questions to build shared understanding. Outputs:
- `feat-001-prd.md` — Product requirements document
- `technical-constitution.md` — Non-negotiable technical constraints

---

### 2. Solution Design Phase — Architect the Solution

```bash
/speckit.multi-agent.solution-design feat-001
```

This command:
- Compares 3 different solution approaches
- Generates an Architectural Decision Record (ADR) recommending one
- Creates detailed solution design with 4 architectural views (C4 diagrams, dependencies, interfaces, data design)

Outputs:
- `feat-001-adr.md` — Decision record with trade-off analysis
- `feat-001-solution-design.md` — Detailed architecture

---

### 3. Refinement Phase — Plan Implementation

**Generate implementation plan:**
```bash
/speckit.plan feat-001
```

**Break into tasks:**
```bash
/speckit.tasks feat-001
```

**Validate completeness:**
```bash
/speckit.analyze feat-001
```

Outputs:
- `feat-001-plan.md` — Technical implementation approach
- `feat-001-tasks.md` — Actionable task breakdown

---

### 4. Implementation Phase — Build with TDD

**Option A: Fully Automated Workflow (Recommended)**

```bash
/speckit.multi-agent.execute feat-001
```

This single command runs the complete TDD cycle:
1. **Test** — Generates failing tests (RED state)
2. **Implement** — Writes minimal code to make tests pass (GREEN state)
3. **Review** — Parallel architecture + code review by MATD agents
4. **Commit** — Validates evidence and creates git commit

**Option B: Step-by-Step Control**

```bash
# Step 1: Write failing tests
/speckit.multi-agent.test feat-001

# Step 2: Implement feature
/speckit.multi-agent.implement feat-001

# Step 3: Parallel reviews
/speckit.multi-agent.review feat-001

# Step 4: Validate and commit
/speckit.multi-agent.commit feat-001
```

---

## Command Reference

### Discovery Commands

| Command | Purpose | Outputs |
|---------|---------|---------|
| `/speckit.specify <description>` | Create feature specification | `feat-NNN-spec.md` |
| `/speckit.multi-agent.discover <feature-id>` | Deep requirements discovery via Q&A | `feat-NNN-prd.md`<br/>`technical-constitution.md` |

### Design Commands

| Command | Purpose | Outputs |
|---------|---------|---------|
| `/speckit.multi-agent.solution-design <feature-id>` | Compare approaches, generate architecture | `feat-NNN-adr.md`<br/>`feat-NNN-solution-design.md` |

### Planning Commands

| Command | Purpose | Outputs |
|---------|---------|---------|
| `/speckit.plan <feature-id>` | Generate implementation plan | `feat-NNN-plan.md` |
| `/speckit.tasks <feature-id>` | Break into tasks | `feat-NNN-tasks.md` |
| `/speckit.analyze <feature-id>` | Validate completeness | Analysis report |

### Implementation Commands

| Command | Arguments | Purpose | Outputs |
|---------|-----------|---------|---------|
| `/speckit.multi-agent.execute` | `<feature-id>` `[--mode=auto\|interactive]` | Full TDD workflow | All artifacts + commit |
| `/speckit.multi-agent.test` | `<feature-id>` | Write failing tests (RED) | `feat-NNN-test-design.md`<br/>`tests/test_*.py` |
| `/speckit.multi-agent.implement` | `<feature-id>` `[--skip-integration]` | Implement feature (GREEN) | `feat-NNN-impl-notes.md`<br/>`src/*.py` |
| `/speckit.multi-agent.review` | `<feature-id>` `[--max-cycles=N]` | Architecture + code review | `feat-NNN-arch-review.md`<br/>`feat-NNN-code-review.md` |
| `/speckit.multi-agent.commit` | `<feature-id>` | Validate and commit | `feat-NNN-workflow-summary.md`<br/>Git commit |

---

## Configuration

Edit `.specify/harness-tdd-config.yml` to customize:

### Agent Assignments

```yaml
agents:
  test_agent: "matd-qa"                # Agent for writing tests
  implementation_agent: "matd-dev"     # Agent for implementation
  qa_agent: "matd-qa"                  # Agent for acceptance testing
  arch_reviewer: "matd-architect"      # Agent for architecture review
  code_reviewer: "matd-critical-thinker" # Agent for code review
```

### Artifact Paths

```yaml
artifacts:
  root: "docs/features"  # Where to save all artifacts
  types:
    spec: "spec"
    test_design: "test-design"
    impl_notes: "impl-notes"
    arch_review: "arch-review"
    code_review: "code-review"
    workflow_summary: "workflow-summary"
```

### Quality Gates

```yaml
gates:
  default_mode: "auto"        # auto | manual
  manual_gates: []            # Gates requiring human approval
  max_review_cycles: 3        # Stop after N review iterations
  convergence_detection: true # Stop if reviews repeat same findings
```

---

## Understanding the Workflow

### RED → GREEN → REFACTOR

The extension enforces strict test-driven development:

1. **RED State** — Tests written first, must fail for the right reasons:
   - ✅ Valid failures: `MISSING_BEHAVIOR`, `ASSERTION_MISMATCH`, `NameError`, `AttributeError`
   - ❌ Invalid failures: `SyntaxError`, `ImportError`, `TEST_BROKEN`

2. **GREEN State** — Minimal implementation to make tests pass:
   - All tests must pass
   - Integration checks run (ruff, mypy)
   - Implementation notes document approach

3. **REFACTOR** — Parallel review ensures quality:
   - matd-architect agent checks correctness, safety constraints
   - Code reviewer checks complexity, duplication, readability
   - Conflicts resolved (safety wins)

### Evidence Chain

Every commit requires proof of TDD adherence:
- Test design artifact with RED state timestamp
- Implementation notes with GREEN state timestamp
- Review artifacts showing approval
- Workflow summary linking all evidence

---

## MATD Plugin Agents

The extension uses agents from the **matd** Claude Code plugin:

| Agent | Role | Responsibilities |
|-------|------|------------------|
| `matd-qa` | Test & QA Engineer | Creates E2E/Integration tests, acceptance validation |
| `matd-dev` | Implementation Engineer | Implements code using TDD within fixed file manifests |
| `matd-architect` | Solution Architect | Architecture review, solution design |
| `matd-critical-thinker` | Red Team Validator | Code review, analyzes for completeness/edge cases |
| `matd-specifier` | Requirements Specifier | Deep discovery, specification refinement, PRD generation |

**Installation:**
```bash
# Auto-installed via .harness.yml plugins section
# Or manually: claude plugin install /path/to/harness-tooling/.claude/.claude-plugin
```

**Agent definitions:** `harness-tooling/.claude/agents/matd-*.md`

---

## Troubleshooting

### "Agent not found" error

Ensure the matd plugin agents are installed:
```bash
ls harness-tooling/.claude/agents/matd-*.md
# Should show: matd-qa.md, matd-dev.md, matd-architect.md, matd-critical-thinker.md, matd-specifier.md
```

### "Artifact not found" error

Check your artifact root configuration:
```bash
cat .specify/harness-tdd-config.yml | grep "root:"
```

Artifacts must exist before running implementation commands:
- `/speckit.multi-agent.test` requires `feat-NNN-spec.md`
- `/speckit.multi-agent.implement` requires `feat-NNN-test-design.md` + RED state
- `/speckit.multi-agent.review` requires GREEN state
- `/speckit.multi-agent.commit` requires review artifacts

### Review cycle limit reached

If `/speckit.multi-agent.review` stops at max cycles:
1. Check `feat-NNN-arch-review.md` and `feat-NNN-code-review.md` for findings
2. Address the issues manually
3. Increase `max_review_cycles` in config if needed

---

## Best Practices

### 1. Use Discovery for Complex Features

For features with unclear requirements, always run `/speckit.multi-agent.discover` first. The grill-me questioning reveals assumptions and edge cases early.

### 2. Keep Feature Scope Small

SpecKit works best with small, focused features. If `/speckit.multi-agent.execute` takes >30 minutes, the feature is too large — break it down.

### 3. Trust the RED State Validation

Don't bypass RED state checks. If tests fail for the wrong reasons (`SyntaxError`, `ImportError`), fix them before implementing.

### 4. Review the Solution Design

After `/speckit.multi-agent.solution-design`, read the ADR before coding. The AI may propose a simpler approach than you initially imagined.

### 5. Use Interactive Mode for Learning

```bash
/speckit.multi-agent.execute feat-001 --mode=interactive
```

Interactive mode pauses between steps, letting you review artifacts and approve next actions. Great for learning the workflow.

---

## Advanced Usage

### Skip Integration Checks (Use Sparingly)

```bash
/speckit.multi-agent.implement feat-001 --skip-integration
```

Skips ruff/mypy checks. Useful for prototyping, but don't commit without running them.

### Manual Review Gates

Edit `.specify/harness-tdd-config.yml`:
```yaml
gates:
  default_mode: "manual"
  manual_gates: ["arch_review", "code_review"]
```

Now reviews require human approval before proceeding.

### Custom Test Patterns

For non-Python projects, configure test file patterns:
```yaml
test_framework:
  type: "pytest"  # Currently only pytest supported
  file_patterns:
    - "tests/**/*.py"
    - "spec/**/*_spec.rb"  # Add custom patterns
```

---

## What's Next?

After completing implementation:

1. **Verify** the workflow summary:
   ```bash
   cat docs/features/feat-001-workflow-summary.md
   ```

2. **Review** the git commit:
   ```bash
   git log -1 --stat
   ```

3. **Test** the feature manually (TDD validates code, not UX)

4. **Create PR** using the workflow summary as description

---

## Getting Help

- **Full command reference**: See [docs/references/COMMANDS-REFERENCE.md](docs/references/COMMANDS-REFERENCE.md)
- **Configuration schema**: See [config-schema.json](config-schema.json)
- **Agent definitions**: See `harness-tooling/.claude/agents/matd-*.md`
- **Technical requirements**: See archived planning docs in `docs/speckit-tdd/archive/`

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-05-08 | Initial release — Phases 1-4 complete |
