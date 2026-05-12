# Command File Reference

Complete guide to creating SpecKit extension command files.

## Command File Structure

Command files use Markdown with YAML frontmatter:

```markdown
---
description: "Command description"
tools:                              # Optional: AI tools this command uses
  - 'bash/execute'
  - 'file/read'
scripts:                            # Optional: Helper scripts
  sh: ../../scripts/bash/helper.sh
  ps: ../../scripts/powershell/helper.ps1
---

# Command Name

Description of what the command does.

## User Input

$ARGUMENTS

## Steps

1. Step one
2. Step two
3. Step three

```bash
# Implementation code
echo "Executing command"
```

## Expected Output

- Result 1
- Result 2
```

## Available Variables

Commands have access to these variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `$ARGUMENTS` | User-provided arguments | `hello world` |
| `$PROJECT_ROOT` | Root directory of SpecKit project | `/home/user/project` |
| `$SPEC_DIR` | Directory containing specifications | `/home/user/project/specs` |
| `$EXTENSION_CONFIG_DIR` | Extension config directory | `.specify/extensions/my-ext/` |
| `$FEATURE_ID` | Current feature ID (from branch) | `001-photo-albums` |
| `$FEATURE_DIR` | Current feature directory | `specs/001-photo-albums/` |

**Usage example:**

```bash
# Load extension config
CONFIG_FILE="$EXTENSION_CONFIG_DIR/my-ext-config.yml"
if [ -f "$CONFIG_FILE" ]; then
  source "$CONFIG_FILE"
fi

# Work with current feature
SPEC_FILE="$FEATURE_DIR/spec.md"
if [ -f "$SPEC_FILE" ]; then
  echo "Processing spec: $SPEC_FILE"
fi
```

## Helper Scripts

### Defining Helper Scripts

Reference helper scripts in command frontmatter:

```yaml
---
scripts:
  sh: ../../scripts/bash/helper.sh      # Bash version
  ps: ../../scripts/powershell/helper.ps1  # PowerShell version
---
```

### Using Helper Scripts

```bash
# Source the helper script
source ../../scripts/bash/helper.sh

# Call functions from helper
validate_config "$CONFIG_FILE"
process_data "$INPUT_FILE"
```

### Example Helper Script

**File**: `scripts/bash/helper.sh`

```bash
#!/bin/bash

# Validate configuration file
validate_config() {
  local config_file=$1
  if [ ! -f "$config_file" ]; then
    echo "Error: Config file not found: $config_file"
    return 1
  fi
  
  # Validate YAML syntax
  python -c "import yaml; yaml.safe_load(open('$config_file'))" 2>/dev/null
  if [ $? -ne 0 ]; then
    echo "Error: Invalid YAML in $config_file"
    return 1
  fi
  
  return 0
}

# Load config value
get_config_value() {
  local config_file=$1
  local key=$2
  python -c "import yaml; print(yaml.safe_load(open('$config_file'))['$key'])"
}
```

## Command Patterns

### Pattern 1: Simple Command

Basic command with no configuration:

```markdown
---
description: "Say hello"
---

# Hello Command

Greets the user.

## Steps

1. Display greeting message

```bash
echo "Hello from my extension!"
echo "You said: $ARGUMENTS"
```

## Expected Output

- Greeting message
- User arguments echoed back
```

### Pattern 2: Config-Based Command

Command that reads extension configuration:

```markdown
---
description: "Run configured tool"
---

# Run Tool Command

Executes tool based on extension configuration.

## Steps

1. Load extension config
2. Validate tool availability
3. Execute tool with configured options

```bash
CONFIG_FILE="$EXTENSION_CONFIG_DIR/my-ext-config.yml"

# Load config
if [ ! -f "$CONFIG_FILE" ]; then
  echo "Error: Config not found. Run 'specify extension configure my-ext'"
  exit 1
fi

# Extract tool path
TOOL_PATH=$(grep "tool_path:" "$CONFIG_FILE" | cut -d: -f2 | xargs)

# Validate tool exists
if [ ! -x "$TOOL_PATH" ]; then
  echo "Error: Tool not found or not executable: $TOOL_PATH"
  exit 1
fi

# Execute tool
"$TOOL_PATH" $ARGUMENTS
```

## Expected Output

- Tool output
- Error if config missing or tool unavailable
```

### Pattern 3: Spec Analysis Command

