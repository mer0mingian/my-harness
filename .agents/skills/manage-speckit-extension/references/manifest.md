# Extension Manifest Reference

Complete specification for `extension.yml` manifest files.

## Required Fields

### schema_version

Extension manifest schema version. Currently: `"1.0"`

```yaml
schema_version: "1.0"
```

### extension

Extension metadata block.

**Required sub-fields:**
- `id`: Extension identifier (lowercase, alphanumeric, hyphens)
- `name`: Human-readable name
- `version`: Semantic version (MAJOR.MINOR.PATCH)
- `description`: Short description

**Optional sub-fields:**
- `author`: Extension author
- `repository`: Source code URL
- `homepage`: Documentation URL
- `license`: SPDX license identifier (MIT, Apache-2.0, etc.)

```yaml
extension:
  id: "my-ext"                          # Lowercase, alphanumeric + hyphens
  name: "My Extension"
  version: "1.0.0"                      # Semantic versioning
  description: "Detailed description"
  author: "Your Name"
  repository: "https://github.com/you/speckit-my-ext"
  homepage: "https://docs.example.com"
  license: "MIT"
```

### requires

Compatibility requirements.

**Required:**
- `speckit_version`: Semantic version specifier (e.g., ">=0.1.0,<2.0.0")

**Optional:**
- `tools`: External tools required (array of tool objects)
- `commands`: Core spec-kit commands needed (array of command names)
- `scripts`: Core scripts required (array of script names)

```yaml
requires:
  speckit_version: ">=0.1.0"            # Minimum spec-kit version
  tools:                                # External tools required
    - name: "my-tool"
      required: true
      version: ">=1.0.0"
  commands:                             # Core SpecKit commands needed
    - "speckit.tasks"
  scripts:                              # Core scripts required
    - "generate-spec.sh"
```

**Tool object structure:**
```yaml
- name: "docker"
  required: true        # If false, tool is optional
  version: ">=20.0.0"   # Semantic version constraint
```

### provides

What the extension provides.

**Optional sub-fields:**
- `commands`: Array of command objects (at least one command or hook required)
- `config`: Array of config file objects

```yaml
provides:
  commands:
    - name: "speckit.my-ext.hello"      # Must follow: speckit.{ext-id}.{cmd}
      file: "commands/hello.md"
      description: "Say hello"
      aliases:                          # Optional, same pattern
        - "speckit.my-ext.hi"
    - name: "speckit.my-ext.goodbye"
      file: "commands/goodbye.md"
      description: "Say goodbye"
  
  config:                               # Config files
    - name: "my-ext-config.yml"
      template: "config/my-ext-config.template.yml"
      description: "Extension configuration"
      required: false
```

**Command object structure:**
- `name`: Command name (must match `speckit.{ext-id}.{command}`)
- `file`: Path to command file (relative to extension root)
- `description`: Command description (optional)
- `aliases`: Alternative command names (optional, must match pattern)

**Config object structure:**
- `name`: Config file name
- `template`: Path to template file
- `description`: Config description
- `required`: Boolean (default: false)

## Optional Fields

### hooks

Integration hooks for automatic execution.

**Available hook points:**
- `before_specify` / `after_specify`: Before/after spec generation
- `before_plan` / `after_plan`: Before/after implementation planning
- `before_tasks` / `after_tasks`: Before/after task creation
- `before_implement` / `after_implement`: Before/after implementation
- `before_test` / `after_test`: Before/after testing
- `before_deploy` / `after_deploy`: Before/after deployment

**Hook object structure:**
```yaml
after_tasks:
  command: "speckit.my-ext.validate"    # Command to run
  optional: true                        # Whether hook can be skipped
  prompt: "Run validation?"             # Prompt text if optional
```

**Example:**
```yaml
hooks:
  after_tasks:
    command: "speckit.my-ext.hello"
    optional: true
    prompt: "Run hello command?"
  before_specify:
    command: "speckit.my-ext.validate"
    optional: false
```

### tags

Array of strings for catalog search and discovery.

```yaml
tags:
  - "example"
  - "utility"
  - "validation"
  - "security"
  - "integration"
```

## Complete Example

