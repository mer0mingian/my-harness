# Architecture Recommendations for spec-kit-multi-agent-tdd

**Date:** 2026-05-07  
**Status:** Critical Correction Required  
**Issue:** Severe spec drift detected - Python commands incompatible with SpecKit architecture

---

## Executive Summary

**Current State:** Commands implemented as Python scripts (test.py, implement.py, review.py, commit.py, execute.py)

**Correct State:** Commands must be Markdown files with YAML frontmatter per SpecKit specification

**Impact:** Current implementation is incompatible with:
- SpecKit extension registration system
- Universal command format (15+ agent platform support)
- Claude Code skills/commands architecture
- AgentSkills.io open standard
- Real-world SpecKit extension patterns

**Resolution Required:** Immediate architectural correction before Phase 2 completion

---

## Research Findings

### 1. SpecKit Extension Specification

**Source:** `spec-kit/docs/reference/` and real extension `spec-kit-agent-assign/`

**Key Finding:** Commands are **universal Markdown format only**

```markdown
# Mandatory Structure
---
description: "Command description"          # REQUIRED
agent: agent-name                           # OPTIONAL - delegate to agent
tools:                                      # OPTIONAL - MCP tools
  - 'mcp-server/tool_name'
scripts:                                    # OPTIONAL - reference helper scripts
  sh: ../../scripts/bash/helper.sh
---

# Command Instructions
Natural language instructions for Claude Code to execute autonomously.

$ARGUMENTS gets replaced with user input.
```

**From spec-kit-agent-assign analysis:**
- ✅ Extension has ONLY markdown commands (assign.md, validate.md, execute.md)
- ✅ Zero Python scripts in extension directory
- ✅ Scripts referenced are in spec-kit CORE (`.specify/scripts/`)
- ✅ All logic expressed as natural language instructions to Claude Code

**Extension structure:**
```
spec-kit-agent-assign/
├── extension.yml          # Manifest
├── commands/
│   ├── assign.md         # Pure markdown
│   ├── validate.md       # Pure markdown
│   └── execute.md        # Pure markdown
└── .extensionignore      # Excludes dev files
```

### 2. Claude Code Skills Architecture

**Source:** https://code.claude.com/docs/en/skills

**Key Finding:** Skills follow **AgentSkills.io open standard** (cross-platform compatibility)

**Skills vs Commands:**
| Aspect | Commands | Skills |
|--------|----------|--------|
| Format | Markdown + YAML frontmatter | `SKILL.md` in directory |
| Location | `.claude/commands/` | `.claude/skills/skill-name/` |
| Invocation | Slash commands `/cmd` | Auto-triggered or explicit |
| Purpose | Workflow automation | Knowledge + capabilities |
| Scope | Single action | Bundled resources |

**Both are markdown-based** - no Python scripts as commands/skills

### 3. AgentSkills.io Open Standard

**Source:** https://agentskills.io/home

**Key Finding:** Industry standard adopted by **35+ platforms**

**Standard Structure:**
```
skill-name/
├── SKILL.md              # Required: frontmatter + markdown
├── scripts/              # Optional: executable helpers
├── references/           # Optional: supporting docs
└── assets/               # Optional: images, data
```

**Progressive Disclosure:**
- Tier 1: name + description (startup)
- Tier 2: Full SKILL.md body (on invocation)
- Tier 3: Scripts/references (on-demand)

**Compatibility:** Claude Code, GitHub Copilot, VS Code, Cursor, OpenCode, Gemini CLI, and 29+ others

### 4. Claude Code Hooks Architecture

**Source:** https://code.claude.com/docs/en/hooks-guide

**Key Finding:** **THIS IS WHERE PYTHON SCRIPTS BELONG**

**Hooks Execution Model:**
- Hooks are **shell commands** executed at lifecycle points
- Python scripts run as **hook handlers** (not as commands)
- 28 hook types: SessionStart, PreToolUse, PostToolUse, FileChanged, etc.

**Python Script Integration via Hooks:**

```bash
# .claude/hooks/config.yml
hooks:
  PreToolUse:
    - command: python3 scripts/validate_tool_use.py
      when: tool == "Edit"
  
  PostToolUse:
    - command: python3 scripts/run_tests.py
      when: tool == "Write" && path.endswith(".py")
  
  FileChanged:
    - command: python3 scripts/check_tdd_compliance.py
      when: path.startsWith("src/")
```

