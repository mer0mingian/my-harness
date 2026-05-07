# Python Code Reusability Analysis

**Analyzed:** 2026-05-07  
**Total LOC:** ~5,400 lines (commands: 2,615 lines | lib: 2,809 lines)

## Executive Summary

**Recommended Split:**
- **Helper Scripts: 45%** (~2,430 lines) - Deterministic validation, test parsing, subprocess execution
- **Hook Handlers: 15%** (~810 lines) - File gate enforcement, constitutional requirements
- **Natural Language: 40%** (~2,160 lines) - Orchestration, file operations, agent invocation

**Key Insight:** The current Python implementation contains significant orchestration logic (artifact path resolution, agent context building, file operations) that can be naturally expressed in markdown instructions. The most valuable Python code is the deterministic validation and parsing logic (test evidence parsing, RED/GREEN state validation, file pattern matching) which LLMs struggle to implement reliably. By extracting this logic into standalone helper scripts and hooks, we create a more maintainable architecture where markdown orchestrates workflow and Python enforces correctness.

**Philosophy:** Keep LLM-fragile logic (regex parsing, exit code interpretation, schema validation) in Python; convert high-level orchestration (file discovery, agent invocation, template rendering) to natural language; use hooks to enforce non-negotiable constitutional requirements automatically.

---

## File-by-File Analysis

### commands/test.py (847 lines)

#### `find_spec_artifact(feature_id, project_root)` - NATURAL LANGUAGE
**Lines:** 82-115  
**Purpose:** Search candidate paths for spec artifact  
**Why Natural Language:** Simple file existence checks with hardcoded paths  
**Conversion:**
```markdown
## Step 1: Find Spec Artifact

Search for spec artifact in order:
1. Check `docs/features/${feature_id}.md`
2. Check `docs/specs/${feature_id}-spec.md`
3. Check `docs/specs/${feature_id}.md`
4. Check `.specify/specs/${feature_id}.md`

If none exist:
❌ Error: Spec artifact not found for feature: ${feature_id}
```

#### `load_config(project_root)` - NATURAL LANGUAGE
**Lines:** 118-147  
**Purpose:** Load YAML config or return defaults  
**Why Natural Language:** Simple file read with fallback to defaults  
**Conversion:**
```markdown
## Load Configuration

Check if `.specify/harness-tdd-config.yml` exists:
- If exists: Load YAML configuration
- If not exists: Use default configuration (from template)
```

#### `get_artifact_path(feature_id, config, project_root)` - NATURAL LANGUAGE
**Lines:** 150-186  
**Purpose:** Resolve output path from config template  
**Why Natural Language:** String substitution with mkdir  
**Conversion:**
```markdown
## Determine Output Path

From config, read `artifacts.test_design.path` template:
- Default: `docs/tests/test-design/{feature_id}-test-design.md`
- Substitute variables: `{feature_id}`, `{timestamp}`
- Create parent directory if needed
```

#### `extract_acceptance_criteria(spec_content)` - HELPER SCRIPT
**Lines:** 189-224  
**Purpose:** Parse AC-N items from markdown with flexible formatting  
**Why Helper:** Complex regex patterns, state machine for section detection  
**New Location:** `scripts/extract_acceptance_criteria.py`  
**Called From:** commands/test.md Step 2 - Parse Spec Content

**Rationale:** This involves multi-line state tracking, regex pattern matching for various formats (bold, bullets, indentation), and heading level detection. LLMs would struggle to implement this reliably, especially the edge cases (nested sections, different markdown styles).

#### `validate_test_file_pattern(file_path, config)` - HOOK HANDLER
**Lines:** 227-274  
**Purpose:** Enforce file gate - only test files during test step  
**Why Hook:** Constitutional requirement, automatic enforcement  
**New Location:** `hooks/handlers/file_gate_enforcer.py`  
**Triggered By:** PreToolUse when tool=="Write" && phase=="test"

**Logic:**
```python
if phase == "test" and not matches_test_pattern(file_path):
    sys.exit(2)  # Block - constitutional violation
```

#### `build_agent_context(feature_id, spec_content, config)` - NATURAL LANGUAGE
**Lines:** 277-301  
**Purpose:** Build dictionary with context for @test-specialist  
**Why Natural Language:** Simple dict construction, no complex logic  
**Conversion:**
```markdown
## Build Agent Context

Prepare context for @test-specialist:
- Feature ID: ${feature_id}
- Spec content: (full spec file)
- Acceptance criteria: (extracted list)
- Test patterns: ${test_framework.file_patterns}
- Valid failure codes: ${test_framework.failure_codes.valid_red}
- Instructions: "Write failing tests (RED state) for all acceptance criteria..."
```

#### `spawn_test_agent(...)` - NATURAL LANGUAGE
**Lines:** 304-399  
**Purpose:** Write temp file with agent prompt, print invocation instructions  
**Why Natural Language:** Straightforward file write and console output  
**Conversion:**
```markdown
## Step 4: Invoke @test-specialist Agent

Create temporary context file: `/tmp/test-agent-context-${feature_id}.txt`

Content:
```
You are @test-specialist writing tests for feature: ${feature_id}

SPEC CONTENT:
${spec_content}

TASK:
1. Write failing tests (RED state) for all acceptance criteria
2. Use test patterns from config
3. Tests MUST fail initially (MISSING_BEHAVIOR or ASSERTION_MISMATCH)
...
```

Print instructions:
- Feature ID: ${feature_id}
- Context file: ${context_file}
- Next step: Invoke agent with context
```

#### `generate_test_design_artifact(...)` - NATURAL LANGUAGE
**Lines:** 402-464  
**Purpose:** Render Jinja2 template with variables  
**Why Natural Language:** Template rendering can be described, not scripted  
**Conversion:**
```markdown
## Step 5: Generate Test Design Artifact

Use template: `templates/test-design-template.md`

Variables:
- feature_id: ${feature_id}
- feature_name: ${feature_name}
- timestamp: ${timestamp}
- status: "draft"
- bypass_info: ${bypass_info} (if file gate bypassed)
- evidence: ${evidence} (if tests run)
- valid_red: ${valid_red} (if validation performed)

Output: ${output_path}
```

#### `detect_test_failures(project_root, config)` - HELPER SCRIPT
**Lines:** 467-515  
**Purpose:** Run pytest, parse output with parse_test_evidence library  
**Why Helper:** Subprocess execution with complex output parsing  
**New Location:** `scripts/detect_test_failures.py`  
**Called From:** commands/test.md Step 5 - Validate RED State

**Input:** Project root, config with test patterns  
**Output:** JSON with TestEvidence structure  
**Exit Codes:** 0=success, 1=pytest failed, 2=parsing error

