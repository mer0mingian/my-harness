#!/bin/bash
# Validate documentation automation setup
# Usage: ./scripts/validate-doc-automation.sh

set -euo pipefail

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Documentation Automation Setup Validation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo

errors=0
warnings=0

# Check 1: Required scripts exist
echo "✓ Checking required scripts..."
if [ -f "scripts/update-c4-docs.sh" ]; then
    echo "  ✓ update-c4-docs.sh found"
else
    echo "  ✗ update-c4-docs.sh missing"
    ((errors++))
fi

if [ -f "scripts/update-cgc-index.sh" ]; then
    echo "  ✓ update-cgc-index.sh found"
else
    echo "  ✗ update-cgc-index.sh missing"
    ((errors++))
fi

echo

# Check 2: Scripts are executable
echo "✓ Checking script permissions..."
if [ -x "scripts/update-c4-docs.sh" ]; then
    echo "  ✓ update-c4-docs.sh is executable"
else
    echo "  ⚠ update-c4-docs.sh not executable (run: chmod +x scripts/*.sh)"
    ((warnings++))
fi

if [ -x "scripts/update-cgc-index.sh" ]; then
    echo "  ✓ update-cgc-index.sh is executable"
else
    echo "  ⚠ update-cgc-index.sh not executable (run: chmod +x scripts/*.sh)"
    ((warnings++))
fi

echo

# Check 3: Required tools installed
echo "✓ Checking required tools..."
if command -v deepwiki &> /dev/null; then
    version=$(deepwiki --version 2>&1 || echo "unknown")
    echo "  ✓ deepwiki installed: $version"
else
    echo "  ⚠ deepwiki not found (install: pip install deepwiki)"
    ((warnings++))
fi

if command -v cgc &> /dev/null; then
    version=$(cgc --version 2>&1 || echo "unknown")
    echo "  ✓ cgc installed: $version"
else
    echo "  ⚠ cgc not found (install: pip install code-graph-context)"
    ((warnings++))
fi

echo

# Check 4: Command specification exists
echo "✓ Checking command specification..."
if [ -f "spec-kit-multi-agent-tdd/commands/update-docs.md" ]; then
    echo "  ✓ update-docs.md command spec found"
else
    echo "  ✗ update-docs.md command spec missing"
    ((errors++))
fi

echo

# Check 5: Documentation exists
echo "✓ Checking documentation..."
if [ -f "spec-kit-multi-agent-tdd/docs/AUTOMATION.md" ]; then
    echo "  ✓ AUTOMATION.md guide found"
else
    echo "  ✗ AUTOMATION.md guide missing"
    ((errors++))
fi

if [ -f "spec-kit-multi-agent-tdd/.specify/hooks.yml.example" ]; then
    echo "  ✓ hooks.yml.example found"
else
    echo "  ⚠ hooks.yml.example missing"
    ((warnings++))
fi

echo

# Check 6: Output directories
echo "✓ Checking output directories..."
if [ -d "docs/c4" ]; then
    echo "  ✓ docs/c4/ exists"
else
    echo "  ⚠ docs/c4/ missing (will be created on first run)"
fi

if [ -d ".cgc" ]; then
    echo "  ✓ .cgc/ exists"
else
    echo "  ⚠ .cgc/ missing (will be created on first run)"
fi

echo

# Check 7: Git repository
echo "✓ Checking git setup..."
if git rev-parse --git-dir > /dev/null 2>&1; then
    echo "  ✓ Git repository detected"
else
    echo "  ✗ Not a git repository"
    ((errors++))
fi

echo

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Validation Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ $errors -eq 0 ] && [ $warnings -eq 0 ]; then
    echo "✅ All checks passed! Setup is complete."
    echo
    echo "Try running:"
    echo "  /speckit.matd.update-docs test-001"
    exit 0
elif [ $errors -eq 0 ]; then
    echo "⚠️  Setup mostly complete with $warnings warnings"
    echo
    echo "Warnings are non-blocking. You can:"
    echo "  1. Fix warnings (recommended)"
    echo "  2. Proceed anyway (tools will fail gracefully)"
    echo
    echo "Next steps:"
    echo "  - Install missing tools: pip install deepwiki code-graph-context"
    echo "  - Fix permissions: chmod +x scripts/*.sh"
    exit 0
else
    echo "❌ Setup incomplete: $errors errors, $warnings warnings"
    echo
    echo "Fix errors before using automation:"
    echo "  - Ensure all scripts exist in scripts/"
    echo "  - Verify command specification in commands/"
    echo "  - Confirm git repository setup"
    exit 1
fi