**Python Script Structure for Hooks:**
```python
#!/usr/bin/env python3
import sys
import json

# Read hook context from stdin
context = json.load(sys.stdin)

# Perform validation/action
result = validate(context)

# Return via exit code
if result.valid:
    sys.exit(0)  # Allow
else:
    print(json.dumps({"error": result.message}))
    sys.exit(2)  # Block
```

**Available Hook Context:**
- Tool name, file paths, content
- Environment variables: `$CLAUDE_PROJECT_DIR`, `$CLAUDE_ENV_FILE`
- Event type, timestamp
- Full conversation context (for some hooks)

---

## Architectural Correction Plan

### Recommended Architecture

```
spec-kit-multi-agent-tdd/
├── extension.yml                    # Manifest (declare commands, hooks)
├── commands/                        # MARKDOWN ONLY
│   ├── test.md                     # Natural language workflow
│   ├── implement.md                # Natural language workflow
│   ├── review.md                   # Natural language workflow
│   ├── commit.md                   # Natural language workflow
│   └── execute.md                  # Orchestration workflow
├── scripts/                         # Python helpers (invoked by hooks)
│   ├── validate_red_state.py
│   ├── validate_green_state.py
│   ├── generate_artifact.py
│   └── evidence_validator.py
├── lib/                            # Shared Python libraries
│   ├── test_runner.py
│   ├── artifact_paths.py
│   └── parse_test_evidence.py
├── templates/                      # Jinja2 templates
│   ├── test-design-template.md
│   ├── implementation-notes-template.md
│   ├── arch-review-template.md
│   ├── code-review-template.md
│   └── workflow-summary-template.md
└── hooks/                          # Hook configurations
    └── config.yml                  # Hook declarations
```

### Command Structure (Markdown)

**Example: commands/test.md**

```markdown
---
description: "Generate failing tests for a feature (Step 7)"
agent: test-specialist
tools:
  - 'filesystem/read'
  - 'filesystem/write'
scripts:
  sh: ../../scripts/bash/validate_environment.sh
  py: ../../scripts/python/validate_red_state.py
---

# Generate Tests Workflow

## User Input
Feature ID: $ARGUMENTS

## Prerequisites

1. Locate feature spec artifact in `docs/features/`
2. Validate project has test framework configured (pytest)
3. Check `.specify/harness-tdd-config.yml` exists

## Step 1: Load Configuration

Load extension configuration:
```bash
config_file=".specify/extensions/multi-agent-tdd/config.yml"
feature_id="$ARGUMENTS"
```

## Step 2: Find Spec Artifact

Search for spec artifact:
- `docs/features/${feature_id}-spec.md`
- `docs/features/${feature_id}.md`

If not found, report error and exit.

## Step 3: Prepare Agent Context

Create context bundle for @test-specialist agent:
- Spec artifact path
- Test design template path
- Target test file patterns from config
- Failure codes configuration

## Step 4: Invoke @test-specialist Agent

Delegate to @test-specialist agent with context:

**Instructions for @test-specialist:**
1. Read feature spec at [spec_path]
2. Write failing tests following TDD principles
3. Only modify files matching patterns: `tests/**/*.py`, `**/test_*.py`
4. Run pytest to validate RED state
5. Generate test-design artifact at `docs/features/${feature_id}-test-design.md`

**File Gate:** Enforce test-only patterns (constitutional requirement)

## Step 5: Validate RED State

After @test-specialist completes:

1. Run pytest to capture test output
2. Parse failure codes (MISSING_BEHAVIOR, ASSERTION_MISMATCH are valid RED)
3. Detect invalid codes (SyntaxError, ImportError require escalation)
4. Store evidence in test-design artifact

Use validation script: `python3 scripts/validate_red_state.py`

## Step 6: Generate Artifact

Create test-design artifact from template:
- Use template: `templates/test-design-template.md`
- Populate with: feature_id, timestamp, RED state evidence
- Save to: `docs/features/${feature_id}-test-design.md`

Use generation script: `python3 scripts/generate_artifact.py`

## Exit Codes
- 0: Success (RED state validated, artifact created)
- 1: Validation failure (tests already passing, spec not found)
- 2: Escalation required (tests broken, template missing)

## Success Criteria
- [ ] Test design artifact created
- [ ] RED state validated
- [ ] Valid failure codes only
- [ ] File gate enforced
```

### Hook Configuration

**hooks/config.yml**

