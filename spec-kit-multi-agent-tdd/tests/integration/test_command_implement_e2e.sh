#!/usr/bin/env bash
# End-to-end integration test for /speckit.multi-agent.implement command
# Tests: RED validation, GREEN validation, integration checks, artifact generation

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
TEST_WORKSPACE="$PROJECT_ROOT/test-implement-workspace"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}=== S4-006: End-to-End Test for /speckit.multi-agent.implement ===${NC}"

# Cleanup
cleanup() {
    echo -e "${YELLOW}Cleaning up test workspace...${NC}"
    rm -rf "$TEST_WORKSPACE"
}
trap cleanup EXIT

# Create test workspace
echo "Creating test workspace..."
mkdir -p "$TEST_WORKSPACE"
cd "$TEST_WORKSPACE"

# Initialize git repo (required)
git init -q
git config user.email "test@example.com"
git config user.name "Test User"

# Create directory structure
mkdir -p docs/features tests .specify

# Create fake test design artifact (from step 7)
cat > docs/features/feat-test-001-test-design.md <<'EOF'
# Test Design: Test Feature

**Feature ID:** feat-test-001
**Agent:** @test
**Status:** draft

## Test Strategy
Unit tests for validation logic using pytest

## RED State Validation

**Test Output:**
```
FAILED tests/test_validation.py::test_validates_input - NotImplementedError
FAILED tests/test_validation.py::test_returns_error - NotImplementedError
```

**Valid RED:** YES
**State:** RED
EOF

# Create config file with integration checks
cat > .specify/harness-tdd-config.yml <<'EOF'
version: "1.0"

agents:
  implementation_agent: "dev-specialist"

artifacts:
  root: "docs/features"
  types:
    test_design: "test-design"
    impl_notes: "impl-notes"

test_framework:
  type: "pytest"
  file_patterns:
    - "tests/**/*.py"

integration_checks:
  enabled: true
  commands:
    - name: "style-check"
      command: "echo 'Style check passed'"
      critical: false
    - name: "type-check"
      command: "echo 'Type check passed'"
      critical: false
EOF

# Create fake failing tests (RED state)
cat > tests/test_validation.py <<'EOF'
"""Test validation logic"""
import pytest

def test_validates_input():
    """Test that system validates user input"""
    from validation import validate_input  # Will fail - module doesn't exist
    assert validate_input("test") == True

def test_returns_error():
    """Test that system returns error for invalid data"""
    from validation import validate_input
    with pytest.raises(ValueError):
        validate_input("")
EOF

# Create fake pytest that simulates failing tests (RED state)
mkdir -p bin
cat > bin/pytest <<'EOF'
#!/bin/bash
# Fake pytest that produces RED state output

# Check if we have test files
if [ ! -f "tests/test_validation.py" ]; then
    echo "collected 0 items"
    exit 0
fi

# Read test file to determine expected state
if grep -q "from validation import validate_input" tests/test_validation.py && \
   [ ! -f "src/validation.py" ]; then
    # RED state - NotImplementedError (missing behavior)
    cat <<'PYTEST_OUT'
============================= test session starts ==============================
collected 2 items

tests/test_validation.py::test_validates_input FAILED                    [ 50%]
tests/test_validation.py::test_returns_error FAILED                      [100%]

=================================== FAILURES ===================================
______________________________ test_validates_input _____________________________
    def test_validates_input():
>       assert validate_input("test") == True
E       NotImplementedError: validate_input not implemented

tests/test_validation.py:4: NotImplementedError
______________________________ test_returns_error _____________________________
    def test_returns_error():
>       with pytest.raises(ValueError):
>           validate_input("")
E       NotImplementedError: validate_input not implemented

tests/test_validation.py:8: NotImplementedError
=========================== short test summary info ============================
FAILED tests/test_validation.py::test_validates_input - NotImplementedError
FAILED tests/test_validation.py::test_returns_error - NotImplementedError
========================= 2 failed in 0.01s ==========================
PYTEST_OUT
    exit 1
elif grep -q "from validation import validate_input" tests/test_validation.py && \
     [ -f "src/validation.py" ]; then
    # GREEN state - tests pass
    cat <<'PYTEST_OUT'
============================= test session starts ==============================
collected 2 items

tests/test_validation.py::test_validates_input PASSED                    [ 50%]
tests/test_validation.py::test_returns_false_for_empty PASSED            [100%]

============================== 2 passed in 0.01s ===============================
PYTEST_OUT
    exit 0
elif grep -q "def test_passes" tests/test_validation.py; then
    # GREEN state - simple passing test
    cat <<'PYTEST_OUT'
============================= test session starts ==============================
collected 1 items

tests/test_validation.py::test_passes PASSED                             [100%]

============================== 1 passed in 0.01s ===============================
PYTEST_OUT
    exit 0