#### `validate_red_state(evidence)` - HELPER SCRIPT
**Lines:** 518-549  
**Purpose:** Validate tests in valid RED state (not GREEN or BROKEN)  
**Why Helper:** Precise failure code detection, multi-condition logic  
**New Location:** `scripts/validate_red_state.py`  
**Called From:** commands/test.md Step 5 - Validate RED State

**Input:** TestEvidence JSON  
**Output:** JSON with `{is_valid: bool, reason: string}`  
**Logic:** GREEN=all passing, BROKEN=TEST_BROKEN/ENV_BROKEN, RED=MISSING_BEHAVIOR/ASSERTION_MISMATCH

#### `diagnose_root_cause(result)` + `recommend_action(result)` - HELPER SCRIPT
**Lines:** 552-587  
**Purpose:** Map failure codes to human-readable root cause and action  
**Why Helper:** Deterministic mapping logic  
**New Location:** `scripts/diagnose_test_failure.py`  
**Called From:** commands/test.md when escalation needed

#### `escalate_broken_tests(evidence)` - HELPER SCRIPT
**Lines:** 590-631  
**Purpose:** Generate structured escalation data for broken tests  
**Why Helper:** Iterates results, builds structured dict with diagnosis  
**New Location:** `scripts/escalate_broken_tests.py`  
**Called From:** commands/test.md Step 6 - Handle Escalations

#### `execute_test_command(...)` - NATURAL LANGUAGE
**Lines:** 634-754  
**Purpose:** Main orchestration - call sub-functions in sequence  
**Why Natural Language:** High-level workflow orchestration  
**Conversion:** This becomes the actual `commands/test.md` file structure

---

### commands/implement.py (801 lines)

#### `load_config(project_root)` - NATURAL LANGUAGE (duplicate)
**Lines:** 81-109  
**Same as test.py, convert once**

#### `find_test_design_artifact(feature_id, config, project_root)` - NATURAL LANGUAGE
**Lines:** 112-143  
**Purpose:** Find test-design artifact using artifact_paths.find_existing  
**Why Natural Language:** Simple library call with error handling  
**Conversion:**
```markdown
## Step 2: Find Test Design Artifact

Use artifact_paths library:
```
artifact_paths.find_existing(feature_id, 'test_design', config, project_root)
```

If not found:
❌ Error: Test design artifact not found. Run /speckit.multi-agent.test first.
```

#### `find_spec_artifact(feature_id, project_root)` - NATURAL LANGUAGE (duplicate)
**Lines:** 146-170  
**Same as test.py**

#### `prepare_agent_context(...)` - NATURAL LANGUAGE
**Lines:** 173-211  
**Purpose:** Build dict with paths for @make agent  
**Why Natural Language:** Simple dict construction  
**Conversion:**
```markdown
## Step 4: Prepare Agent Context

Build context dict:
- feature_id: ${feature_id}
- test_design_path: ${test_artifact}
- test_file_patterns: ${config.test_framework.file_patterns}
- spec_path: ${spec_artifact} (if exists)
```

#### `create_implementation_notes(...)` - NATURAL LANGUAGE
**Lines:** 214-293  
**Purpose:** Render Jinja2 template for impl-notes  
**Why Natural Language:** Template rendering with error handling  
**Conversion:**
```markdown
## Step 5: Create Implementation Notes

Template: `templates/implementation-notes-template.md`

Variables:
- feature_id, feature_name, agent_name
- timestamp, status: "draft"
- red_state_evidence: ${validation_result} (if validated)

Output: Resolve path using artifact_paths.resolve()

If template missing: Escalate (exit 2)
If permission error: Escalate (exit 2)
```

#### `run_integration_checks(project_root, config, feature_id)` - HELPER SCRIPT
**Lines:** 296-397  
**Purpose:** Execute integration checks (ruff, mypy) with timeout, capture output  
**Why Helper:** Subprocess execution, timeout handling, structured result collection  
**New Location:** `scripts/run_integration_checks.py`  
**Called From:** commands/implement.md Step 8 - Run Integration Checks (GREEN validation)

**Input:** Project root, config with integration_checks section  
**Output:** JSON array of check results with exit codes, output, critical flag  
**Features:** 60s timeout per check, error handling, critical vs warning distinction

#### `update_impl_notes_with_integration_results(artifact_path, results)` - NATURAL LANGUAGE
**Lines:** 400-465  
**Purpose:** Insert integration results section into markdown  
**Why Natural Language:** Simple string replacement, markdown generation  
**Conversion:**
```markdown
## Update Implementation Notes with Integration Results

Read artifact: ${artifact_path}

Build markdown section:
- Summary: ${passed}/${total} checks passed
- Table with check name, command, status
- Details for failed checks (output snippet)

Insert before "## Notes" section or append at end
```

#### `update_impl_notes_with_green_evidence(artifact_path, validation_result)` - NATURAL LANGUAGE
**Lines:** 468-551  
**Purpose:** Insert GREEN evidence section into markdown  
**Why Natural Language:** Regex replacement, markdown generation  
**Conversion:**
```markdown
## Update Implementation Notes with GREEN Evidence

Read artifact: ${artifact_path}

Update status line: draft → complete

Build GREEN evidence section:
- Test success output (snippet)
- Passing test counts
- Timestamp
- GREEN validation: YES
- Coverage metrics (if available)

Insert after RED State section using regex
```

#### Main function and TDD validation - NATURAL LANGUAGE
**Lines:** 554-801  
**Purpose:** Orchestrate RED/GREEN validation flow  
**Why Natural Language:** High-level workflow, calls validation functions  
**Conversion:** Becomes the structure of `commands/implement.md`

---

### commands/review.py (382 lines)

Most functions are NATURAL LANGUAGE (simple file finding, template rendering):

#### `load_config(project_root)` - NATURAL LANGUAGE (duplicate)
**Lines:** 67-94

#### `find_implementation_notes(feature_id, project_root)` - NATURAL LANGUAGE
**Lines:** 97-132  
**Simple path search with error message**

#### `find_spec_artifact(feature_id, project_root)` - NATURAL LANGUAGE (duplicate)
**Lines:** 135-163

#### `get_feature_name(feature_id, impl_notes_path)` - NATURAL LANGUAGE
**Lines:** 166-188  
**Extract first H1 from markdown**

#### `generate_review_artifacts(...)` - NATURAL LANGUAGE
**Lines:** 190-265  
**Jinja2 template rendering for arch/code review**

#### `execute_review_command(...)` - NATURAL LANGUAGE
**Lines:** 268-327  
**High-level orchestration**

---

### commands/commit.py (320 lines)

Entire file is NATURAL LANGUAGE - all functions are simple:

#### `load_config(project_root)` - NATURAL LANGUAGE (duplicate)
**Lines:** 49-77

