#!/bin/bash
# Update C4 diagrams incrementally after code changes
# Usage: ./scripts/update-c4-docs.sh [feature-id]

set -euo pipefail

feature_id="${1:-unknown}"
changed_files=$(git diff --name-only HEAD~1 HEAD 2>/dev/null || echo "")

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Updating C4 diagrams (incremental)"
echo "Feature: $feature_id"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check if deepwiki is available
if ! command -v deepwiki &> /dev/null; then
    echo "⚠️  deepwiki not found in PATH"
    echo "    Install: pip install deepwiki"
    echo "    Or add to container: docker-compose exec agent bash"
    exit 1
fi

# Check if there are changed files
if [ -z "$changed_files" ]; then
    echo "✓ No files changed, skipping C4 update"
    exit 0
fi

echo "Changed files:"
echo "$changed_files" | sed 's/^/  - /'
echo

# Run incremental C4 generation
echo "Running deepwiki generate..."
if deepwiki generate . \
    --output docs/c4 \
    --incremental \
    --changed-files "$changed_files" 2>&1; then

    # Check if docs actually changed
    if git diff --quiet docs/c4/ 2>/dev/null; then
        echo "✓ No C4 diagram changes needed"
    else
        echo "✓ C4 diagrams updated"
        git diff --stat docs/c4/ 2>/dev/null || true
    fi
else
    echo "⚠️  deepwiki generation failed (non-blocking)"
    exit 0  # Non-critical failure
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
