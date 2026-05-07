# Python Reusability Summary for Architectural Correction

**Date:** 2026-05-07  
**Purpose:** Answer key questions before starting architectural correction

---

## Question 1: Which Existing Scripts Can Be Reused?

### ✅ Keep as Helper Scripts (7 scripts - 45% of code)

**These scripts contain LLM-fragile logic that should remain in Python:**

| Script | Purpose | Lines | Why Python? |
|--------|---------|-------|-------------|
| **validate_red_state.py** | Enforce RED before implementation | ~350 | Complex pytest parsing, multi-condition state detection, failure code classification |
| **validate_green_state.py** | Verify GREEN after implementation | ~340 | Coverage metrics extraction, baseline comparison, regression detection |
| **parse_pytest_output.py** | Parse pytest into TestEvidence | ~260 | Regex-heavy, multi-pass parsing, handles edge cases in pytest output formats |
| **extract_acceptance_criteria.py** | Extract AC-N items from spec | ~120 | State machine for section detection, handles nested markdown, various formatting styles |
| **validate_feature_artifacts.py** | Validate evidence before commit | ~280 | Schema validation, timestamp ordering, structural checks across 5 artifact types |
| **run_integration_checks.py** | Execute ruff/mypy with timeout | ~180 | Subprocess with timeout, parallel execution, critical vs non-critical classification |
| **escalate_broken_tests.py** | Generate escalation report | ~140 | Deterministic mapping of failure codes to root causes and recommendations |

**Total: ~1,670 lines of robust validation logic**

### ✅ Keep as Libraries (lib/ - already correct location)

**These modules are already in the right place:**

| Library | Purpose | Keep As | Notes |
|---------|---------|---------|-------|
| **lib/test_runner.py** | Test execution utilities | Library | Core TDD validation - used by multiple scripts |
| **lib/parse_test_evidence.py** | Pytest output parsing | Library | Shared by validate_red and validate_green |
| **lib/artifact_paths.py** | Path resolution | Library | Used across all commands |
| **lib/evidence_validator.py** | Evidence chain validation | Library | Used by commit command and hooks |
| **lib/validate_artifacts.py** | Artifact structure validation | Library | Used by validate_feature_artifacts script |
| **lib/human_feedback.py** | Interactive prompts | Library | Used by execute command (interactive mode) |
| **lib/jira_local.py** | Local Jira state machine | Library | Used by commit command |

### ✅ Convert to Hook Handlers (3 hooks - 15% of code)

**These functions enforce constitutional requirements automatically:**

| Hook Handler | Purpose | Trigger | Exit Codes |
|--------------|---------|---------|------------|
| **file_gate_enforcer.py** | Block non-test files during test step | PreToolUse: tool=="Write" && phase=="test" | 0=allow, 2=block |
| **tdd_sequence_enforcer.py** | Enforce RED before GREEN | PreToolUse: tool=="Write" && path.startsWith("src/") | Calls validate_red_state.py |
| **evidence_gate_enforcer.py** | Block commit without evidence | PreToolUse: tool=="Bash" && args.contains("git commit") | Calls validate_feature_artifacts.py |

**Total: ~810 lines of enforcement logic**

### ❌ Convert to Natural Language (40% of code)

**These functions orchestrate workflows and can be described in markdown:**

- File path resolution (simple candidate list)
- Config loading with defaults
- Agent context building (dictionary construction)
- Template rendering instructions
- Artifact path calculation
- Success/error message formatting
- Command-line argument parsing
- Exit code decisions (when to return 0/1/2)

**Total: ~2,160 lines become markdown instructions**

---

## Question 2: Good Split of Natural Language vs Script Support

### Recommended Architecture Pattern

```
                    MARKDOWN COMMAND
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
    ORCHESTRATION    VALIDATION        ENFORCEMENT
   (Natural Lang)    (Scripts)         (Hooks)
        │                 │                 │
        ├─ Find files     ├─ Parse pytest  ├─ Block non-test
        ├─ Load config    ├─ Detect state  ├─ Verify RED→GREEN
        ├─ Build context  ├─ Extract AC    ├─ Check evidence
        ├─ Invoke agent   ├─ Validate      └─ (Automatic)
        └─ Report status  └─ Classify         (Constitutional)
           (Described)       (Deterministic)
```

### Principle: "Fragile vs Fluent"

**Keep in Python (Scripts/Hooks) - "LLM-Fragile":**
- Regex parsing
- Multi-condition state machines
- Exit code interpretation from subprocess output
- Schema validation (YAML structure, required fields)
- Numerical calculations (coverage %, test counts)
- Timeout management
- Parallel execution coordination
- Failure code classification (TEST_BROKEN vs MISSING_BEHAVIOR)

