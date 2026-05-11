# Architectural Correction Plan: Python Commands → Markdown

**Status:** Ready to Execute  
**Effort:** 12.5 hours (4 phases)  
**Priority:** P0 - Blocking Phase 2 completion

---

## Problem

Current implementation uses Python scripts as commands (`test.py`, `implement.py`, `review.py`, `commit.py`, `execute.py`), which is incompatible with SpecKit extension architecture. Commands must be markdown files with YAML frontmatter.

**Impact:** Extension cannot be registered, incompatible with 15+ agent platforms, violates SpecKit specification.

---

## Solution

Convert commands to markdown format, move Python logic to helper scripts and hooks.

**Architecture Pattern:**
```
commands/          → Markdown orchestration (natural language)
scripts/           → Helper scripts (deterministic validation)
hooks/handlers/    → Constitutional enforcement (automatic)
lib/               → Shared utilities (unchanged)
```

---

## Execution Plan

### Phase 1: Core Validation Scripts (3 hours)

**Goal:** Create essential validation infrastructure

**Tasks:**
1. **Create `scripts/validate_red_state.py`** (1h)
   - Source: `lib/test_runner.py::validate_red_state()` + `commands/test.py::validate_red_state()`
   - Input: feature_id, project_root
   - Output: JSON with state, evidence, validation_passed
   - Exit: 0=valid RED, 1=invalid, 2=system error

2. **Create `scripts/validate_green_state.py`** (1h)
   - Source: `lib/test_runner.py::validate_green_state()` + coverage extraction
   - Input: feature_id, project_root, optional baseline_count
   - Output: JSON with state, evidence, coverage
   - Exit: 0=valid GREEN, 1=still failing, 2=broken

3. **Create `scripts/parse_pytest_output.py`** (0.5h)
   - Source: `lib/parse_test_evidence.py::parse_pytest_output()`
   - Standalone wrapper for pytest parsing
   - Input: pytest stdout (stdin or file)
   - Output: TestEvidence JSON

4. **Create `hooks/handlers/file_gate_enforcer.py`** (0.5h)
   - Source: `commands/test.py::validate_test_file_pattern()`
   - Hook: PreToolUse when tool=="Write"
   - Block non-test files during test phase
   - Exit: 0=allow, 2=block

**Deliverables:**
- 3 working helper scripts
- 1 working hook handler
- Test each script standalone

---

### Phase 2: Artifact Validation (2 hours)

**Goal:** Evidence and artifact validation for commit gate

**Tasks:**
1. **Create `scripts/validate_feature_artifacts.py`** (1h)
   - Source: `lib/validate_artifacts.py::validate_feature_artifacts()`
   - Validate all 5 artifacts exist with correct structure
   - Check RED→GREEN timestamp ordering
   - Output: Validation report JSON
   - Exit: 0=valid, 1=missing artifacts, 2=system error

2. **Create `scripts/extract_acceptance_criteria.py`** (0.5h)
   - Source: `commands/test.py::extract_acceptance_criteria()`
   - Regex-based AC extraction from spec markdown
   - Output: JSON array of AC strings
   - Exit: 0=success, 1=no AC found

3. **Create `hooks/handlers/evidence_gate_enforcer.py`** (0.5h)
   - Hook: PreToolUse when tool=="Bash" && args.contains("git commit")
   - Call validate_feature_artifacts.py
   - Block commit if validation fails
   - Exit: 0=allow, 2=block

**Deliverables:**
- 2 working helper scripts
- 1 working hook handler
- Commit gate functional

---

### Phase 3: Supporting Scripts (1.5 hours)

**Goal:** Integration checks and diagnostics

**Tasks:**
1. **Create `scripts/run_integration_checks.py`** (0.5h)
   - Source: `commands/implement.py::run_integration_checks()`
   - Execute ruff, mypy, etc. with 60s timeout
   - Output: JSON array of check results
   - Exit: 0=all passed, 1=non-critical failed, 2=critical failed

2. **Create `scripts/escalate_broken_tests.py`** (0.5h)
   - Source: `commands/test.py::escalate_broken_tests()` + diagnosis functions
   - Generate escalation report for BROKEN tests
   - Map failure codes to root causes
   - Output: Escalation report JSON

3. **Create `hooks/handlers/tdd_sequence_enforcer.py`** (0.5h)
   - Hook: PreToolUse when tool=="Write" && path.startsWith("src/")
   - Call validate_red_state.py before allowing implementation
   - Enforce RED before GREEN constitutional requirement
   - Exit: 0=allow (RED validated), 2=block (not RED)

**Deliverables:**
- 2 working helper scripts
- 1 working hook handler
- TDD sequence enforcement working

---