#### `find_artifact(feature_id, artifact_type, config, project_root)` - NATURAL LANGUAGE
**Lines:** 80-115  
**Simple path construction with exists() check**

#### `generate_workflow_summary(...)` - NATURAL LANGUAGE
**Lines:** 119-182  
**Jinja2 template rendering**

#### `execute_commit_command(...)` - NATURAL LANGUAGE
**Lines:** 185-285  
**Check all artifacts exist, generate summary**

---

### commands/execute.py (265 lines)

Entire file is NATURAL LANGUAGE - subprocess orchestration:

#### `invoke_subcommand(command, feature_id, project_root, ...)` - NATURAL LANGUAGE
**Lines:** 15-74  
**Purpose:** Run subprocess, map exit codes to status  
**Why Natural Language:** Straightforward subprocess.run with status mapping  
**Conversion:**
```markdown
## Invoke Subcommand

Execute: `python commands/${command}.py ${feature_id} ${additional_args}`

Map exit codes:
- 0 → SUCCESS
- 1 → FAILED (validation failure)
- 2 → BLOCKED (escalation)

Capture stdout, stderr
```

#### `request_interactive_approval(...)` - NATURAL LANGUAGE
**Lines:** 77-106  
**Simple user input prompt**

#### `execute_workflow(...)` - NATURAL LANGUAGE
**Lines:** 109-189  
**Sequential step execution with error handling**

---

## Library Files Analysis

### lib/artifact_paths.py (124 lines)

**Status:** KEEP AS LIBRARY - already correctly located

#### `resolve(feature_id, artifact_type, config, project_root)` - KEEP AS LIBRARY
**Purpose:** Resolve artifact path from config template  
**Why Library:** Reusable utility, deterministic path construction  
**Usage:** Called from multiple commands for artifact path resolution

#### `find_existing(feature_id, artifact_type, config, project_root)` - KEEP AS LIBRARY
**Purpose:** Search configured paths for existing artifact  
**Why Library:** Reusable search logic with priority ordering  
**Usage:** Called from multiple commands for artifact discovery

#### `ensure_directory(path)` - KEEP AS LIBRARY
**Purpose:** Create parent directory for artifact  
**Why Library:** Simple utility, prevents duplication  

---

### lib/parse_test_evidence.py (600 lines)

**Status:** PROMOTE TO HELPER SCRIPT - too complex for library

#### `load_patterns(patterns_file)` - KEEP AS LIBRARY
**Purpose:** Load test-patterns.yml configuration  
**Why Library:** Simple YAML loading  

#### `get_default_patterns()` - KEEP AS LIBRARY
**Purpose:** Return hardcoded failure patterns  
**Why Library:** Fallback configuration  

#### `classify_failure(error_message, patterns)` - HELPER SCRIPT
**Lines:** 136-159  
**Purpose:** Match error message against regex patterns to classify failure  
**Why Helper:** Complex regex matching, priority ordering  
**New Location:** `scripts/classify_test_failure.py`  
**Called From:** Test parsing helper script

**Input:** Error message string, patterns dict  
**Output:** Classification code (MISSING_BEHAVIOR, ASSERTION_MISMATCH, TEST_BROKEN, ENV_BROKEN, UNKNOWN)  
**Exit Codes:** 0=success

#### `detect_state(evidence)` - HELPER SCRIPT
**Lines:** 162-195  
**Purpose:** Determine RED/GREEN/BROKEN from TestEvidence  
**Why Helper:** Multi-condition state machine logic  
**New Location:** `scripts/detect_test_state.py`  
**Called From:** Test parsing helper script

**Logic:**
- GREEN: all tests passed
- BROKEN: any TEST_BROKEN/ENV_BROKEN
- RED: any MISSING_BEHAVIOR/ASSERTION_MISMATCH
- Default: BROKEN (if failures but unclassified)

#### `parse_pytest_output(output, patterns)` - HELPER SCRIPT
**Lines:** 198-404  
**Purpose:** Parse pytest output into structured TestEvidence  
**Why Helper:** Complex multi-pass parsing, regex, state tracking  
**New Location:** `scripts/parse_pytest_output.py`  
**Called From:** Multiple commands need test parsing

**Input:** Raw pytest stdout string, patterns dict  
**Output:** JSON with TestEvidence structure  
**Features:**
- Multi-line state machine (collecting failures, summary sections)
- Regex extraction (test names, statuses, error messages, line numbers)
- Two-pass parsing (test results first, then failure details)
- Short summary parsing for counts

#### Helper functions - KEEP AS LIBRARY
**Lines:** 407-475  
`_parse_summary_counts`, `_process_failure` are internal utilities

#### `format_summary(evidence)` - NATURAL LANGUAGE
**Lines:** 477-531  
**Purpose:** Format TestEvidence as human-readable text  
**Why Natural Language:** Simple string formatting  
**Conversion:** Can be described in markdown for LLM to implement

---

### lib/test_runner.py (384 lines)

**Status:** SPLIT - some functions to helpers, some to natural language

#### `run_tests(project_root, test_command, test_paths)` - HELPER SCRIPT
**Lines:** 16-58  
**Purpose:** Execute test command with arguments, capture output  
**Why Helper:** Subprocess execution, exit code handling  
**New Location:** `scripts/run_tests.py`  
**Called From:** validate_red_state, validate_green_state helpers

**Input:** Project root, command (pytest), paths  
**Output:** Tuple of (exit_code, stdout, stderr)  
**Features:** Adds pytest flags (-v, --tb=short)

#### `validate_red_state(project_root, config, feature_id)` - HELPER SCRIPT
**Lines:** 61-193  
**Purpose:** Run tests, parse, validate RED state with detailed messaging  
**Why Helper:** Combines subprocess + parsing + validation logic with precise exit codes  
**New Location:** `scripts/validate_red_state.py`  
**Called From:** commands/implement.md Step 4.5 - TDD Entry Validation

**Input:** Project root, config, feature_id  
**Output:** JSON with validation result:
```json
{
  "state": "RED|GREEN|BROKEN",
  "evidence": TestEvidence,
  "timestamp": "ISO8601",
  "exit_code": 0-2,
  "output": "stdout",
  "validation_passed": bool,
  "message": "human-readable"
}
```

**Exit Codes:** 0=valid RED, 1=invalid (GREEN/BROKEN)

#### `validate_green_state(project_root, config, feature_id, baseline_test_count)` - HELPER SCRIPT
**Lines:** 196-336  
**Purpose:** Run tests, parse, validate GREEN state, check test count vs baseline  
**Why Helper:** Similar complexity to validate_red_state  
**New Location:** `scripts/validate_green_state.py`  
**Called From:** commands/implement.md Step 8 - GREEN State Validation (with --validate-green)

