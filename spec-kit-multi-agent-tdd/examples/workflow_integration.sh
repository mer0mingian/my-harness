#!/bin/bash
# Example: Integrating Test Evidence Parser into TDD Workflow
#
# This script demonstrates how to use the test evidence parser
# to automate TDD workflow gates (Steps 7, 8, 10).

set -e

PROJECT_DIR="$(dirname "$0")/.."
cd "$PROJECT_DIR"

PARSER="lib/parse_test_evidence.py"

echo "=========================================="
echo "TDD Workflow with Test Evidence Parser"
echo "=========================================="
echo ""

# Step 7: Verify RED State
echo "Step 7: Writing test first (RED state expected)..."
echo ""

# Simulate running tests (would be: pytest tests/)
# For demo, use fixture
TEST_OUTPUT="tests/fixtures/pytest_red_missing_behavior.txt"

echo "Running tests..."
python "$PARSER" --input "$TEST_OUTPUT" --format summary

# Check exit code
EXIT_CODE=$?

if [ $EXIT_CODE -eq 1 ]; then
    echo ""
    echo "✓ Tests are RED (expected TDD state)"
    echo "  Failure codes detected: MISSING_BEHAVIOR"
    echo "  Ready to proceed to implementation"
elif [ $EXIT_CODE -eq 2 ]; then
    echo ""
    echo "✗ Tests are BROKEN - escalate to human"
    echo "  Fix test or environment issues before proceeding"
    exit 1
elif [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo "✗ Tests are GREEN - but we haven't implemented yet!"
    echo "  Check test is actually testing the right thing"
    exit 1
else
    echo ""
    echo "✗ Parser error"
    exit 1
fi

echo ""
echo "----------------------------------------"
echo ""

# Step 8: Verify RED→GREEN Transition
echo "Step 8: Implementing feature..."
echo "(In real workflow, implement feature here)"
echo ""

# Simulate GREEN state after implementation
TEST_OUTPUT_GREEN="tests/fixtures/pytest_green.txt"

echo "Running tests again..."
python "$PARSER" --input "$TEST_OUTPUT_GREEN" --format summary

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo "✓ Tests are GREEN - implementation successful!"
    echo "  RED→GREEN transition verified"
elif [ $EXIT_CODE -eq 1 ]; then
    echo ""
    echo "✗ Tests still RED - implementation incomplete"
    exit 1
elif [ $EXIT_CODE -eq 2 ]; then
    echo ""
    echo "✗ Tests are BROKEN - implementation broke something"
    exit 1
fi

echo ""
echo "----------------------------------------"
echo ""

# Step 10: Generate Evidence for Commit
echo "Step 10: Generating test evidence for commit..."
echo ""

# Generate evidence report
EVIDENCE_FILE="/tmp/test_evidence_$(date +%s).txt"
python "$PARSER" --input "$TEST_OUTPUT_GREEN" --format summary > "$EVIDENCE_FILE"

echo "Evidence report saved to: $EVIDENCE_FILE"
echo ""
echo "Commit message template:"
echo "---"
cat << EOF
feat: implement login feature

Implemented user login functionality with authentication.

Test Evidence:
$(cat "$EVIDENCE_FILE")

Co-Authored-By: Test Evidence Parser (automated)
EOF
echo "---"

echo ""
echo "=========================================="
echo "TDD Workflow Complete! ✓"
echo "=========================================="