### Phase 4: Convert Commands (6 hours)

**Goal:** Convert Python commands to markdown format

**Tasks:**

#### 4.1 Convert `commands/test.md` (1.5h)
- Structure: 6 steps (Prerequisites → Find Spec → Parse AC → Invoke Agent → Validate RED → Generate Artifact)
- Calls: extract_acceptance_criteria.py, validate_red_state.py, escalate_broken_tests.py
- Agent: test-specialist
- Exit codes: 0=success, 1=spec not found/tests passing, 2=tests broken

#### 4.2 Convert `commands/implement.md` (1.5h)
- Structure: Two-phase (RED validation → GREEN validation with --validate-green flag)
- Calls: validate_red_state.py, validate_green_state.py, run_integration_checks.py
- Agent: dev-specialist
- Exit codes: 0=success, 1=validation failed, 2=template missing

#### 4.3 Convert `commands/review.md` (1h)
- Structure: 4 steps (Find Impl Notes → Prepare Context → Generate Artifacts)
- Calls: No scripts (pure orchestration)
- Agents: check, simplify (parallel - described, not executed)
- Exit codes: 0=success, 1=impl notes not found, 2=template missing

#### 4.4 Convert `commands/commit.md` (1h)
- Structure: 3 steps (Validate Artifacts → Generate Workflow Summary → Exit)
- Calls: validate_feature_artifacts.py
- No agent (orchestrator only)
- Exit codes: 0=success, 1=missing artifacts, 2=template missing

#### 4.5 Convert `commands/execute.md` (1h)
- Structure: Sequential orchestration (test → implement → review → commit)
- Calls: Invokes other commands via subprocess
- Handles interactive mode with human_feedback.py
- Exit codes: 0=completed, 1=validation failed, 2=escalation required

**Deliverables:**
- 5 markdown commands
- All using helper scripts and hooks
- Extension manifest updated

---

## Markdown Command Template

```markdown
---
description: "Brief command description"
agent: specialist-agent-name              # Optional
tools:                                     # Optional MCP tools
  - 'filesystem/read'
  - 'filesystem/write'
scripts:                                   # Optional helper references
  validate_red: scripts/validate_red_state.py
  validate_green: scripts/validate_green_state.py
---

# Command Title

## Prerequisites
- Requirement 1
- Requirement 2

## User Input
$ARGUMENTS

## Step 1: [Natural Language Description]

[Orchestration instructions]

Search for file in order:
1. Check `path/to/file1.md`
2. Check `path/to/file2.md`

If not found:
❌ Error: File not found
Exit with code 1

## Step 2: [Call Helper Script]

Execute validation:
```bash
python3 scripts/validate_red_state.py ${feature_id}
```

Expected exit codes:
- 0: Valid RED state → Continue
- 1: Tests passing → Report and exit
- 2: Tests broken → Escalate

Handle each exit code appropriately.

## Step 3: [Invoke Agent]

Delegate to @specialist-agent with context:

**Context:**
- Feature ID: ${feature_id}
- Spec path: ${spec_path}
- Instructions: [task description]

**Agent Task:**
1. Write failing tests
2. Follow file patterns
3. Respect file gate

## Exit Codes
- 0: Success
- 1: Validation failure
- 2: Escalation required
```

---

## Hook Configuration

**Create `hooks/config.yml`:**

```yaml
hooks:
  # File gate enforcement (test phase)
  PreToolUse:
    - name: file_gate_enforcer
      command: python3 hooks/handlers/file_gate_enforcer.py
      when: tool == "Write" && phase == "test"
      description: "Block non-test files during test step"
  
  # TDD sequence enforcement (implementation phase)
  PreToolUse:
    - name: tdd_sequence_enforcer
      command: python3 hooks/handlers/tdd_sequence_enforcer.py
      when: tool == "Write" && path.startsWith("src/")
      description: "Enforce RED before GREEN"
  
  # Evidence gate (commit phase)
  PreToolUse:
    - name: evidence_gate_enforcer
      command: python3 hooks/handlers/evidence_gate_enforcer.py
      when: tool == "Bash" && args.contains("git commit")
      description: "Validate evidence before commit"
```

---

## Extension Manifest Updates

**Update `extension.yml`:**

```yaml
provides:
  commands:
    - name: "speckit.matd.test"
      file: "commands/test.md"                    # Changed from .py
      description: "Generate failing tests"
    
    - name: "speckit.matd.implement"
      file: "commands/implement.md"               # Changed from .py
      description: "Implement feature with TDD"
    
    - name: "speckit.matd.review"
      file: "commands/review.md"                  # Changed from .py
      description: "Parallel architecture + code review"
    
    - name: "speckit.matd.commit"
      file: "commands/commit.md"                  # Changed from .py
      description: "Validate evidence and commit"
    
    - name: "speckit.matd.execute"
      file: "commands/execute.md"                 # Changed from .py
      description: "Execute full TDD workflow"
  
  hooks:
    - file: "hooks/config.yml"
      description: "TDD workflow enforcement hooks"
```

