#!/usr/bin/env bash
set -euo pipefail

# Installation hook for harness-tdd-workflow SpecKit extension
# Runs when: specify extension add harness-tdd-workflow

EXTENSION_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORKSPACE_ROOT="$(pwd)"
SPECIFY_DIR="${WORKSPACE_ROOT}/.specify"

echo "Installing harness-tdd-workflow extension..."

# Create .specify/ directory if missing
mkdir -p "${SPECIFY_DIR}/templates"

# Copy config template to workspace
if [[ ! -f "${SPECIFY_DIR}/harness-tdd-config.yml" ]]; then
  cp "${EXTENSION_DIR}/harness-tdd-config.yml.template" \
     "${SPECIFY_DIR}/harness-tdd-config.yml"
  echo "✓ Created .specify/harness-tdd-config.yml"
else
  echo "⚠ .specify/harness-tdd-config.yml already exists (not overwritten)"
fi

# Copy artifact templates to workspace
echo "Copying artifact templates..."
for template in test-design implementation-notes arch-review code-review workflow-summary; do
  if [[ ! -f "${SPECIFY_DIR}/templates/${template}-template.md" ]]; then
    if [[ -f "${EXTENSION_DIR}/templates/${template}-template.md" ]]; then
      cp "${EXTENSION_DIR}/templates/${template}-template.md" \
         "${SPECIFY_DIR}/templates/"
      echo "  ✓ ${template}-template.md"
    else
      echo "  ⚠ ${template}-template.md not found in extension (skipped)"
    fi
  else
    echo "  - ${template}-template.md (already exists)"
  fi
done

# Create artifact directories (placeholders)
mkdir -p "${SPECIFY_DIR}/../docs/tests/test-design"
mkdir -p "${SPECIFY_DIR}/../docs/implementation"
mkdir -p "${SPECIFY_DIR}/../docs/reviews/arch-review"
mkdir -p "${SPECIFY_DIR}/../docs/reviews/code-review"
mkdir -p "${SPECIFY_DIR}/../docs/workflow"

echo "✓ Installation complete!"
echo ""
echo "Next steps:"
echo "  1. Review .specify/harness-tdd-config.yml"
echo "  2. Customize artifact templates in .specify/templates/"
echo "  3. Run: specify multi-agent test <feature-id>"