```yaml
# Hooks for TDD workflow enforcement
hooks:
  # Before agent invokes tools
  PreToolUse:
    - name: validate_tdd_sequence
      command: python3 scripts/validate_tdd_sequence.py
      when: tool == "Write" && path.endsWith(".py") && path.startsWith("src/")
      description: "Ensure tests exist before implementation"
  
  # After test files are written
  PostToolUse:
    - name: validate_red_state
      command: python3 scripts/validate_red_state.py
      when: tool == "Write" && path.contains("test_")
      description: "Validate RED state after test creation"
  
  # After implementation files are written
  PostToolUse:
    - name: validate_green_state
      command: python3 scripts/validate_green_state.py
      when: tool == "Write" && path.startsWith("src/")
      description: "Validate GREEN state after implementation"
  
  # Before commit
  PreToolUse:
    - name: validate_evidence
      command: python3 scripts/evidence_validator.py
      when: tool == "Bash" && args[0] == "git" && args[1] == "commit"
      description: "Ensure complete evidence chain exists"
```

### Python Script as Hook Handler

**scripts/validate_red_state.py**

```python
#!/usr/bin/env python3
"""
Hook handler: Validate RED state after test creation
Invoked by PostToolUse hook when test files are written
"""

import sys
import json
from pathlib import Path

# Import shared libraries
from lib.test_runner import run_tests, parse_pytest_output
from lib.artifact_paths import find_test_design

def main():
    # Read hook context from stdin
    context = json.load(sys.stdin)
    
    # Extract relevant info
    tool = context['tool']
    file_path = context['args']['file_path']
    project_dir = Path(context['env']['CLAUDE_PROJECT_DIR'])
    
    # Only validate if test file was written
    if 'test_' not in file_path:
        sys.exit(0)  # Not a test file, allow
    
    # Run tests
    exit_code, stdout, stderr = run_tests(project_dir)
    evidence = parse_pytest_output(stdout)
    
    # Validate RED state
    if evidence.state == "GREEN":
        result = {
            "error": "Tests already passing (no work needed)",
            "recommendation": "Review test assertions"
        }
        print(json.dumps(result))
        sys.exit(2)  # Block - invalid RED state
    
    elif evidence.state == "BROKEN":
        result = {
            "error": f"Tests broken: {evidence.failure_codes}",
            "recommendation": "Fix test syntax errors before continuing"
        }
        print(json.dumps(result))
        sys.exit(2)  # Block - escalation required
    
    else:  # RED state
        result = {
            "status": "RED state validated",
            "failure_codes": evidence.failure_codes,
            "test_count": evidence.total_tests
        }
        print(json.dumps(result))
        sys.exit(0)  # Allow - valid RED state

if __name__ == "__main__":
    main()
```

---

## Migration Strategy

### Phase 1: Convert Commands to Markdown (Priority: CRITICAL)

**For each command (test, implement, review, commit, execute):**

1. **Create markdown file** in `commands/` directory
2. **Write YAML frontmatter** with description, agent, tools, scripts
3. **Convert Python logic to natural language instructions**
   - Step-by-step workflow description
   - Agent delegation instructions
   - Script invocation points
4. **Reference Python scripts via hooks** (not directly)

**Example Conversion:**

**Before (test.py - lines 1-50):**
```python
def find_spec_artifact(feature_id: str) -> Path:
    candidates = [
        Path("docs/features") / f"{feature_id}-spec.md",
        Path("docs/features") / f"{feature_id}.md",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError(f"Spec artifact not found: {feature_id}")
```

**After (test.md):**
```markdown
## Step 2: Find Spec Artifact

Search for spec artifact in order of precedence:
1. `docs/features/${feature_id}-spec.md`
2. `docs/features/${feature_id}.md`

If not found, report error:
```
❌ Error: Spec artifact not found for feature: $feature_id
Expected locations:
  • docs/features/${feature_id}-spec.md
  • docs/features/${feature_id}.md
```
And exit with code 1 (validation failure).
```

### Phase 2: Move Python to Scripts/Lib

**Reorganize Python code:**