**Input:** Project root, config, feature_id, optional baseline_test_count  
**Output:** JSON with validation result (same structure as RED validation)  
**Features:** Baseline test count comparison, coverage extraction

#### `extract_coverage_metrics(test_output)` - HELPER SCRIPT
**Lines:** 339-384  
**Purpose:** Parse pytest-cov output for coverage percentage  
**Why Helper:** Regex pattern matching for specific output format  
**New Location:** `scripts/extract_coverage_metrics.py`  
**Called From:** validate_green_state helper

**Input:** Test stdout string  
**Output:** JSON with `{percentage: int, statements: int, missing: int, found: bool}` or null

---

### lib/evidence_validator.py (172 lines)

**Status:** KEEP AS LIBRARY with some HELPER SCRIPT extraction

#### `validate_all(feature_id, config, project_root)` - KEEP AS LIBRARY
**Purpose:** Check all artifacts exist with required evidence  
**Why Library:** Orchestrates multiple validations, returns structured result  
**Usage:** Called from commit command or hooks

#### `validate_test_evidence(feature_id, config, project_root)` - KEEP AS LIBRARY
**Purpose:** Check test-design has RED state validation markers  
**Why Library:** Simple content checks for required strings  

#### `validate_review_evidence(feature_id, config, project_root)` - KEEP AS LIBRARY
**Purpose:** Check arch/code review artifacts have verdicts  
**Why Library:** Simple content checks for required strings  

---

### lib/generate_artifact.py (396 lines)

**Status:** KEEP AS LIBRARY - utility functions for template rendering

All functions are straightforward utilities for Jinja2 template handling, file path validation, and CLI argument parsing. These are correctly placed as library code.

---

### lib/validate_artifacts.py (369 lines)

**Status:** HELPER SCRIPT - complex validation logic

#### `validate_template_sections(artifact_path, template_sections)` - HELPER SCRIPT
**Lines:** 56-86  
**Purpose:** Check markdown sections exist using regex  
**Why Helper:** Complex regex with multiple pattern variants  
**New Location:** `scripts/validate_artifact_structure.py`  
**Called From:** Commit command or pre-commit hook

#### `validate_evidence_timestamps(artifacts_dir)` - HELPER SCRIPT
**Lines:** 89-132  
**Purpose:** Parse timestamps from workflow summary, verify RED < GREEN  
**Why Helper:** Regex extraction, ISO8601 parsing, comparison logic  
**New Location:** `scripts/validate_evidence_timestamps.py`  
**Called From:** Commit command or pre-commit hook

#### `validate_red_green_evidence(artifacts_dir)` - HELPER SCRIPT
**Lines:** 134-177  
**Purpose:** Check workflow summary contains RED and GREEN markers  
**Why Helper:** Multiple regex patterns, boolean logic  
**New Location:** `scripts/validate_evidence_content.py`  
**Called From:** Commit command or pre-commit hook

#### `validate_feature_artifacts(feature_id, artifacts_dir)` - HELPER SCRIPT
**Lines:** 180-264  
**Purpose:** Main validation - check all artifacts exist with valid structure  
**Why Helper:** Orchestrates multiple validation helpers, builds report  
**New Location:** `scripts/validate_feature_artifacts.py`  
**Called From:** commands/commit.md Step 1 - Validate Evidence Artifacts

**Input:** Feature ID, artifacts directory  
**Output:** JSON validation report:
```json
{
  "feature_id": "feat-123",
  "valid": bool,
  "artifacts": {
    "test_design": {"exists": bool, "valid_structure": bool, "missing_sections": []},
    ...
  },
  "evidence": {
    "red_green_transition": bool,
    "timestamps_valid": bool,
    "message": "..."
  },
  "errors": ["..."]
}
```

**Exit Codes:** 0=valid, 1=validation failed

#### `format_report_text(report, verbose)` - NATURAL LANGUAGE
**Lines:** 267-305  
**Purpose:** Format validation report as human-readable text  
**Why Natural Language:** Simple string formatting  

---

### lib/validate_manifests.py (460 lines)

**Status:** HELPER SCRIPT - JSON schema validation

Entire file is for validating plugin.json, extension.json, agent .md files against schemas. This is deterministic validation logic that should remain as a helper script.

#### Key functions:
- `validate_plugin_manifest(path)` - JSON schema validation
- `validate_extension_manifest(path)` - JSON schema validation  
- `validate_agent_definition(path)` - YAML frontmatter validation  
- `validate_config_yaml(path)` - YAML structure validation  

**Location:** `scripts/validate_manifests.py` (already correct as script)  
**Called From:** Pre-commit hooks, CI/CD pipelines, make validate

---

### lib/human_feedback.py (71 lines)

**Status:** NATURAL LANGUAGE - simple I/O

#### `request_feedback(stage, context, skip)` - NATURAL LANGUAGE
**Lines:** 10-56  
**Purpose:** Print context, request user input  
**Why Natural Language:** Straightforward console I/O  
**Conversion:**
```markdown
## Request Human Feedback

Print header:
```
HUMAN FEEDBACK REQUESTED: ${stage}
${context}
```

Prompt: "Provide feedback (or press Enter to continue): "

If input non-empty: Store feedback
```

#### `append_to_artifact(artifact_path, feedback)` - NATURAL LANGUAGE
**Lines:** 59-71  
**Purpose:** Append feedback section to markdown  
**Why Natural Language:** Simple file append  

---

### lib/jira_local.py (233 lines)

**Status:** NATURAL LANGUAGE - simple file/folder operations

Entire file is straightforward directory creation and markdown file generation with frontmatter. No complex logic requiring helper scripts.

---

## Recommended Helper Scripts

### 1. scripts/validate_red_state.py
**Purpose:** Validate tests are in RED state before implementation  
**Source Functions:**
- `lib/test_runner.py::validate_red_state()` (lines 61-193)
- `lib/test_runner.py::run_tests()` (lines 16-58) - dependency
- `lib/parse_test_evidence.py::parse_pytest_output()` (lines 198-404) - dependency
- `commands/test.py::validate_red_state()` (lines 518-549) - simpler version

**Input:** Feature ID, project root  
**Output:** JSON with validation result
```json
{
  "state": "RED|GREEN|BROKEN",
  "validation_passed": bool,
  "message": "human-readable explanation",
  "evidence": {
    "total_tests": 5,
    "passed": 0,
    "failed": 5,
    "errors": 0,
    "failure_codes": ["MISSING_BEHAVIOR", "ASSERTION_MISMATCH"]
  },
  "timestamp": "2026-05-07T10:30:00Z"
}
```

**Exit Codes:**
- 0 = valid RED (tests failing with MISSING_BEHAVIOR/ASSERTION_MISMATCH)
- 1 = invalid (tests passing or broken)
- 2 = system error (pytest failed to run, parsing error)