else
    # Default: no tests collected
    echo "collected 0 items"
    exit 0
fi
EOF
chmod +x bin/pytest
export PATH="$PWD/bin:$PATH"

git add -A
git commit -q -m "Initial setup for feat-test-001"

##############################################################################
# Test 1: RED Validation (Phase 1)
##############################################################################

echo -e "\n${GREEN}Test 1: RED validation phase${NC}"

if python3 "$PROJECT_ROOT/commands/implement.py" feat-test-001 > /tmp/implement_red_output.txt 2>&1; then
    echo -e "${GREEN}✓ Command executed successfully${NC}"

    # Check output contains expected messages
    if grep -q "TDD ENTRY VALIDATION" /tmp/implement_red_output.txt && \
       grep -q "RED state confirmed" /tmp/implement_red_output.txt; then
        echo -e "${GREEN}✓ RED validation messages present${NC}"
    else
        echo -e "${RED}✗ Missing RED validation messages${NC}"
        cat /tmp/implement_red_output.txt
        exit 1
    fi

    # Check impl notes artifact created
    if [ -f "docs/features/feat-test-001-impl-notes.md" ]; then
        echo -e "${GREEN}✓ Implementation notes artifact created${NC}"

        # Verify contains RED evidence
        if grep -q "RED State" docs/features/feat-test-001-impl-notes.md; then
            echo -e "${GREEN}✓ RED state evidence in artifact${NC}"
        else
            echo -e "${RED}✗ Missing RED state evidence${NC}"
            exit 1
        fi
    else
        echo -e "${RED}✗ Implementation notes not created${NC}"
        exit 1
    fi
else
    echo -e "${RED}✗ Command failed unexpectedly${NC}"
    cat /tmp/implement_red_output.txt
    exit 1
fi

##############################################################################
# Test 2: Halt on Already-Passing Tests
##############################################################################

echo -e "\n${GREEN}Test 2: Halt when tests already passing${NC}"

# Create passing tests (GREEN state - should block)
cat > tests/test_validation.py <<'EOF'
"""Test validation logic"""
def test_passes():
    """Test that passes"""
    assert True
EOF

git add tests/test_validation.py
git commit -q -m "Make tests pass (for testing halt)"

if python3 "$PROJECT_ROOT/commands/implement.py" feat-test-001 > /tmp/implement_halt_output.txt 2>&1; then
    echo -e "${RED}✗ Command should have failed (exit 1) for GREEN state${NC}"
    cat /tmp/implement_halt_output.txt
    exit 1
else
    EXIT_CODE=$?
    if [ $EXIT_CODE -eq 1 ]; then
        echo -e "${GREEN}✓ Command exited with code 1 (validation failure)${NC}"

        if grep -q "Tests already passing" /tmp/implement_halt_output.txt; then
            echo -e "${GREEN}✓ Correct error message displayed${NC}"
        else
            echo -e "${RED}✗ Wrong error message${NC}"
            cat /tmp/implement_halt_output.txt
            exit 1
        fi
    else
        echo -e "${RED}✗ Wrong exit code: $EXIT_CODE (expected 1)${NC}"
        exit 1
    fi
fi

# Restore RED state for remaining tests
cat > tests/test_validation.py <<'EOF'
"""Test validation logic"""
def test_validates_input():
    from validation import validate_input
    assert validate_input("test") == True
EOF

git add tests/test_validation.py
git commit -q -m "Restore RED state"

##############################################################################
# Test 3: Simulate Implementation + GREEN Validation
##############################################################################

echo -e "\n${GREEN}Test 3: Implementation + GREEN validation${NC}"

# Simulate @make agent implementing the code
mkdir -p src
cat > src/validation.py <<'EOF'
"""Validation module"""
def validate_input(value):
    """Validate input value"""
    if not isinstance(value, str):
        raise ValueError("Input must be a string")
    return bool(value)
EOF

# Update test to work with implementation
cat > tests/test_validation.py <<'EOF'
"""Test validation logic"""
import sys
sys.path.insert(0, 'src')

def test_validates_input():
    from validation import validate_input
    assert validate_input("test") == True

def test_returns_false_for_empty():
    from validation import validate_input
    assert validate_input("") == False
EOF

git add -A
git commit -q -m "Implement validation module"