1. **Move validation logic to scripts/**
   - `validate_red_state.py`
   - `validate_green_state.py`
   - `evidence_validator.py`

2. **Move shared utilities to lib/**
   - `test_runner.py`
   - `artifact_paths.py`
   - `parse_test_evidence.py`

3. **Keep existing structure for libraries** (already correct)

### Phase 3: Configure Hooks

**Create hooks/config.yml:**

```yaml
hooks:
  PostToolUse:
    - name: validate_red_state
      command: python3 scripts/validate_red_state.py
      when: tool == "Write" && path.contains("test_")
  
  PostToolUse:
    - name: validate_green_state
      command: python3 scripts/validate_green_state.py
      when: tool == "Write" && path.startsWith("src/")
  
  PreToolUse:
    - name: validate_evidence_before_commit
      command: python3 scripts/evidence_validator.py
      when: tool == "Bash" && args.contains("git commit")
```

### Phase 4: Update Extension Manifest

**extension.yml changes:**

```yaml
provides:
  commands:
    - name: "speckit.multi-agent.test"
      file: "commands/test.md"           # Changed from .py to .md
      description: "Generate failing tests"
    
    - name: "speckit.multi-agent.implement"
      file: "commands/implement.md"      # Changed from .py to .md
      description: "Implement feature with TDD"
    
    - name: "speckit.multi-agent.review"
      file: "commands/review.md"         # Changed from .py to .md
      description: "Parallel arch + code review"
    
    - name: "speckit.multi-agent.commit"
      file: "commands/commit.md"         # Changed from .py to .md
      description: "Validate evidence and commit"
    
    - name: "speckit.multi-agent.execute"
      file: "commands/execute.md"        # Changed from .py to .md
      description: "Execute full TDD workflow"
  
  hooks:
    - file: "hooks/config.yml"
      description: "TDD workflow validation hooks"
```

### Phase 5: Testing

**Verify each command:**

1. Install extension: `specify extension add .`
2. Test command invocation: `/speckit.multi-agent.test feat-123`
3. Verify hooks execute at correct lifecycle points
4. Confirm Python scripts receive correct context
5. Test exit codes and error handling

---

## Benefits of Corrected Architecture

### 1. Universal Compatibility
- Commands work across 15+ agent platforms
- Skills follow AgentSkills.io standard (35+ platforms)
- No vendor lock-in

### 2. Separation of Concerns
- **Commands** (markdown): Workflow orchestration
- **Scripts** (Python): Validation logic
- **Hooks** (YAML): Lifecycle integration
- **Lib** (Python): Shared utilities

### 3. Maintainability
- Workflows expressed in natural language (easy to modify)
- Python logic isolated and testable
- Clear extension points via hooks

### 4. Constitutional Compliance
- Hooks enforce non-bypassable gates
- Scripts validate evidence requirements
- Lifecycle integration ensures TDD discipline

### 5. Agent Orchestration
- Commands delegate to specialist agents (@test, @make, @check, @simplify)
- Agents defined separately (`.agents/agents/`)
- Clear responsibility boundaries

---

## Timeline Estimate

**Conversion Effort:**

| Task | Effort | Priority |
|------|--------|----------|
| Convert test.py → test.md | 2 hours | P0 |
| Convert implement.py → implement.md | 2 hours | P0 |
| Convert review.py → review.md | 1 hour | P0 |
| Convert commit.py → commit.md | 1 hour | P0 |
| Convert execute.py → execute.md | 1 hour | P0 |
| Move Python to scripts/ | 1 hour | P0 |
| Create hooks/config.yml | 2 hours | P0 |
| Update extension.yml | 0.5 hours | P0 |
| Testing and validation | 2 hours | P0 |
| **Total** | **12.5 hours** | **CRITICAL** |

**Recommendation:** Halt current implementation, perform architectural correction, then resume Phase 2

---

## Questions for User

1. **Immediate Action:** Should I halt Phase 2 and perform architectural correction now?

2. **Scope Decision:** Should I:
   - A. Convert all 5 commands + existing test/implement from Slice 3-4
   - B. Start fresh with corrected architecture
   - C. Create parallel markdown commands alongside Python (temporary)

3. **Python Scripts:** Which validation logic should remain in Python hooks vs converted to natural language instructions?

4. **Testing Strategy:** Should I create test workspace to validate corrected architecture before full conversion?

5. **Agent Definitions:** Should specialist agents (@test, @make, @check, @simplify) be bundled in extension or discovered from `.claude/agents/`?

---

## Recommendation Summary

**CRITICAL CORRECTION REQUIRED**

Current Python command implementation is fundamentally incompatible with SpecKit architecture. Must convert to universal Markdown format with Python scripts moved to hooks.

**Immediate Action:**
1. Halt Phase 2 Slice 5-6 implementation
2. Perform architectural correction (12.5 hours)
3. Validate corrected architecture
4. Resume Phase 2 with correct patterns

**Long-term Benefit:**
- Cross-platform compatibility (35+ tools)
- Cleaner separation of concerns
- Constitutional enforcement via hooks
- Maintainable natural language workflows
- Industry standard compliance

The research conclusively shows that SpecKit extensions must use markdown commands, with Python scripts relegated to hooks and helper utilities. This is not optional - it's the architectural foundation of the SpecKit ecosystem.
