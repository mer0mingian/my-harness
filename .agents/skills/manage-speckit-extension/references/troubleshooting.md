# Extension Troubleshooting Guide

Solutions to common issues when creating and using SpecKit extensions.

## Extension Not Loading

### Symptom
Extension doesn't appear in `specify extension list` after installation.

### Possible Causes & Solutions

#### 1. Invalid YAML Syntax

**Check:**
```bash
# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('extension.yml'))"
```

**Common YAML errors:**
```yaml
# ❌ Wrong: Missing quotes around string with colon
description: Error: Invalid

# ✓ Correct: Quote strings with special characters
description: "Error: Invalid"

# ❌ Wrong: Inconsistent indentation
extension:
  id: "my-ext"
    name: "My Extension"

# ✓ Correct: Consistent 2-space indentation
extension:
  id: "my-ext"
  name: "My Extension"
```

**Fix:**
1. Run `yamllint extension.yml` to find syntax errors
2. Fix indentation and quoting issues
3. Reinstall: `specify extension remove my-ext && specify extension add .`

#### 2. Missing Required Fields

**Check:**
```bash
# Validate manifest has required fields
grep -E "schema_version|extension.id|extension.name|requires.speckit_version" extension.yml
```

**Fix:**
Ensure all required fields present:
```yaml
schema_version: "1.0"

extension:
  id: "my-ext"           # Required
  name: "My Extension"   # Required
  version: "1.0.0"       # Required
  description: "..."     # Required

requires:
  speckit_version: ">=0.1.0"  # Required
```

#### 3. Invalid Extension ID

**Check:**
```bash
# Extension ID must be lowercase, alphanumeric + hyphens
grep "^  id:" extension.yml
```

**Common mistakes:**
```yaml
# ❌ Wrong: Uppercase
id: "My-Ext"

# ❌ Wrong: Underscore
id: "my_ext"

# ❌ Wrong: Starts with hyphen
id: "-my-ext"

# ✓ Correct
id: "my-ext"
```

**Fix:**
1. Change ID to lowercase with hyphens only
2. Update command names to match new ID
3. Reinstall extension

#### 4. File Path Issues

**Check:**
```bash
# Verify command files exist
for cmd in $(grep "file:" extension.yml | cut -d: -f2 | xargs); do
  [ -f "$cmd" ] && echo "✓ $cmd" || echo "✗ $cmd missing"
done
```

**Fix:**
Ensure all referenced files exist and paths are correct:
```yaml
provides:
  commands:
    - name: "speckit.my-ext.hello"
      file: "commands/hello.md"  # Must exist
```

---

## Commands Not Available

### Symptom
Extension installed but commands not available in AI agent (e.g., `/speckit.my-ext.hello` not found).

### Possible Causes & Solutions

#### 1. Command Name Mismatch

**Check:**
```bash
# Command names must match pattern: speckit.{ext-id}.{command}
grep "name:" extension.yml | grep "speckit\."
```

**Common mistakes:**
```yaml
# ❌ Wrong: Missing 'speckit.' prefix
- name: "my-ext.hello"

# ❌ Wrong: Extension ID mismatch
extension:
  id: "docker"
provides:
  commands:
    - name: "speckit.docker-ext.build"  # ID is 'docker', not 'docker-ext'

# ✓ Correct
extension:
  id: "my-ext"
provides:
  commands:
    - name: "speckit.my-ext.hello"
```

**Fix:**
1. Update command names to match `speckit.{ext-id}.{command}` pattern
2. Reinstall extension
3. Restart AI agent

#### 2. Command File Missing Frontmatter

**Check:**
```bash
# Command file must have YAML frontmatter
head -5 commands/hello.md
```

**Fix:**
Ensure command file has frontmatter:
```markdown
---
description: "Say hello"
---

# Hello Command

...
```

#### 3. AI Agent Not Restarted

**Fix:**
After installing extension, restart AI agent:
```bash
# Claude Code
# Exit and restart claude CLI

# Or reload plugin
claude
> /reload
```

