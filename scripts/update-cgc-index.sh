#!/bin/bash
# Update Code Graph Context index incrementally after code changes
# Usage: ./scripts/update-cgc-index.sh [feature-id]

set -euo pipefail

feature_id="${1:-unknown}"
changed_files=$(git diff --name-only HEAD~1 HEAD 2>/dev/null | tr '\n' ',' || echo "")

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Updating CGC index (incremental)"
echo "Feature: $feature_id"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check if cgc is available
if ! command -v cgc &> /dev/null; then
    echo "⚠️  cgc not found in PATH"
    echo "    Install: pip install code-graph-context"
    echo "    Or add to container: docker-compose exec agent bash"
    exit 1
fi

# Check if there are changed files
if [ -z "$changed_files" ]; then
    echo "✓ No files changed, skipping CGC update"
    exit 0
fi

# Remove trailing comma
changed_files="${changed_files%,}"

echo "Changed files: $changed_files"
echo

# Run incremental CGC indexing
echo "Running cgc index..."
if cgc index \
    --incremental \
    --files "$changed_files" \
    --tag "implementation:$feature_id" 2>&1; then

    echo "✓ CGC index updated"

    # Show index stats if available
    if cgc stats &> /dev/null; then
        echo
        cgc stats | head -5
    fi
else
    echo "⚠️  CGC indexing failed (non-blocking)"
    exit 0  # Non-critical failure
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