**Called From:**
- commands/test.md - Step 5: Validate RED State
- commands/implement.md - Step 4.5: TDD Entry Validation
- hooks/handlers/tdd_sequence_enforcer.py - Automatic validation before implementation

### 2. scripts/validate_green_state.py
**Purpose:** Validate tests are in GREEN state after implementation  
**Source Functions:**
- `lib/test_runner.py::validate_green_state()` (lines 196-336)
- `lib/test_runner.py::extract_coverage_metrics()` (lines 339-384) - dependency

**Input:** Feature ID, project root, optional baseline test count  
**Output:** JSON with validation result (same structure as RED, plus coverage)
```json
{
  "state": "GREEN|RED|BROKEN",
  "validation_passed": bool,
  "message": "...",
  "evidence": {...},
  "coverage": {
    "percentage": 85,
    "statements": 120,
    "missing": 18,
    "found": true
  },
  "baseline_test_count": 5,
  "current_test_count": 5
}
```

**Exit Codes:**
- 0 = valid GREEN (all tests passing)
- 1 = invalid (tests still failing)
- 2 = escalation (tests broken)

**Called From:**
- commands/implement.md - Step 8: GREEN State Validation (with --validate-green)
- hooks/handlers/tdd_sequence_enforcer.py - Automatic validation after implementation

### 3. scripts/parse_pytest_output.py
**Purpose:** Parse pytest output into structured TestEvidence  
**Source Functions:**
- `lib/parse_test_evidence.py::parse_pytest_output()` (lines 198-404)
- `lib/parse_test_evidence.py::classify_failure()` (lines 136-159) - dependency
- `lib/parse_test_evidence.py::detect_state()` (lines 162-195) - dependency

**Input:** Pytest stdout (via stdin or file), patterns config  
**Output:** JSON TestEvidence
```json
{
  "state": "RED|GREEN|BROKEN",
  "total_tests": 5,
  "passed": 0,
  "failed": 5,
  "errors": 0,
  "skipped": 0,
  "results": [
    {
      "name": "test_login",
      "status": "failed",
      "failure_code": "MISSING_BEHAVIOR",
      "error_message": "NotImplementedError: login() not implemented",
      "file_path": "tests/test_auth.py",
      "line_number": 45
    }
  ],
  "summary": "5 tests: 5 failed (state: RED)"
}
```

**Exit Codes:**
- 0 = GREEN
- 1 = RED
- 2 = BROKEN
- 3 = parsing error

**Called From:**
- validate_red_state.py helper
- validate_green_state.py helper
- commands/test.md (via detect_test_failures)

### 4. scripts/extract_acceptance_criteria.py
**Purpose:** Extract AC-N items from spec markdown  
**Source Functions:**
- `commands/test.py::extract_acceptance_criteria()` (lines 189-224)

**Input:** Spec content (via stdin or file)  
**Output:** JSON array of acceptance criteria
```json
[
  "AC-1: User can log in with email and password",
  "AC-2: Invalid credentials show error message",
  "AC-3: Successful login redirects to dashboard"
]
```

**Exit Codes:** 0=success, 1=no AC found

**Called From:**
- commands/test.md - Step 2: Parse Spec Content

### 5. scripts/validate_feature_artifacts.py
**Purpose:** Validate all evidence artifacts exist with correct structure  
**Source Functions:**
- `lib/validate_artifacts.py::validate_feature_artifacts()` (lines 180-264)
- `lib/validate_artifacts.py::validate_template_sections()` (lines 56-86) - dependency
- `lib/validate_artifacts.py::validate_evidence_timestamps()` (lines 89-132) - dependency
- `lib/validate_artifacts.py::validate_red_green_evidence()` (lines 134-177) - dependency

**Input:** Feature ID, artifacts directory  
**Output:** JSON validation report
```json
{
  "feature_id": "feat-123",
  "valid": true,
  "artifacts": {
    "test_design": {
      "exists": true,
      "valid_structure": true,
      "missing_sections": []
    },
    "impl_notes": {"exists": false},
    "arch_review": {"exists": true, "valid_structure": true, "missing_sections": []},
    "code_review": {"exists": true, "valid_structure": true, "missing_sections": []},
    "workflow_summary": {"exists": true, "valid_structure": true, "missing_sections": []}
  },
  "evidence": {
    "red_green_transition": true,
    "timestamps_valid": true,
    "message": "RED (2026-05-07T10:00:00Z) before GREEN (2026-05-07T11:30:00Z)"
  },
  "errors": []
}
```

**Exit Codes:** 0=valid, 1=validation failed, 2=system error

**Called From:**
- commands/commit.md - Step 1: Validate Evidence Artifacts
- hooks/handlers/pre_commit_gate.py - Block commit if validation fails

### 6. scripts/run_integration_checks.py
**Purpose:** Execute integration checks (ruff, mypy, etc.) with timeout  
**Source Functions:**
- `commands/implement.py::run_integration_checks()` (lines 296-397)

**Input:** Project root, feature ID  
**Output:** JSON array of check results
```json
[
  {
    "name": "ruff",
    "command": "ruff check src/",
    "exit_code": 0,
    "passed": true,
    "output": "All checks passed!",
    "critical": false
  },
  {
    "name": "mypy",
    "command": "mypy src/",
    "exit_code": 1,
    "passed": false,
    "output": "Found 2 errors in src/auth.py",
    "critical": false
  }
]
```

**Exit Codes:**
- 0 = all checks passed
- 1 = some checks failed (non-critical)
- 2 = critical check failed
- 3 = timeout or system error

**Called From:**
- commands/implement.md - Step 8: Run Integration Checks (after GREEN validation)

### 7. scripts/escalate_broken_tests.py
**Purpose:** Generate escalation details for broken tests  
**Source Functions:**
- `commands/test.py::escalate_broken_tests()` (lines 590-631)
- `commands/test.py::diagnose_root_cause()` (lines 552-566) - dependency
- `commands/test.py::recommend_action()` (lines 569-587) - dependency

**Input:** TestEvidence JSON (with BROKEN state)  
**Output:** JSON escalation report
```json
{
  "escalated": true,
  "count": 2,
  "failures": [
    {
      "failure_type": "TEST_BROKEN",
      "test_name": "test_login",
      "location": "tests/test_auth.py:45",
      "error_message": "SyntaxError: invalid syntax",
      "root_cause": "Test code has syntax errors",
      "recommended_action": "Fix syntax errors in test code"
    },
    {
      "failure_type": "ENV_BROKEN",
      "test_name": "test_api_call",
      "location": "tests/test_api.py:20",
      "error_message": "ModuleNotFoundError: No module named 'requests'",
      "root_cause": "Test environment missing dependencies",
      "recommended_action": "Install missing test dependencies"
    }
  ]
}
```