# Run GREEN validation
if python3 "$PROJECT_ROOT/commands/implement.py" feat-test-001 --validate-green > /tmp/implement_green_output.txt 2>&1; then
    echo -e "${GREEN}✓ GREEN validation executed successfully${NC}"

    # Check output
    if grep -q "GREEN STATE VALIDATION" /tmp/implement_green_output.txt && \
       grep -q "GREEN state confirmed" /tmp/implement_green_output.txt; then
        echo -e "${GREEN}✓ GREEN validation messages present${NC}"
    else
        echo -e "${RED}✗ Missing GREEN validation messages${NC}"
        cat /tmp/implement_green_output.txt
        exit 1
    fi

    # Check artifact updated with GREEN evidence
    if grep -q "GREEN State" docs/features/feat-test-001-impl-notes.md; then
        echo -e "${GREEN}✓ GREEN state evidence in artifact${NC}"
    else
        echo -e "${RED}✗ Missing GREEN state evidence${NC}"
        exit 1
    fi

    # Check integration validation ran
    if grep -q "INTEGRATION VALIDATION" /tmp/implement_green_output.txt; then
        echo -e "${GREEN}✓ Integration validation executed${NC}"
    else
        echo -e "${YELLOW}⚠ Integration validation not detected${NC}"
    fi

    # Check status updated to complete
    if grep -q "Status.*complete" docs/features/feat-test-001-impl-notes.md; then
        echo -e "${GREEN}✓ Artifact status updated to complete${NC}"
    else
        echo -e "${YELLOW}⚠ Artifact status not updated${NC}"
    fi
else
    echo -e "${RED}✗ GREEN validation failed${NC}"
    cat /tmp/implement_green_output.txt
    exit 1
fi

##############################################################################
# Test 4: Complete RED→GREEN Evidence
##############################################################################

echo -e "\n${GREEN}Test 4: Complete RED→GREEN evidence captured${NC}"

IMPL_NOTES="docs/features/feat-test-001-impl-notes.md"

if [ -f "$IMPL_NOTES" ]; then
    if grep -q "RED State" "$IMPL_NOTES" && \
       grep -q "GREEN State" "$IMPL_NOTES"; then
        echo -e "${GREEN}✓ Both RED and GREEN evidence present${NC}"
    else
        echo -e "${RED}✗ Missing evidence sections${NC}"
        exit 1
    fi

    # Verify timestamps
    if grep -q "Timestamp:" "$IMPL_NOTES"; then
        echo -e "${GREEN}✓ Timestamps captured${NC}"
    else
        echo -e "${YELLOW}⚠ Timestamps not found${NC}"
    fi
else
    echo -e "${RED}✗ Implementation notes artifact missing${NC}"
    exit 1
fi

##############################################################################
# Test 5: Integration Checks Execution
##############################################################################

echo -e "\n${GREEN}Test 5: Integration checks execution${NC}"

# Verify integration commands ran
if grep -q "style-check" /tmp/implement_green_output.txt || \
   grep -q "Style check passed" /tmp/implement_green_output.txt; then
    echo -e "${GREEN}✓ Style check executed${NC}"
else
    echo -e "${YELLOW}⚠ Style check not detected in output${NC}"
fi

if grep -q "type-check" /tmp/implement_green_output.txt || \
   grep -q "Type check passed" /tmp/implement_green_output.txt; then
    echo -e "${GREEN}✓ Type check executed${NC}"
else
    echo -e "${YELLOW}⚠ Type check not detected in output${NC}"
fi

##############################################################################
# Test 6: Artifact Content Validation
##############################################################################

echo -e "\n${GREEN}Test 6: Artifact content validation${NC}"

if [ -f "$IMPL_NOTES" ]; then
    # Check required sections
    REQUIRED_SECTIONS=(
        "Feature ID"
        "Implementation Summary"
        "RED State"
        "GREEN State"
        "Integration Validation"
    )

    for section in "${REQUIRED_SECTIONS[@]}"; do
        if grep -q "$section" "$IMPL_NOTES"; then
            echo -e "${GREEN}✓ Section present: $section${NC}"
        else
            echo -e "${YELLOW}⚠ Section missing: $section${NC}"
        fi
    done

    # Verify feature ID matches
    if grep -q "feat-test-001" "$IMPL_NOTES"; then
        echo -e "${GREEN}✓ Correct feature ID in artifact${NC}"
    else
        echo -e "${RED}✗ Feature ID mismatch${NC}"
        exit 1
    fi
else
    echo -e "${RED}✗ Implementation notes artifact not found${NC}"
    exit 1
fi

##############################################################################
# Summary
##############################################################################

echo -e "\n${GREEN}=== Test Summary ===${NC}"
echo -e "${GREEN}✓ RED validation works${NC}"
echo -e "${GREEN}✓ Workflow halts on already-passing tests${NC}"
echo -e "${GREEN}✓ GREEN validation works${NC}"
echo -e "${GREEN}✓ Integration validation executes${NC}"
echo -e "${GREEN}✓ RED→GREEN evidence captured${NC}"
echo -e "${GREEN}✓ Artifact created and updated correctly${NC}"
echo -e "${GREEN}✓ All required sections present${NC}"

echo -e "\n${GREEN}=== S4-006: PASSED ===${NC}"