Command that reads and analyzes spec files:

```markdown
---
description: "Analyze specification"
tools:
  - 'file/read'
---

# Analyze Spec Command

Analyzes current feature specification for completeness.

## Steps

1. Load current feature spec
2. Check for required sections
3. Report missing elements

```bash
SPEC_FILE="$FEATURE_DIR/spec.md"

if [ ! -f "$SPEC_FILE" ]; then
  echo "Error: No spec found for current feature"
  exit 1
fi

# Check required sections
MISSING_SECTIONS=()

grep -q "## User Stories" "$SPEC_FILE" || MISSING_SECTIONS+=("User Stories")
grep -q "## Acceptance Criteria" "$SPEC_FILE" || MISSING_SECTIONS+=("Acceptance Criteria")
grep -q "## Success Metrics" "$SPEC_FILE" || MISSING_SECTIONS+=("Success Metrics")

# Report results
if [ ${#MISSING_SECTIONS[@]} -eq 0 ]; then
  echo "✓ Spec is complete"
else
  echo "⚠ Missing sections:"
  for section in "${MISSING_SECTIONS[@]}"; do
    echo "  - $section"
  done
  exit 1
fi
```

## Expected Output

- Success message if spec complete
- List of missing sections if incomplete
```

### Pattern 4: Integration Command

Command that integrates with external tools:

```markdown
---
description: "Sync to Jira"
tools:
  - 'bash/execute'
scripts:
  sh: ../../scripts/bash/jira-helper.sh
---

# Sync to Jira Command

Syncs current feature spec to Jira.

## Steps

1. Load Jira configuration
2. Extract spec metadata
3. Create or update Jira issue
4. Link spec to Jira issue

```bash
source ../../scripts/bash/jira-helper.sh

CONFIG_FILE="$EXTENSION_CONFIG_DIR/jira-config.yml"

# Validate config
validate_jira_config "$CONFIG_FILE" || exit 1

# Extract spec details
SPEC_FILE="$FEATURE_DIR/spec.md"
FEATURE_NAME=$(grep "^# " "$SPEC_FILE" | head -1 | sed 's/^# //')
DESCRIPTION=$(grep -A 10 "## Overview" "$SPEC_FILE" | tail -n +2)

# Create Jira issue
JIRA_KEY=$(create_jira_issue "$FEATURE_NAME" "$DESCRIPTION")

if [ $? -eq 0 ]; then
  echo "✓ Synced to Jira: $JIRA_KEY"
  
  # Store Jira key in spec metadata
  echo "" >> "$SPEC_FILE"
  echo "<!-- JIRA: $JIRA_KEY -->" >> "$SPEC_FILE"
else
  echo "Error: Failed to sync to Jira"
  exit 1
fi
```

## Expected Output

- Jira issue key if successful
- Error message if sync fails
```

### Pattern 5: Validation Command

Command that validates conformance to standards:

```markdown
---
description: "Validate spec quality"
---

# Validate Spec Command

Validates specification against organization standards.

## Steps

1. Check spec completeness
2. Validate acceptance criteria format
3. Check for anti-patterns
4. Generate validation report

```bash
SPEC_FILE="$FEATURE_DIR/spec.md"
ERRORS=0
WARNINGS=0

echo "Validating: $SPEC_FILE"
echo ""

# Check 1: No tech stack in spec
if grep -qi "react\|angular\|vue\|postgresql\|mongodb" "$SPEC_FILE"; then
  echo "❌ ERROR: Tech stack mentioned in spec (should be in plan.md)"
  ERRORS=$((ERRORS + 1))
fi

# Check 2: Acceptance criteria are testable
if grep -q "## Acceptance Criteria" "$SPEC_FILE"; then
  # Check for vague terms
  if grep -A 50 "## Acceptance Criteria" "$SPEC_FILE" | grep -qi "easy\|simple\|user-friendly"; then
    echo "⚠ WARNING: Vague acceptance criteria detected"
    WARNINGS=$((WARNINGS + 1))
  fi
else
  echo "❌ ERROR: Missing Acceptance Criteria section"
  ERRORS=$((ERRORS + 1))
fi

# Check 3: Success metrics are measurable
if ! grep -q "## Success Metrics" "$SPEC_FILE"; then
  echo "❌ ERROR: Missing Success Metrics section"
  ERRORS=$((ERRORS + 1))
fi

# Report
echo ""
echo "Validation complete:"
echo "  Errors: $ERRORS"
echo "  Warnings: $WARNINGS"

if [ $ERRORS -gt 0 ]; then
  exit 1
fi
```

## Expected Output

- Validation errors (if any)
- Validation warnings (if any)
- Summary with error and warning counts
```

## Multi-Language Support

### Bash and PowerShell

Provide both Bash and PowerShell implementations:

**Bash** (`scripts/bash/validator.sh`):
```bash
#!/bin/bash
validate_file() {
  local file=$1
  [ -f "$file" ] && echo "✓ File exists" || echo "✗ File missing"
}
```

**PowerShell** (`scripts/powershell/validator.ps1`):
```powershell
function Validate-File {
  param([string]$FilePath)
  if (Test-Path $FilePath) {
    Write-Output "✓ File exists"
  } else {
    Write-Output "✗ File missing"
  }
}
```

**Command file** (`commands/validate.md`):
```markdown
---
scripts:
  sh: ../../scripts/bash/validator.sh
  ps: ../../scripts/powershell/validator.ps1
---

# Validate Command

```bash
# Bash version
source ../../scripts/bash/validator.sh
validate_file "$SPEC_FILE"
```

```powershell
# PowerShell version
. ..\..\scripts\powershell\validator.ps1
Validate-File -FilePath $env:SPEC_FILE
```
```

## Error Handling

### Exit Codes

Use standard exit codes:

- `0`: Success
- `1`: General error
- `2`: Misuse (invalid arguments)
- `126`: Command cannot execute
- `127`: Command not found

```bash
# Success
echo "Operation complete"
exit 0

# Error
echo "Error: Operation failed"
exit 1

# Invalid usage
if [ -z "$ARGUMENTS" ]; then
  echo "Error: Missing required argument"
  exit 2
fi
```

### Error Messages

Provide clear, actionable error messages:

```bash
# Bad
echo "Error: Failed"

# Good
echo "Error: Config file not found at $CONFIG_FILE"
echo "Run 'specify extension configure my-ext' to create config"
```

## Testing Commands

### Manual Testing

```bash
# Install extension locally
specify extension add --dev /path/to/extension

# Test command via AI agent
claude
> /speckit.my-ext.hello world

# Or test directly
cd /path/to/project
.specify/extensions/my-ext/commands/hello.md
```

### Automated Testing

**File**: `tests/test_hello.py`

```python
import subprocess
import os

def test_hello_command():
    """Test hello command execution"""
    result = subprocess.run(
        ["bash", "commands/hello.md"],
        env={"ARGUMENTS": "world"},
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0
    assert "Hello from my extension!" in result.stdout
    assert "world" in result.stdout
```

Run tests:

```bash
pytest tests/
```

## Best Practices

### 1. Validate Inputs

Always validate user inputs:

```bash
if [ -z "$ARGUMENTS" ]; then
  echo "Error: Missing required argument"
  echo "Usage: /speckit.my-ext.command <arg>"
  exit 2
fi
```

### 2. Check Prerequisites

Verify required files/tools exist:

```bash
# Check tool availability
if ! command -v docker &> /dev/null; then
  echo "Error: Docker not installed"
  exit 127
fi

# Check required files
if [ ! -f "$SPEC_FILE" ]; then
  echo "Error: Spec file not found"
  exit 1
fi
```

### 3. Provide Progress Feedback

Show progress for long-running commands:

```bash
echo "Analyzing specification..."
# ... analysis code ...
echo "✓ Analysis complete"

echo "Validating against standards..."
# ... validation code ...
echo "✓ Validation complete"
```

### 4. Handle Edge Cases

Consider edge cases and handle gracefully:

```bash
# Empty file
if [ ! -s "$SPEC_FILE" ]; then
  echo "Warning: Spec file is empty"
  exit 0  # Not an error, just warning
fi

# No current feature
if [ -z "$FEATURE_ID" ]; then
  echo "Error: Not on a feature branch"
  echo "Run '/speckit.specify' to start a new feature"
  exit 1
fi
```

### 5. Make Commands Idempotent

Commands should be safe to run multiple times:

```bash
# Create directory only if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Update file without duplicating content
if ! grep -q "JIRA: $JIRA_KEY" "$SPEC_FILE"; then
  echo "<!-- JIRA: $JIRA_KEY -->" >> "$SPEC_FILE"
fi
```