**Exit Codes:** 0=success

**Called From:**
- commands/test.md - Step 6: Handle Escalations (when state=BROKEN)

---

## Recommended Hook Handlers

### 1. hooks/handlers/file_gate_enforcer.py
**Purpose:** Enforce file gate (only test files during test step)  
**Hook Type:** PreToolUse  
**Trigger:** tool=="Write" && phase=="test"  
**Source Functions:**
- `commands/test.py::validate_test_file_pattern()` (lines 227-274)

**Logic:**
```python
#!/usr/bin/env python3
import sys
import json
from pathlib import Path

# Read hook input
input_data = json.load(sys.stdin)
file_path = Path(input_data['params']['file_path'])
phase = input_data.get('context', {}).get('phase', 'unknown')

# Load config
config = load_config()
test_patterns = config.get('test_framework', {}).get('file_patterns', [])

# Check if in test phase
if phase == "test":
    # Check if file matches test patterns
    matches = any(file_path.match(pattern) for pattern in test_patterns)
    
    if not matches:
        # Constitutional violation - block with exit 2
        error = {
            "allowed": False,
            "reason": f"File {file_path} does not match test patterns. Only test files allowed during test step.",
            "details": {
                "file": str(file_path),
                "allowed_patterns": test_patterns
            }
        }
        print(json.dumps(error), file=sys.stderr)
        sys.exit(2)  # Block

# Allow
print(json.dumps({"allowed": True}))
sys.exit(0)
```

**Called From:** Claude Code hook system (automatic on every Write tool use)

### 2. hooks/handlers/tdd_sequence_enforcer.py
**Purpose:** Enforce TDD sequence (RED → GREEN, not GREEN → ???)  
**Hook Type:** PreToolUse  
**Trigger:** tool=="Write" && phase=="implement"  
**Source:** New logic based on TDD constitutional requirements

**Logic:**
```python
#!/usr/bin/env python3
import sys
import json
import subprocess

# Read hook input
input_data = json.load(sys.stdin)
phase = input_data.get('context', {}).get('phase', 'unknown')
feature_id = input_data.get('context', {}).get('feature_id')

# Only enforce during implementation phase
if phase == "implement" and feature_id:
    # Run RED state validation
    result = subprocess.run(
        ['python', 'scripts/validate_red_state.py', feature_id],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        # Not in valid RED state
        validation_data = json.loads(result.stdout)
        
        error = {
            "allowed": False,
            "reason": f"Cannot implement - tests not in valid RED state: {validation_data['message']}",
            "details": validation_data
        }
        print(json.dumps(error), file=sys.stderr)
        sys.exit(2)  # Block

# Allow
print(json.dumps({"allowed": True}))
sys.exit(0)
```

**Called From:** Claude Code hook system (automatic before implementation)

### 3. hooks/handlers/evidence_gate_enforcer.py
**Purpose:** Block commit if evidence artifacts invalid  
**Hook Type:** PreToolUse  
**Trigger:** tool=="Bash" && command contains "git commit"  
**Source:** New logic based on commit constitutional requirements

**Logic:**
```python
#!/usr/bin/env python3
import sys
import json
import subprocess

# Read hook input
input_data = json.load(sys.stdin)
command = input_data.get('params', {}).get('command', '')
feature_id = input_data.get('context', {}).get('feature_id')

# Only enforce for git commit
if 'git commit' in command and feature_id:
    # Run artifact validation
    result = subprocess.run(
        ['python', 'scripts/validate_feature_artifacts.py', feature_id],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        # Validation failed
        validation_data = json.loads(result.stdout)
        
        error = {
            "allowed": False,
            "reason": f"Cannot commit - evidence validation failed: {len(validation_data['errors'])} error(s)",
            "details": validation_data
        }
        print(json.dumps(error), file=sys.stderr)
        sys.exit(2)  # Block

# Allow
print(json.dumps({"allowed": True}))
sys.exit(0)
```

**Called From:** Claude Code hook system (automatic before git commit)

---

## Natural Language Conversions

### 1. Simple File Operations

**Before (Python):**
```python
def find_spec_artifact(feature_id: str, project_root: Optional[Path] = None) -> Path:
    if project_root is None:
        project_root = Path.cwd()
    
    candidates = [
        project_root / "docs" / "features" / f"{feature_id}.md",
        project_root / "docs" / "specs" / f"{feature_id}-spec.md",
        project_root / "docs" / "specs" / f"{feature_id}.md",
        project_root / ".specify" / "specs" / f"{feature_id}.md",
    ]
    
    for path in candidates:
        if path.exists():
            return path
    
    checked_paths = "\n  - ".join(str(p) for p in candidates)
    raise FileNotFoundError(
        f"Spec artifact not found for feature: {feature_id}\n"
        f"Checked locations:\n  - {checked_paths}"
    )
```

**After (Markdown):**
```markdown
## Step 1: Find Spec Artifact

Search for spec artifact in order:
1. Check `docs/features/${feature_id}.md`
2. Check `docs/specs/${feature_id}-spec.md`
3. Check `docs/specs/${feature_id}.md`
4. Check `.specify/specs/${feature_id}.md`

If none exist:
❌ Error: Spec artifact not found for feature: ${feature_id}

Checked locations:
  - docs/features/${feature_id}.md
  - docs/specs/${feature_id}-spec.md
  - docs/specs/${feature_id}.md
  - .specify/specs/${feature_id}.md

Exit with code 1 (validation failure)
```

### 2. Configuration Loading

**Before (Python):**
```python
def load_config(project_root: Optional[Path] = None) -> Dict[str, Any]:
    if project_root is None:
        project_root = Path.cwd()
    
    config_path = project_root / ".specify" / "harness-tdd-config.yml"
    
    if not config_path.exists():
        return DEFAULT_CONFIG.copy()
    
    if yaml is None:
        print("WARNING: PyYAML not installed, using defaults", file=sys.stderr)
        return DEFAULT_CONFIG.copy()
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            return config or DEFAULT_CONFIG.copy()
    except yaml.YAMLError as e:
        print(f"WARNING: Config malformed at {config_path}: {e}, using defaults", file=sys.stderr)
        return DEFAULT_CONFIG.copy()
```

**After (Markdown):**
```markdown
## Load Configuration

Check if `.specify/harness-tdd-config.yml` exists:

**If exists:**
1. Read YAML file
2. Parse configuration
3. If parsing fails:
   - ⚠️  Warning: Config malformed, using defaults
   - Use DEFAULT_CONFIG

**If not exists:**
- Use DEFAULT_CONFIG (from template)

**DEFAULT_CONFIG structure:**
```yaml
version: '1.0'
agents:
  test_agent: 'test-specialist'
  implementation_agent: 'dev-specialist'