#### 4. Wrong Integration Directory

**Check:**
```bash
# Commands should be in AI agent integration directory
ls .claude/commands/speckit.my-ext.*
ls .gemini/commands/speckit.my-ext.*
```

**Fix:**
Reinstall extension with correct integration:
```bash
specify extension remove my-ext
specify init --integration claude  # Or gemini, copilot
specify extension add my-ext
```

---

## Hooks Not Executing

### Symptom
Extension hooks don't execute at expected workflow points.

### Possible Causes & Solutions

#### 1. Invalid Hook Name

**Check:**
```bash
# Hook names must match predefined hooks
grep -A2 "^hooks:" extension.yml
```

**Valid hook names:**
- `before_specify` / `after_specify`
- `before_plan` / `after_plan`
- `before_tasks` / `after_tasks`
- `before_implement` / `after_implement`
- `before_test` / `after_test`
- `before_deploy` / `after_deploy`

**Fix:**
```yaml
# ❌ Wrong: Invalid hook name
hooks:
  on_tasks_complete:  # Not a valid hook

# ✓ Correct
hooks:
  after_tasks:
```

#### 2. Command Doesn't Exist

**Check:**
```bash
# Hook command must be defined in provides.commands
grep -A10 "^hooks:" extension.yml
grep -A10 "^provides:" extension.yml
```

**Fix:**
```yaml
provides:
  commands:
    - name: "speckit.my-ext.validate"  # Define command first

hooks:
  after_tasks:
    command: "speckit.my-ext.validate"  # Then reference in hook
```

#### 3. Hook Command Fails Silently

**Debug:**
```bash
# Run hook command manually
/speckit.my-ext.validate

# Check for errors
echo $?  # Non-zero = error
```

**Fix:**
Add error handling to hook command:
```bash
# In command file
if [ $? -ne 0 ]; then
  echo "Error: Validation failed"
  exit 1
fi
```

#### 4. Optional Hook Skipped

**Check:**
```yaml
hooks:
  after_tasks:
    command: "speckit.my-ext.validate"
    optional: true      # User can skip
    prompt: "Run validation?"
```

**If optional hook:**
- User must respond "yes" to prompt
- If skipped, won't execute (not an error)

---

## Dependency Issues

### Symptom
Extension fails with "tool not found" or "command not found" errors.

### Possible Causes & Solutions

#### 1. Missing External Tool

**Check:**
```bash
# Verify required tools installed
docker --version
kubectl --version
# etc.
```

**Fix:**
Install missing tools, or update manifest to mark as optional:
```yaml
requires:
  tools:
    - name: "docker"
      required: false  # Optional, not required
      version: ">=20.0.0"
```

#### 2. Version Mismatch

**Check:**
```bash
# Check installed version vs required version
docker --version  # Docker version 19.03.0 (required: >=20.0.0)
```

**Fix:**
- Update tool to meet version requirement
- Or adjust version requirement in manifest

#### 3. SpecKit Version Incompatibility

**Check:**
```bash
specify version  # v0.1.0
```

**Fix:**
Update SpecKit or adjust requirement:
```yaml
requires:
  speckit_version: ">=0.1.0"  # Match installed version
```

#### 4. PATH Issues

**Debug:**
```bash
# Tool installed but not in PATH
which docker  # Command not found
/usr/local/bin/docker --version  # Works

# Check PATH
echo $PATH
```

**Fix:**
Add tool directory to PATH:
```bash
export PATH=$PATH:/usr/local/bin
```

Or use full path in command:
```bash
/usr/local/bin/docker build -t myapp .
```

---

## Configuration Issues

### Symptom
Extension can't load configuration or config validation fails.

### Possible Causes & Solutions

#### 1. Config File Not Found

**Check:**
```bash
# Config should be in extension directory
ls .specify/extensions/my-ext/config.yml
```

**Fix:**
Create config from template:
```bash
cp config/my-ext-config.template.yml .specify/extensions/my-ext/config.yml
```