**Convert to Natural Language (Markdown) - "LLM-Fluent":**
- File existence checks ("Check if X exists, if not try Y")
- Sequential workflows ("First do A, then B, then C")
- Agent invocation ("Delegate to @agent with context...")
- Template variable substitution ("Use template with feature_id=${id}")
- Simple conditionals ("If file exists, load it; otherwise use defaults")
- String formatting ("Build path: docs/features/${feature_id}.md")
- Success/error reporting ("Print: ✅ Success - artifact created at ${path}")

### Concrete Examples

#### Example 1: File Discovery

**Python (59 lines) → Markdown (12 lines)**

```markdown
## Step 1: Find Spec Artifact

Search for spec artifact in order:
1. `docs/features/${feature_id}.md`
2. `docs/specs/${feature_id}-spec.md`
3. `docs/specs/${feature_id}.md`
4. `.specify/specs/${feature_id}.md`

If none exist:
❌ Error: Spec artifact not found for feature: ${feature_id}
Exit code: 1
```

**Reduction:** 79%

#### Example 2: Agent Context Building

**Python (85 lines) → Markdown (25 lines)**

```markdown
## Step 3: Build Agent Context

Prepare context for @test-specialist:

**Context Variables:**
- feature_id: ${feature_id}
- spec_content: (full spec file content)
- acceptance_criteria: (extracted AC list from Step 2)
- test_patterns: ${test_framework.file_patterns}
- valid_failure_codes: ${test_framework.failure_codes.valid_red}

**Instructions for Agent:**
You are @test-specialist. Write failing tests (RED state) for:
[context continues...]
```

**Reduction:** 71%

#### Example 3: Test Validation (KEEP IN PYTHON)

**Python (350 lines) → Python helper script**

```bash
# In markdown command:
## Step 5: Validate RED State

Run validation helper:
```bash
python3 scripts/validate_red_state.py feat-123
```

Expected exit codes:
- 0: Valid RED state (tests failing correctly)
- 1: Invalid (tests passing - no work needed)
- 2: Broken (tests have syntax errors)

If exit code 0: Continue to artifact generation
If exit code 1: Report to user and exit
If exit code 2: Escalate with diagnostics
```

**No Reduction:** Too complex for LLM to implement reliably

### Quantified Split Recommendation

| Category | Lines | % of Total | Rationale |
|----------|-------|------------|-----------|
| **Helper Scripts** | 1,670 | 31% | Deterministic, complex parsing, subprocess handling |
| **Hook Handlers** | 810 | 15% | Constitutional enforcement, automatic triggers |
| **Natural Language** | 2,160 | 40% | High-level orchestration, file operations |
| **Library Code** | 760 | 14% | Shared utilities (keep as-is in lib/) |

**Total:** 5,400 lines

### Robustness Guarantees

