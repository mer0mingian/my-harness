# Extension Integration Patterns

Common patterns for building SpecKit extensions.

## Pattern 1: Tool Integration Extension

Integrate external tools with SpecKit workflow.

### Use Case
Wrap existing CLI tools (Docker, security scanners, linters) to work with SpecKit artifacts.

### Structure
```
tool-integration/
├── extension.yml
├── commands/
│   ├── run-tool.md           # Execute tool
│   ├── validate.md           # Validate tool output
│   └── configure.md          # Configure tool
├── scripts/
│   └── bash/
│       └── tool-wrapper.sh   # Tool execution wrapper
└── config/
    └── tool-config.template.yml
```

### Example: Docker Integration

**extension.yml:**
```yaml
schema_version: "1.0"

extension:
  id: "docker"
  name: "Docker Integration"
  version: "1.0.0"
  description: "Containerize SpecKit projects"

requires:
  speckit_version: ">=0.1.0"
  tools:
    - name: "docker"
      required: true
      version: ">=20.0.0"

provides:
  commands:
    - name: "speckit.docker.build"
      file: "commands/build.md"
    - name: "speckit.docker.run"
      file: "commands/run.md"

hooks:
  after_implement:
    command: "speckit.docker.build"
    optional: true
    prompt: "Build Docker image?"
```

**commands/build.md:**
```markdown
---
description: "Build Docker image for project"
tools:
  - 'bash/execute'
---

# Docker Build Command

Builds Docker image based on project structure.

## Steps

1. Detect project type (Node, Python, .NET, etc.)
2. Generate appropriate Dockerfile if missing
3. Build Docker image
4. Tag with feature ID

```bash
PROJECT_TYPE=$(detect_project_type)
IMAGE_NAME="${FEATURE_ID}-app"

# Generate Dockerfile if missing
if [ ! -f "Dockerfile" ]; then
  generate_dockerfile "$PROJECT_TYPE" > Dockerfile
fi

# Build image
docker build -t "$IMAGE_NAME:latest" .

echo "✓ Built image: $IMAGE_NAME:latest"
```
```

### When to Use
- Wrapping existing tools (Docker, Terraform, linters)
- Adding deployment capabilities (AWS, Azure, K8s)
- Integrating security scanners (Snyk, Trivy)

---

## Pattern 2: Workflow Extension

Add custom workflow steps to SpecKit phases.

### Use Case
Insert organization-specific steps into standard SpecKit workflow (compliance checks, approvals, notifications).

### Structure
```
workflow-ext/
├── extension.yml
├── commands/
│   ├── pre-validate.md       # Pre-validation step
│   ├── custom-check.md       # Custom checks
│   └── post-process.md       # Post-processing
└── config/
    └── workflow-rules.template.yml
```

### Example: Compliance Workflow

**extension.yml:**
```yaml
schema_version: "1.0"

extension:
  id: "compliance"
  name: "Compliance Workflow"
  version: "1.0.0"
  description: "Add HIPAA compliance checks to workflow"

requires:
  speckit_version: ">=0.1.0"

provides:
  commands:
    - name: "speckit.compliance.check"
      file: "commands/check.md"

hooks:
  before_plan:
    command: "speckit.compliance.check"
    optional: false  # Required for compliance
```

**commands/check.md:**
```markdown
---
description: "Validate HIPAA compliance"
---

# Compliance Check Command

Validates specification meets HIPAA requirements.

## Steps

1. Check for PHI handling
2. Validate encryption requirements
3. Check audit logging plan
4. Validate data retention policy

```bash
SPEC_FILE="$FEATURE_DIR/spec.md"
ERRORS=0

# Check 1: PHI handling documented
if ! grep -qi "PHI\|protected health information" "$SPEC_FILE"; then
  echo "⚠ WARNING: No PHI handling documented"
fi

# Check 2: Encryption mentioned
if ! grep -qi "encrypt" "$SPEC_FILE"; then
  echo "❌ ERROR: Encryption requirements missing"
  ERRORS=$((ERRORS + 1))
fi

# Check 3: Audit logging
if ! grep -qi "audit\|logging" "$SPEC_FILE"; then
  echo "❌ ERROR: Audit logging not specified"
  ERRORS=$((ERRORS + 1))
fi

if [ $ERRORS -gt 0 ]; then
  echo "Compliance check failed. Cannot proceed to planning."
  exit 1
fi

echo "✓ Compliance check passed"
```
```

### When to Use
- Adding compliance checks (HIPAA, SOC2, GDPR)
- Implementing approval gates
- Adding custom validation steps
- Integrating notification systems

---

## Pattern 3: Domain-Specific Extension

Encode domain knowledge and best practices.