---

## Validation Checklist

### Per Phase:
- [ ] All scripts executable: `chmod +x scripts/*.py hooks/handlers/*.py`
- [ ] Scripts work standalone with test data
- [ ] Exit codes correct (0/1/2)
- [ ] JSON output valid and parseable
- [ ] Error messages clear and actionable

### After Phase 4:
- [ ] All markdown commands follow template
- [ ] YAML frontmatter valid
- [ ] $ARGUMENTS placeholder used correctly
- [ ] Scripts referenced in frontmatter exist
- [ ] Extension manifest updated
- [ ] Hooks configuration created
- [ ] Test each command: `/speckit.matd.test feat-test`
- [ ] Verify hooks trigger correctly

---

## Testing Strategy

### Unit Testing (Per Phase)
```bash
# Phase 1
python3 scripts/validate_red_state.py feat-test
python3 scripts/validate_green_state.py feat-test
python3 hooks/handlers/file_gate_enforcer.py < test_input.json

# Phase 2
python3 scripts/validate_feature_artifacts.py feat-test
python3 scripts/extract_acceptance_criteria.py < spec.md

# Phase 3
python3 scripts/run_integration_checks.py
python3 scripts/escalate_broken_tests.py < evidence.json
```

### Integration Testing (Phase 4)
```bash
# Create test workspace
mkdir -p test-workspace/docs/features
cd test-workspace

# Create test spec
cat > docs/features/feat-test-spec.md << 'EOF'
# Feature Spec
## Acceptance Criteria
- AC-1: User can login
- AC-2: Invalid credentials rejected
EOF

# Test command invocation
/speckit.matd.test feat-test
# Verify: test-design artifact created, RED state validated

# Test implement command
/speckit.matd.implement feat-test
# Verify: RED validation runs, impl notes created

# Test commit command
/speckit.matd.commit feat-test
# Verify: Evidence validation runs, workflow summary created
```

---

## Rollback Plan

If architectural correction fails:

1. **Preserve current Python commands:**
   ```bash
   cp commands/*.py commands/backup/
   ```

2. **Revert extension.yml:**
   - Change `.md` back to `.py` in command file references
   - Remove hooks section

3. **Keep helper scripts:**
   - Scripts in scripts/ and lib/ can coexist
   - No harm in having them available

4. **Document issues:**
   - Create issue in docs/issues/ with specific failure details
   - Include: what failed, error messages, environment info

---

## Success Criteria

**Phase 1-3 Complete:**
- [ ] 7 helper scripts working
- [ ] 3 hook handlers working
- [ ] All scripts return correct exit codes
- [ ] All scripts produce valid JSON output

**Phase 4 Complete:**
- [ ] 5 markdown commands created
- [ ] Extension manifest updated
- [ ] Hooks configuration created
- [ ] Commands follow SpecKit specification
- [ ] Test command works: `/speckit.matd.test feat-test`
- [ ] Hooks trigger automatically (file gate blocks non-test files)
- [ ] Evidence gate blocks commit without artifacts

**Overall Success:**
- [ ] Extension can be installed: `specify extension add .`
- [ ] Commands available as slash commands in Claude Code
- [ ] Constitutional requirements enforced automatically
- [ ] Cross-platform compatible (universal markdown format)
- [ ] Phase 2 can resume with correct architecture

---

## Timeline

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| Phase 1 | 3h | None - start immediately |
| Phase 2 | 2h | Phase 1 (needs validate_red_state.py) |
| Phase 3 | 1.5h | Phase 1-2 (needs validation scripts) |
| Phase 4 | 6h | Phase 1-3 (needs all scripts/hooks) |
| **Total** | **12.5h** | Sequential execution required |

**Execution Mode:** Use subagent-driven-development pattern
- Dispatch implementer subagent per task
- Spec review after each completion
- Code quality review after spec approval
- Mark complete and move to next

---

## Next Steps

1. **Commit current work:**
   ```bash
   git add docs/references/
   git commit -m "docs: add architectural correction analysis and plan"
   ```

2. **Begin Phase 1:**
   - Start with `scripts/validate_red_state.py`
   - Follow TDD: write tests first, then implementation
   - Verify standalone execution before moving to next script

3. **Track progress:**
   - Update TodoWrite with Phase 1-4 tasks
   - Mark scripts complete as they pass tests
   - Document any deviations or issues

Ready to execute.