```yaml
schema_version: "1.0"

extension:
  id: "docker-integration"
  name: "Docker Integration"
  version: "1.2.0"
  description: "Integrate Docker containerization into SpecKit workflows"
  author: "DevOps Team"
  repository: "https://github.com/org/speckit-docker"
  homepage: "https://docs.example.com/speckit-docker"
  license: "MIT"

requires:
  speckit_version: ">=0.1.0"
  tools:
    - name: "docker"
      required: true
      version: ">=20.0.0"
    - name: "docker-compose"
      required: false
      version: ">=2.0.0"
  commands:
    - "speckit.plan"
    - "speckit.implement"

provides:
  commands:
    - name: "speckit.docker.build"
      file: "commands/build.md"
      description: "Build Docker image for project"
    - name: "speckit.docker.run"
      file: "commands/run.md"
      description: "Run project in Docker container"
      aliases:
        - "speckit.docker.start"
    - name: "speckit.docker.compose"
      file: "commands/compose.md"
      description: "Generate docker-compose.yml"
  
  config:
    - name: "docker-config.yml"
      template: "config/docker-config.template.yml"
      description: "Docker build and runtime configuration"
      required: true

hooks:
  after_plan:
    command: "speckit.docker.compose"
    optional: true
    prompt: "Generate docker-compose.yml?"
  after_implement:
    command: "speckit.docker.build"
    optional: true
    prompt: "Build Docker image?"

tags:
  - "docker"
  - "containerization"
  - "deployment"
  - "devops"
```

## Validation Rules

### Extension ID Rules
- Must be lowercase
- Only alphanumeric characters and hyphens
- 3-30 characters long
- Must start with letter
- Cannot end with hyphen

**Valid:**
- `my-ext`
- `docker-integration`
- `sec-scan`

**Invalid:**
- `My-Ext` (uppercase)
- `my_ext` (underscore)
- `-my-ext` (starts with hyphen)
- `my-ext-` (ends with hyphen)
- `m` (too short)

### Command Name Rules
- Must follow pattern: `speckit.{ext-id}.{command}`
- Command part: lowercase, alphanumeric, hyphens
- Examples: `speckit.docker.build`, `speckit.sec.scan`

### Version Rules
- Must follow semantic versioning: MAJOR.MINOR.PATCH
- Valid: `1.0.0`, `2.3.1`, `0.1.0-beta`
- Invalid: `1.0`, `v1.0.0`, `1.0.0.0`

### File Path Rules
- Relative to extension root
- Use forward slashes (/) even on Windows
- No leading slash
- Valid: `commands/hello.md`, `scripts/bash/helper.sh`
- Invalid: `/commands/hello.md`, `commands\hello.md`

## Manifest Validation

SpecKit validates manifests during installation:

```bash
# Explicit validation without installation
specify extension validate /path/to/extension

# Validation happens automatically during install
specify extension add /path/to/extension
```

**Common validation errors:**

1. **Invalid YAML syntax**
   ```
   Error: extension.yml is not valid YAML
   Line 5: unexpected token
   ```

2. **Missing required fields**
   ```
   Error: Missing required field 'extension.id'
   Error: Missing required field 'requires.speckit_version'
   ```

3. **Invalid extension ID**
   ```
   Error: Extension ID 'My_Ext' is invalid
   Must be lowercase alphanumeric with hyphens
   ```

4. **Command name mismatch**
   ```
   Error: Command 'speckit.other.cmd' does not match extension ID 'my-ext'
   Must be: speckit.my-ext.*
   ```

5. **File not found**
   ```
   Error: Command file 'commands/hello.md' not found
   ```

6. **Invalid version**
   ```
   Error: Version '1.0' is not valid semantic version
   Must be: MAJOR.MINOR.PATCH (e.g., 1.0.0)
   ```

## Migration from Older Versions

If updating an extension from older schema versions:

### From schema 0.x to 1.0

**Changes:**
1. Added `schema_version` field (required)
2. Hook syntax changed from `on_*` to `before_*/after_*`
3. Config templates now use `provides.config` array
4. Tool requirements now support optional tools

**Migration example:**

**Old (0.x):**
```yaml
extension:
  id: "my-ext"
  version: "1.0.0"

commands:
  - name: "my-ext.hello"
    file: "commands/hello.md"

on_tasks_complete:
  command: "my-ext.validate"
```

**New (1.0):**
```yaml
schema_version: "1.0"

extension:
  id: "my-ext"
  version: "2.0.0"  # Bump major version for breaking changes

provides:
  commands:
    - name: "speckit.my-ext.hello"  # Add 'speckit.' prefix
      file: "commands/hello.md"

hooks:
  after_tasks:  # Rename from on_tasks_complete
    command: "speckit.my-ext.validate"
    optional: true
```