### Use Case
Capture organization-specific patterns, templates, and standards (microservices patterns, API standards, testing frameworks).

### Structure
```
domain-ext/
├── extension.yml
├── commands/
│   ├── generate-spec.md      # Domain-specific spec generation
│   ├── validate-rules.md     # Domain rule validation
│   └── apply-template.md     # Apply domain templates
├── templates/
│   ├── microservice-spec.md
│   ├── api-spec.md
│   └── data-model.md
└── config/
    └── domain-rules.template.yml
```

### Example: Microservices Extension

**extension.yml:**
```yaml
schema_version: "1.0"

extension:
  id: "microservices"
  name: "Microservices Patterns"
  version: "1.0.0"
  description: "Apply microservices best practices"

requires:
  speckit_version: ">=0.1.0"

provides:
  commands:
    - name: "speckit.microservices.spec"
      file: "commands/generate-spec.md"
    - name: "speckit.microservices.validate"
      file: "commands/validate-rules.md"

hooks:
  after_specify:
    command: "speckit.microservices.validate"
    optional: false
```

**commands/validate-rules.md:**
```markdown
---
description: "Validate microservices design rules"
---

# Microservices Validation Command

Validates spec follows microservices principles.

## Rules

1. Single responsibility (one domain per service)
2. Database per service (no shared databases)
3. Async communication preferred
4. Health checks specified
5. Circuit breakers for external calls

```bash
SPEC_FILE="$FEATURE_DIR/spec.md"
ERRORS=0
WARNINGS=0

# Rule 1: Check for clear domain boundary
DOMAIN_COUNT=$(grep -c "^## Domain:" "$SPEC_FILE" || echo "0")
if [ "$DOMAIN_COUNT" -ne 1 ]; then
  echo "❌ ERROR: Must have exactly one domain (found $DOMAIN_COUNT)"
  ERRORS=$((ERRORS + 1))
fi

# Rule 2: Database per service
if grep -qi "shared database" "$SPEC_FILE"; then
  echo "❌ ERROR: Shared database detected (violates microservices principle)"
  ERRORS=$((ERRORS + 1))
fi

# Rule 3: Async communication
if ! grep -qi "event\|message\|queue" "$SPEC_FILE"; then
  echo "⚠ WARNING: No async communication mentioned (consider events/messaging)"
  WARNINGS=$((WARNINGS + 1))
fi

# Rule 4: Health checks
if ! grep -qi "health check\|readiness\|liveness" "$SPEC_FILE"; then
  echo "⚠ WARNING: No health checks specified"
  WARNINGS=$((WARNINGS + 1))
fi

# Rule 5: Circuit breakers
if grep -qi "external api\|third.party" "$SPEC_FILE"; then
  if ! grep -qi "circuit breaker\|retry\|fallback" "$SPEC_FILE"; then
    echo "⚠ WARNING: External calls without circuit breaker pattern"
    WARNINGS=$((WARNINGS + 1))
  fi
fi

echo ""
echo "Validation complete: $ERRORS errors, $WARNINGS warnings"

if [ $ERRORS -gt 0 ]; then
  exit 1
fi
```
```

### When to Use
- Encoding organizational standards (API design, testing)
- Domain-specific templates (e-commerce, healthcare, fintech)
- Best practices enforcement (security, performance)

---

## Pattern 4: Quality Gate Extension

Add quality checks at workflow checkpoints.

### Use Case
Automated quality validation (test coverage, code quality, security scanning).

### Structure
```
quality-gate/
├── extension.yml
├── commands/
│   ├── coverage-check.md     # Test coverage validation
│   ├── security-scan.md      # Security scanning
│   └── complexity-check.md   # Code complexity analysis
└── config/
    └── quality-thresholds.template.yml
```

### Example: Test Coverage Gate

**extension.yml:**
```yaml
schema_version: "1.0"

extension:
  id: "quality"
  name: "Quality Gates"
  version: "1.0.0"
  description: "Enforce quality thresholds"

requires:
  speckit_version: ">=0.1.0"
  tools:
    - name: "pytest"
      required: true
    - name: "coverage"
      required: true

provides:
  commands:
    - name: "speckit.quality.coverage"
      file: "commands/coverage-check.md"

hooks:
  after_implement:
    command: "speckit.quality.coverage"
    optional: false  # Required gate
```

**commands/coverage-check.md:**
```markdown
---
description: "Check test coverage meets threshold"
tools:
  - 'bash/execute'
---

# Coverage Check Command

Validates test coverage meets minimum threshold.

## Steps

1. Run tests with coverage
2. Extract coverage percentage
3. Compare against threshold
4. Fail if below threshold

```bash
CONFIG_FILE="$EXTENSION_CONFIG_DIR/quality-config.yml"
THRESHOLD=$(grep "coverage_threshold:" "$CONFIG_FILE" | cut -d: -f2 | xargs)
THRESHOLD=${THRESHOLD:-80}  # Default 80% if not configured