artifacts:
  test_design:
    path: 'docs/tests/test-design/{feature_id}-test-design.md'
test_framework:
  type: 'pytest'
  file_patterns:
    - 'tests/**/*.py'
```
```

### 3. Agent Invocation

**Before (Python):**
```python
def spawn_test_agent(
    feature_id: str,
    spec_content: str,
    config: Dict[str, Any],
    project_root: Optional[Path] = None,
    allow_non_test_files: bool = False,
    bypass_justification: Optional[str] = None
) -> int:
    if project_root is None:
        project_root = Path.cwd()
    
    context = build_agent_context(feature_id, spec_content, config)
    
    # Build file gate section
    file_gate_section = "\nFILE GATE RESTRICTIONS:\n"
    if allow_non_test_files and bypass_justification:
        file_gate_section += f"⚠️  BYPASS ACTIVE: Non-test files allowed\n"
        file_gate_section += f"Justification: {bypass_justification}\n"
    else:
        file_gate_section += "You MUST only create/modify files matching these patterns:\n"
        file_gate_section += chr(10).join('- ' + p for p in context['test_patterns'])
    
    # Format prompt
    prompt = f"""
You are @test-specialist writing tests for feature: {context['feature_id']}

SPEC CONTENT:
{context['spec_content']}

{file_gate_section}

TASK:
1. Write failing tests (RED state) for all acceptance criteria
2. Tests MUST fail initially
"""
    
    # Write context file
    fd, temp_path = tempfile.mkstemp(prefix=f"test-agent-context-{feature_id}-", suffix=".txt")
    context_file = Path(temp_path)
    os.close(fd)
    context_file.write_text(prompt, encoding='utf-8')
    
    print(f"Context file: {context_file}")
    return 0
```

**After (Markdown):**
```markdown
## Step 4: Invoke @test-specialist Agent

Create temporary context file: `/tmp/test-agent-context-${feature_id}.txt`

**Build agent prompt:**

```
You are @test-specialist writing tests for feature: ${feature_id}

SPEC CONTENT:
${spec_content}

ACCEPTANCE CRITERIA:
${acceptance_criteria}

TEST PATTERNS:
${test_patterns}

VALID FAILURE CODES:
${valid_failure_codes}

FILE GATE RESTRICTIONS:
[If --allow-non-test-files is set and --justification provided:]
  ⚠️  BYPASS ACTIVE: Non-test files allowed
  Justification: ${bypass_justification}
  
  You may create/modify files outside test patterns if necessary.

[Otherwise:]
  You MUST only create/modify files matching these patterns:
  ${test_patterns}
  
  Files not matching these patterns will be rejected.

TASK:
1. Write failing tests (RED state) for all acceptance criteria
2. Use test patterns from config
3. Tests MUST fail initially (MISSING_BEHAVIOR or ASSERTION_MISMATCH)
4. DO NOT write implementation code
5. RESPECT file gate restrictions
```

**Write context to file:**
- Path: `/tmp/test-agent-context-${feature_id}.txt`
- Content: (agent prompt above)

**Print instructions:**
```
=== Agent Invocation Required ===
Please invoke @test-specialist agent with the following context:
Feature ID: ${feature_id}
Context file: /tmp/test-agent-context-${feature_id}.txt

NOTE: This is Phase 2 MVP behavior (context-file handoff).
      Future phases will automate via Claude Code Agent API.
================================
```
```

### 4. Template Rendering

**Before (Python):**
```python
def generate_test_design_artifact(
    feature_id: str,
    feature_name: str,
    output_path: Path,
    template_dir: Optional[Path] = None,
    bypass_info: Optional[Dict[str, Any]] = None,
    evidence: Optional[TestEvidence] = None,
    valid_red: Optional[bool] = None,
    escalation: Optional[Dict[str, Any]] = None
) -> Path:
    if template_dir is None or not template_dir.exists():
        script_dir = Path(__file__).parent.parent
        template_dir = script_dir / "templates"
    
    if not template_dir.exists():
        raise FileNotFoundError(f"Template directory not found: {template_dir}")
    
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        undefined=StrictUndefined
    )
    
    template = env.get_template("test-design-template.md")
    
    variables = {
        "feature_id": feature_id,
        "feature_name": feature_name,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "draft",
        "bypass_info": bypass_info,
        "evidence": evidence,
        "valid_red": valid_red,
        "escalation": escalation,
    }
    content = template.render(**variables)
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding='utf-8')
    
    return output_path
```

**After (Markdown):**
```markdown
## Step 5: Generate Test Design Artifact

**Locate template:**
- Check for custom template: `.specify/templates/test-design-template.md`
- If not found, use built-in: `spec-kit-multi-agent-tdd/templates/test-design-template.md`

**Prepare variables:**
```yaml
feature_id: ${feature_id}
feature_name: ${feature_name}
timestamp: ${timestamp} (ISO 8601 UTC)
status: "draft"
bypass_info: ${bypass_info} (if file gate bypassed)
evidence: ${evidence} (if tests run)
valid_red: ${valid_red} (if validation performed)
escalation: ${escalation} (if tests broken)
```

**Render template:**
- Load template with Jinja2
- Substitute variables
- Generate markdown content

**Write output:**
- Path: Resolve from config using artifact_paths.resolve(feature_id, 'test_design')
- Create parent directory if needed
- Write rendered content

**Handle errors:**
- If template not found: Exit 2 (escalation)
- If permission denied: Exit 2 (escalation)
```

### 5. Subprocess Execution

**Before (Python):**
```python
def invoke_subcommand(
    command: str,
    feature_id: str,
    project_root: Path,
    additional_args: Optional[list] = None
) -> Dict[str, Any]:
    commands_dir = Path(__file__).parent
    command_script = commands_dir / f"{command}.py"
    
    cmd = [sys.executable, str(command_script), feature_id]
    if additional_args:
        cmd.extend(additional_args)
    
    result = subprocess.run(
        cmd,
        cwd=project_root,
        capture_output=True,
        text=True
    )
    
    status_map = {0: 'SUCCESS', 1: 'FAILED', 2: 'BLOCKED'}
    status = status_map.get(result.returncode, 'FAILED')
    
    return {
        'status': status,
        'exit_code': result.returncode,
        'stdout': result.stdout,
        'stderr': result.stderr,
        'command': ' '.join(cmd),
    }
```