Or generate during extension installation (automatic if template exists in manifest).

#### 2. Invalid Config YAML

**Check:**
```bash
python -c "import yaml; yaml.safe_load(open('.specify/extensions/my-ext/config.yml'))"
```

**Fix:**
Correct YAML syntax errors in config file.

#### 3. Missing Required Config

**Check manifest:**
```yaml
provides:
  config:
    - name: "config.yml"
      template: "config/config.template.yml"
      required: true  # Config is required
```

**Fix:**
Ensure config file exists if marked required.

---

## Installation Failures

### Symptom
`specify extension add` fails with error.

### Possible Causes & Solutions

#### 1. Invalid Package Format

**Check:**
```bash
# Extension directory must have extension.yml
ls -la /path/to/extension/extension.yml
```

**Fix:**
Ensure directory structure is correct:
```
my-extension/
├── extension.yml  # Required
├── commands/      # At least one command
│   └── hello.md
└── README.md      # Recommended
```

#### 2. Network Issues (Remote Install)

**Error:**
```
Error: Failed to download extension from URL
```

**Fix:**
- Check network connectivity
- Verify URL is correct and accessible
- Try installing from local directory instead

#### 3. Permission Issues

**Error:**
```
Error: Permission denied writing to .specify/extensions/
```

**Fix:**
```bash
# Fix permissions
chmod -R u+w .specify/

# Or run with appropriate permissions
sudo specify extension add my-ext
```

---

## Testing Issues

### Symptom
Commands work in isolation but fail during workflow.

### Possible Causes & Solutions

#### 1. Missing Context Variables

**Debug:**
```bash
# Check if variables are set during workflow
echo "PROJECT_ROOT: $PROJECT_ROOT"
echo "FEATURE_ID: $FEATURE_ID"
echo "FEATURE_DIR: $FEATURE_DIR"
```

**Fix:**
Handle missing variables gracefully:
```bash
if [ -z "$FEATURE_ID" ]; then
  echo "Error: Not on a feature branch"
  echo "Run '/speckit.specify' to start a feature"
  exit 1
fi
```

#### 2. State Dependencies

**Issue:**
Command assumes previous command ran successfully.

**Fix:**
Validate prerequisites:
```bash
# Check that spec exists before analyzing
if [ ! -f "$FEATURE_DIR/spec.md" ]; then
  echo "Error: Spec not found. Run '/speckit.specify' first"
  exit 1
fi
```

#### 3. Race Conditions

**Issue:**
Hook runs before file is fully written.

**Fix:**
Add small delay or file check:
```bash
# Wait for file to be written
for i in {1..10}; do
  [ -f "$SPEC_FILE" ] && break
  sleep 0.5
done
```

---

## Debugging Tips

### Enable Verbose Logging

```bash
# Run SpecKit with verbose output
specify --verbose extension add my-ext

# Or set debug environment variable
export SPECKIT_DEBUG=1
specify extension add my-ext
```

### Check Extension Logs

```bash
# View extension execution logs
cat .specify/logs/extensions/my-ext.log
```

### Test Commands Manually

```bash
# Test command outside workflow
cd /path/to/project
export ARGUMENTS="test"
export PROJECT_ROOT=$(pwd)
export FEATURE_ID="001-test"
export FEATURE_DIR="$PROJECT_ROOT/specs/$FEATURE_ID"

bash .specify/extensions/my-ext/commands/hello.md
```

### Validate Extension

```bash
# Run built-in validation
specify extension validate /path/to/extension

# Or use yamllint
yamllint extension.yml
```

---

## Getting Help

If issues persist:

1. **Check SpecKit documentation**
   - https://github.com/github/spec-kit/tree/main/extensions

2. **Search existing issues**
   - https://github.com/github/spec-kit/issues

3. **Create new issue**
   - Include: extension.yml, error messages, steps to reproduce
   - Tag with `extension` label

4. **Community support**
   - SpecKit community forum
   - Extension authors (check repository)