echo "Running tests with coverage..."
coverage run -m pytest tests/
COVERAGE=$(coverage report | tail -1 | awk '{print $NF}' | sed 's/%//')

echo ""
echo "Coverage: ${COVERAGE}%"
echo "Threshold: ${THRESHOLD}%"

if [ "$COVERAGE" -lt "$THRESHOLD" ]; then
  echo "❌ FAILED: Coverage below threshold"
  exit 1
fi

echo "✓ Coverage gate passed"
```
```

### When to Use
- Test coverage requirements
- Code quality thresholds (complexity, duplication)
- Security scanning (SAST, dependency scanning)
- Performance benchmarks

---

## Pattern 5: Integration/Sync Extension

Bidirectional sync with external systems.

### Use Case
Keep SpecKit artifacts in sync with project management tools (Jira, GitHub Issues, Linear).

### Structure
```
sync-ext/
├── extension.yml
├── commands/
│   ├── sync-to-external.md   # Push to external system
│   ├── sync-from-external.md # Pull from external system
│   └── configure-sync.md     # Setup sync
├── scripts/
│   └── bash/
│       └── sync-helper.sh
└── config/
    └── sync-config.template.yml
```

### Example: Jira Sync

**extension.yml:**
```yaml
schema_version: "1.0"

extension:
  id: "jira"
  name: "Jira Integration"
  version: "1.0.0"
  description: "Bidirectional Jira sync"

requires:
  speckit_version: ">=0.1.0"
  tools:
    - name: "jq"
      required: true

provides:
  commands:
    - name: "speckit.jira.sync"
      file: "commands/sync.md"
    - name: "speckit.jira.pull"
      file: "commands/pull.md"

hooks:
  after_specify:
    command: "speckit.jira.sync"
    optional: true
    prompt: "Sync to Jira?"
```

**commands/sync.md:**
```markdown
---
description: "Sync spec to Jira"
scripts:
  sh: ../../scripts/bash/jira-helper.sh
---

# Jira Sync Command

Creates or updates Jira issue from spec.

```bash
source ../../scripts/bash/jira-helper.sh

SPEC_FILE="$FEATURE_DIR/spec.md"
FEATURE_NAME=$(grep "^# " "$SPEC_FILE" | head -1 | sed 's/^# //')

# Check if already synced
JIRA_KEY=$(grep "<!-- JIRA:" "$SPEC_FILE" | sed 's/.*JIRA: \(.*\) -->/\1/')

if [ -n "$JIRA_KEY" ]; then
  echo "Updating existing Jira issue: $JIRA_KEY"
  update_jira_issue "$JIRA_KEY" "$SPEC_FILE"
else
  echo "Creating new Jira issue"
  JIRA_KEY=$(create_jira_issue "$FEATURE_NAME" "$SPEC_FILE")
  
  # Store reference in spec
  echo "" >> "$SPEC_FILE"
  echo "<!-- JIRA: $JIRA_KEY -->" >> "$SPEC_FILE"
fi

echo "✓ Synced to Jira: $JIRA_KEY"
```
```

### When to Use
- Project management integration (Jira, Linear, Azure DevOps)
- Documentation sync (Confluence, Notion)
- Version control integration (GitHub Issues, GitLab)

---

## Combining Patterns

Extensions can combine multiple patterns:

### Example: Full-Stack Extension

```
fullstack-ext/
├── extension.yml
├── commands/
│   ├── generate-api.md       # Domain pattern
│   ├── validate-api.md       # Quality gate pattern
│   ├── deploy-api.md         # Tool integration pattern
│   └── sync-docs.md          # Integration pattern
└── config/
    └── fullstack-config.yml
```

**Combines:**
1. **Domain pattern**: API generation following org standards
2. **Quality gate**: API validation (OpenAPI compliance)
3. **Tool integration**: Deployment to AWS/Azure
4. **Integration**: Sync API docs to documentation portal

## Best Practices

### 1. Keep Extensions Focused
- One clear purpose per extension
- Don't bundle unrelated functionality
- Easier to maintain and test

### 2. Make Extensions Composable
- Extensions should work together
- Don't duplicate functionality from other extensions
- Use extension dependencies when needed

### 3. Provide Configuration
- Allow users to customize behavior
- Provide sensible defaults
- Document all configuration options

### 4. Handle Errors Gracefully
- Validate prerequisites before executing
- Provide clear error messages
- Don't fail silently

### 5. Document Integration Points
- Explain when hooks execute
- Document expected inputs/outputs
- Provide usage examples