**After (Markdown):**
```markdown
## Invoke Subcommand

**Build command:**
```bash
python commands/${command}.py ${feature_id} ${additional_args}
```

**Execute:**
- Working directory: ${project_root}
- Capture stdout and stderr

**Map exit code to status:**
- 0 → SUCCESS
- 1 → FAILED (validation failure)
- 2 → BLOCKED (escalation)
- Other → FAILED

**Return result:**
```json
{
  "status": "SUCCESS|FAILED|BLOCKED",
  "exit_code": 0-2,
  "stdout": "...",
  "stderr": "...",
  "command": "python commands/..."
}
```

**Handle status:**
- SUCCESS: Continue to next step
- FAILED: Stop workflow, report validation failure, exit 1
- BLOCKED: Stop workflow, report escalation, exit 2
```

---

## Robustness Analysis

### What Makes Instructions Fragile:

1. **Complex conditionals with multiple branches**
   - Example: Classifying test failures into 4 categories based on regex patterns
   - Solution: Keep in Python (classify_test_failure.py)

2. **Precise error code detection from subprocess output**
   - Example: Parsing pytest exit codes, stderr vs stdout
   - Solution: Keep in Python (run_tests.py, parse_pytest_output.py)

3. **Schema validation (YAML structure, JSON format)**
   - Example: Validating plugin.json against JSON schema
   - Solution: Keep in Python (validate_manifests.py)

4. **Numerical calculations (coverage percentages, test counts)**
   - Example: Extracting coverage from pytest-cov output: "TOTAL 120 18 85%"
   - Solution: Keep in Python (extract_coverage_metrics.py)

5. **Regex pattern matching (failure codes in test output)**
   - Example: Detecting "MISSING_BEHAVIOR" vs "TEST_BROKEN" from error messages
   - Solution: Keep in Python (classify_failure.py)

6. **State machine logic (multi-line parsing, section tracking)**
   - Example: Parsing pytest output (collecting failures, switching contexts)
   - Solution: Keep in Python (parse_pytest_output.py)

7. **Subprocess timeout handling**
   - Example: Running integration checks with 60s timeout, handling TimeoutExpired
   - Solution: Keep in Python (run_integration_checks.py)

8. **Exit code logic for gates (allow/block decisions)**
   - Example: File gate - exit 2 if non-test file during test phase
   - Solution: Keep in Python hooks (file_gate_enforcer.py)

### What LLMs Handle Well:

1. **File existence checks**
   - Example: "Check if docs/features/${feature_id}.md exists"
   - Markdown: Simple instruction, LLM can use Read tool

2. **Simple read/write operations**
   - Example: "Write agent context to /tmp/test-agent-context-${feature_id}.txt"
   - Markdown: LLM can use Write tool

3. **Agent delegation**
   - Example: "Invoke @test-specialist with context file"
   - Markdown: Natural language instructions for agent invocation

4. **Template rendering with clear variables**
   - Example: "Render test-design-template.md with feature_id, timestamp, status"
   - Markdown: LLM can describe variables and expected output

5. **Conditional logic with 2-3 branches**
   - Example: "If config exists, load it. Otherwise, use defaults."
   - Markdown: Simple if-else can be described clearly

6. **Sequential orchestration**
   - Example: "Step 1: Find spec. Step 2: Extract AC. Step 3: Invoke agent."
   - Markdown: Natural structure for command files

7. **String formatting and path construction**
   - Example: "Build path: docs/features/${feature_id}-test-design.md"
   - Markdown: LLM can construct strings

8. **User interaction (prompts, input)**
   - Example: "Prompt user: Continue to next step? (y/n)"
   - Markdown: LLM can handle console I/O

### Recommended Philosophy:

**KEEP IN PYTHON:**
- Test output parsing (pytest, coverage)
- Failure code classification (regex patterns)
- State validation (RED/GREEN/BROKEN logic)
- Subprocess execution with error handling
- Schema validation (JSON, YAML)
- Constitutional enforcement (file gate, TDD sequence)
- Numerical calculations (coverage %, test counts)
- Timeout handling

**CONVERT TO MARKDOWN:**
- File discovery (search candidate paths)
- Agent context building (dict construction)
- Template rendering (describe variables)
- Configuration loading (simple YAML read)
- Artifact path resolution (string substitution)
- User prompts (console I/O)
- Sequential orchestration (high-level workflow)
- Error message formatting

**USE HOOKS FOR:**
- File gate enforcement (automatic before Write)
- TDD sequence validation (automatic before implement)
- Evidence validation (automatic before commit)
- Any non-negotiable constitutional requirement

---

## Migration Checklist

For each Python function reviewed:

**Commands:**
- [x] test.py (847 lines) - Categorized all functions
- [x] implement.py (801 lines) - Categorized all functions
- [x] review.py (382 lines) - Categorized all functions
- [x] commit.py (320 lines) - Categorized all functions
- [x] execute.py (265 lines) - Categorized all functions

**Libraries:**
- [x] artifact_paths.py (124 lines) - Keep as library
- [x] parse_test_evidence.py (600 lines) - Promote to helper script
- [x] test_runner.py (384 lines) - Split to helper scripts
- [x] evidence_validator.py (172 lines) - Keep as library
- [x] generate_artifact.py (396 lines) - Keep as library
- [x] validate_artifacts.py (369 lines) - Promote to helper script
- [x] validate_manifests.py (460 lines) - Keep as helper script
- [x] human_feedback.py (71 lines) - Convert to natural language
- [x] jira_local.py (233 lines) - Convert to natural language

**Summary:**
- **Helper Scripts Identified:** 7 scripts (~2,430 lines)
  1. validate_red_state.py
  2. validate_green_state.py
  3. parse_pytest_output.py
  4. extract_acceptance_criteria.py
  5. validate_feature_artifacts.py
  6. run_integration_checks.py
  7. escalate_broken_tests.py

- **Hook Handlers Identified:** 3 hooks (~810 lines)
  1. file_gate_enforcer.py
  2. tdd_sequence_enforcer.py
  3. evidence_gate_enforcer.py

- **Natural Language Conversions:** ~2,160 lines
  - All command orchestration logic
  - Simple file operations
  - Agent invocation
  - Template rendering descriptions
  - Configuration loading
  - User interaction

**Next Steps:**
1. Create `scripts/` directory in spec-kit-multi-agent-tdd
2. Extract helper scripts from commands/ and lib/
3. Create `hooks/handlers/` directory
4. Implement hook handlers
5. Convert commands/*.py to commands/*.md
6. Update references in documentation

**Dependencies Identified:**
- Helper scripts depend on:
  - lib/artifact_paths.py (path resolution)
  - lib/parse_test_evidence.py (TestEvidence dataclass)
  - config/test-patterns.yml (failure code patterns)
- Hook handlers depend on:
  - Helper scripts (call via subprocess)
  - Claude Code hook protocol (JSON input/output)

**Test Coverage Assessment:**
- Current: Limited unit tests for libraries
- Needed: Integration tests for helper scripts
- Priority: Test RED/GREEN validation logic extensively