**What Python Scripts Provide:**
1. ✅ Consistent pytest output parsing across Python 3.8-3.12
2. ✅ Accurate failure code classification (MISSING_BEHAVIOR vs TEST_BROKEN)
3. ✅ Precise state detection (RED vs GREEN vs BROKEN)
4. ✅ Schema validation (artifacts have required sections)
5. ✅ Timeout enforcement (integration checks don't hang)
6. ✅ Coverage metric extraction from pytest-cov output
7. ✅ Timestamp ordering validation (RED before GREEN)

**What Natural Language Handles:**
1. ✅ File path resolution (with clear fallback sequence)
2. ✅ Agent invocation with context
3. ✅ Template variable substitution
4. ✅ Success/error reporting
5. ✅ Workflow sequencing (Step 1 → Step 2 → Step 3)

**What Hooks Guarantee:**
1. ✅ File gate cannot be bypassed (PreToolUse blocks writes)
2. ✅ TDD sequence enforced (RED validated before implementation allowed)
3. ✅ Evidence required for commit (PreToolUse blocks git commit without artifacts)

---

## Practical Conversion Guidelines

### When to Use Each Approach

**Use Python Helper Script when:**
- Function has >3 conditional branches
- Parsing text with regex (especially pytest output)
- Detecting patterns in subprocess output
- Calculating metrics (percentages, counts)
- Validating schema/structure
- Handling timeouts or parallel execution

**Use Hook Handler when:**
- Requirement is constitutional (non-bypassable)
- Validation should be automatic (not explicit)
- Enforcement needed at lifecycle point (PreToolUse, PostToolUse)
- Binary allow/block decision required
- Should work even if LLM "forgets"

**Use Natural Language when:**
- Logic is sequential (first X, then Y, then Z)
- Conditionals are simple (if exists, load; else default)
- File operations are straightforward (read, write, copy)
- Agent invocation can be described
- Template rendering can be explained
- Success/error messages just need formatting

### Markdown Command Structure

```markdown
---
description: "Command description"
agent: specialist-agent-name
tools:
  - 'filesystem/read'
  - 'filesystem/write'
scripts:
  validate_red: scripts/validate_red_state.py
  validate_green: scripts/validate_green_state.py
  parse_pytest: scripts/parse_pytest_output.py
---

# Command Workflow

## Prerequisites
[Natural language checks]

## Step 1: [Natural Language]
[Orchestration logic described]

## Step 2: [Call Helper Script]
Execute validation:
```bash
python3 scripts/validate_red_state.py ${feature_id}
```

[Handle exit codes]

## Step 3: [Invoke Agent]
Delegate to @agent with context:
[Natural language delegation]

## Step 4: [Natural Language]
[More orchestration]

## Exit Codes
- 0: Success
- 1: Validation failure
- 2: Escalation required
```

---

## Migration Priority

### Phase 1: Essential Scripts (Day 1)
1. ✅ Create `scripts/validate_red_state.py` (most critical)
2. ✅ Create `scripts/validate_green_state.py` (TDD enforcement)
3. ✅ Create `scripts/parse_pytest_output.py` (dependency for above)
4. ✅ Create `hooks/handlers/file_gate_enforcer.py` (constitutional)

### Phase 2: Artifact Validation (Day 2)
5. ✅ Create `scripts/validate_feature_artifacts.py` (commit gate)
6. ✅ Create `hooks/handlers/evidence_gate_enforcer.py` (constitutional)
7. ✅ Create `scripts/extract_acceptance_criteria.py` (test quality)

### Phase 3: Integration & Polish (Day 3)
8. ✅ Create `scripts/run_integration_checks.py` (quality checks)
9. ✅ Create `scripts/escalate_broken_tests.py` (diagnostics)
10. ✅ Create `hooks/handlers/tdd_sequence_enforcer.py` (RED→GREEN)

### Phase 4: Markdown Commands (Day 4-5)
11. ✅ Convert `test.py` → `test.md` (using scripts from Phase 1)
12. ✅ Convert `implement.py` → `implement.md` (using scripts from Phase 1-2)
13. ✅ Convert `review.py` → `review.md` (lighter - mostly orchestration)
14. ✅ Convert `commit.py` → `commit.md` (using scripts from Phase 2)
15. ✅ Convert `execute.py` → `execute.md` (orchestration only)

---

## Expected Outcomes

### Before Correction (Current State)
- ❌ 2,615 lines in Python commands (incompatible with SpecKit)
- ❌ Complex orchestration logic in imperative code
- ❌ Constitutional requirements enforced by command logic (bypassable)
- ❌ Platform-specific (only works with Python interpreter)

### After Correction (Target State)
- ✅ 1,670 lines in helper scripts (deterministic validation)
- ✅ 810 lines in hook handlers (automatic constitutional enforcement)
- ✅ 2,160 lines as natural language instructions (clear orchestration)
- ✅ 760 lines in lib/ (shared utilities)
- ✅ Cross-platform compatible (markdown works with 15+ agents)
- ✅ Constitutional requirements enforced by hooks (non-bypassable)
- ✅ Maintainable (workflows in plain language, validation in code)

### Robustness Improvement
- ✅ LLM-fragile logic isolated in Python (robust)
- ✅ LLM-fluent logic in markdown (flexible)
- ✅ Constitutional enforcement automatic (reliable)
- ✅ Test validation is deterministic (not LLM-dependent)
- ✅ Evidence gates cannot be forgotten (hook-enforced)

---

## Answering Your Questions

### 1. Which existing scripts can be reused?

**All Python validation logic can and should be reused:**
- 7 helper scripts (~1,670 lines of deterministic validation)
- 3 hook handlers (~810 lines of constitutional enforcement)
- All lib/ modules remain unchanged (~760 lines)

**Total reuse: 3,240 lines (60% of Python code)**

The remaining 40% (orchestration logic) converts to natural language but the underlying patterns are preserved - just expressed differently.

### 2. What is a good split?

**Recommended Split:**
- **Natural Language (Markdown): 60%** - Orchestration, sequencing, agent invocation, file operations
- **Scripts (Python): 31%** - Deterministic validation, parsing, calculation, subprocess handling
- **Hooks (Python): 15%** - Automatic constitutional enforcement
- **Libraries (Python): 14%** - Shared utilities (already correct)

**Philosophy:** Natural language orchestrates, scripts validate, hooks enforce.

**Robustness Strategy:**
- Keep complexity where computers excel (Python)
- Keep flexibility where LLMs excel (natural language)
- Keep enforcement where reliability matters (hooks)

This split maximizes both maintainability (workflows in plain language) and reliability (critical validation in code).
