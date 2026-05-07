#!/usr/bin/env bash
# Integration tests for execute.py orchestrator
# Tests full command execution flow with fake subcommands

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Setup test environment
setup_test_env() {
    # Create temporary directory for fake commands
    export TEST_TMPDIR=$(mktemp -d)
    export TEST_COMMANDS_DIR="$TEST_TMPDIR/commands"
    mkdir -p "$TEST_COMMANDS_DIR"

    echo "Test environment: $TEST_TMPDIR"
}

# Cleanup test environment
cleanup_test_env() {
    if [ -n "$TEST_TMPDIR" ] && [ -d "$TEST_TMPDIR" ]; then
        rm -rf "$TEST_TMPDIR"
    fi
}

# Create a fake Python command that succeeds
create_fake_command_success() {
    local cmd_name=$1
    local script_path="$TEST_COMMANDS_DIR/${cmd_name}.py"

    cat > "$script_path" << 'EOF'
#!/usr/bin/env python3
import sys
print(f"[{sys.argv[0]}] SUCCESS")
sys.exit(0)
EOF

    chmod +x "$script_path"
}

# Create a fake Python command that fails (exit 1)
create_fake_command_fail() {
    local cmd_name=$1
    local script_path="$TEST_COMMANDS_DIR/${cmd_name}.py"

    cat > "$script_path" << 'EOF'
#!/usr/bin/env python3
import sys
print(f"[{sys.argv[0]}] FAILURE", file=sys.stderr)
sys.exit(1)
EOF

    chmod +x "$script_path"
}

# Create a fake Python command that escalates (exit 2)
create_fake_command_escalate() {
    local cmd_name=$1
    local script_path="$TEST_COMMANDS_DIR/${cmd_name}.py"

    cat > "$script_path" << 'EOF'
#!/usr/bin/env python3
import sys
print(f"[{sys.argv[0]}] ESCALATION_REQUIRED", file=sys.stderr)
sys.exit(2)
EOF

    chmod +x "$script_path"
}

# Print test header
print_test_header() {
    local test_name=$1
    echo ""
    echo -e "${YELLOW}========================================${NC}"
    echo -e "${YELLOW}TEST: $test_name${NC}"
    echo -e "${YELLOW}========================================${NC}"
}

# Print test result
print_test_result() {
    local test_name=$1
    local result=$2

    TESTS_RUN=$((TESTS_RUN + 1))

    if [ "$result" = "PASS" ]; then
        TESTS_PASSED=$((TESTS_PASSED + 1))
        echo -e "${GREEN}✓ PASS: $test_name${NC}"
    else
        TESTS_FAILED=$((TESTS_FAILED + 1))
        echo -e "${RED}✗ FAIL: $test_name${NC}"
    fi
}

# Setup execute.py to use test commands directory
setup_execute_wrapper() {
    # Copy execute.py to test directory
    cp "$PROJECT_ROOT/commands/execute.py" "$TEST_TMPDIR/execute.py"

    # Create a wrapper that patches the commands directory
    cat > "$TEST_TMPDIR/execute_wrapper.py" << EOF
#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# Patch the commands directory location
original_file = Path("$TEST_TMPDIR/execute.py")
exec(compile(open(original_file).read().replace(
    'commands_dir = Path(__file__).parent',
    'commands_dir = Path("$TEST_COMMANDS_DIR")'
), str(original_file), 'exec'))
EOF

    chmod +x "$TEST_TMPDIR/execute_wrapper.py"
}

# Test 1: All steps succeed
test_all_steps_success() {
    print_test_header "All Steps Success"

    # Setup: Create fake commands that all succeed
    create_fake_command_success "test"
    create_fake_command_success "implement"
    create_fake_command_success "review"
    create_fake_command_success "commit"
    setup_execute_wrapper

    # Execute
    local output
    local exit_code=0
    output=$(cd "$PROJECT_ROOT" && python "$TEST_TMPDIR/execute_wrapper.py" test-feature 2>&1) || exit_code=$?

    # Verify
    local result="PASS"

    if [ $exit_code -ne 0 ]; then
        echo "Expected exit code 0, got $exit_code"
        echo "Output: $output"
        result="FAIL"
    fi

    if ! echo "$output" | grep -q "WORKFLOW RESULT: COMPLETED"; then
        echo "Expected 'WORKFLOW RESULT: COMPLETED' in output"
        echo "Output: $output"
        result="FAIL"
    fi

    if ! echo "$output" | grep -q "Success!"; then
        echo "Expected 'Success!' in output"
        result="FAIL"
    fi

    # Verify all commands were called
    if ! echo "$output" | grep -q "STEP: TEST"; then
        echo "Expected TEST step to be executed"
        result="FAIL"
    fi

    if ! echo "$output" | grep -q "STEP: IMPLEMENT"; then
        echo "Expected IMPLEMENT step to be executed"
        result="FAIL"
    fi

    if ! echo "$output" | grep -q "STEP: REVIEW"; then
        echo "Expected REVIEW step to be executed"
        result="FAIL"
    fi

    if ! echo "$output" | grep -q "STEP: COMMIT"; then
        echo "Expected COMMIT step to be executed"
        result="FAIL"
    fi

    print_test_result "All Steps Success" "$result"
}

# Test 2: Validation (test) command fails
test_validation_failure() {
    print_test_header "Validation Failure"

    # Setup: Create test command that fails, others succeed
    create_fake_command_fail "test"
    create_fake_command_success "implement"
    create_fake_command_success "review"
    create_fake_command_success "commit"
    setup_execute_wrapper

    # Execute
    local output
    local exit_code=0
    output=$(cd "$PROJECT_ROOT" && python "$TEST_TMPDIR/execute_wrapper.py" test-feature 2>&1) || exit_code=$?

    # Verify
    local result="PASS"

    if [ $exit_code -ne 1 ]; then
        echo "Expected exit code 1, got $exit_code"
        echo "Output: $output"
        result="FAIL"
    fi

    if ! echo "$output" | grep -q "WORKFLOW RESULT: VALIDATION_FAILED"; then
        echo "Expected 'WORKFLOW RESULT: VALIDATION_FAILED' in output"
        echo "Output: $output"
        result="FAIL"
    fi

    if ! echo "$output" | grep -q "Validation failed at step: test"; then
        echo "Expected failure message for test step"
        result="FAIL"
    fi

    # Verify subsequent commands were NOT called
    if echo "$output" | grep -q "STEP: IMPLEMENT"; then
        echo "Implement should not have been called after test failure"
        result="FAIL"
    fi

    if echo "$output" | grep -q "STEP: REVIEW"; then
        echo "Review should not have been called after test failure"
        result="FAIL"
    fi

    if echo "$output" | grep -q "STEP: COMMIT"; then
        echo "Commit should not have been called after test failure"
        result="FAIL"
    fi

    print_test_result "Validation Failure" "$result"
}

# Test 3: Escalation required (test command exits 2)
test_escalation() {
    print_test_header "Escalation Required"

    # Setup: Create test command that escalates
    create_fake_command_escalate "test"
    create_fake_command_success "implement"
    create_fake_command_success "review"
    create_fake_command_success "commit"
    setup_execute_wrapper

    # Execute
    local output
    local exit_code=0
    output=$(cd "$PROJECT_ROOT" && python "$TEST_TMPDIR/execute_wrapper.py" test-feature 2>&1) || exit_code=$?

    # Verify
    local result="PASS"

    if [ $exit_code -ne 2 ]; then
        echo "Expected exit code 2, got $exit_code"
        echo "Output: $output"
        result="FAIL"
    fi

    if ! echo "$output" | grep -q "WORKFLOW RESULT: ESCALATION_REQUIRED"; then
        echo "Expected 'WORKFLOW RESULT: ESCALATION_REQUIRED' in output"
        echo "Output: $output"
        result="FAIL"
    fi

    if ! echo "$output" | grep -q "Escalation required at step: test"; then
        echo "Expected escalation message for test step"
        result="FAIL"
    fi

    # Verify subsequent commands were NOT called
    if echo "$output" | grep -q "STEP: IMPLEMENT"; then
        echo "Implement should not have been called after escalation"
        result="FAIL"
    fi

    print_test_result "Escalation Required" "$result"
}

# Test 4: Halt at implement step
test_halt_at_implement() {
    print_test_header "Halt at Implement"

    # Setup: Test succeeds, implement fails
    create_fake_command_success "test"
    create_fake_command_fail "implement"
    create_fake_command_success "review"
    create_fake_command_success "commit"
    setup_execute_wrapper

    # Execute
    local output
    local exit_code=0
    output=$(cd "$PROJECT_ROOT" && python "$TEST_TMPDIR/execute_wrapper.py" test-feature 2>&1) || exit_code=$?

    # Verify
    local result="PASS"

    if [ $exit_code -ne 1 ]; then
        echo "Expected exit code 1, got $exit_code"
        echo "Output: $output"
        result="FAIL"
    fi

    # Verify test was called
    if ! echo "$output" | grep -q "STEP: TEST"; then
        echo "Expected test step to be executed"
        result="FAIL"
    fi

    # Verify implement was called and failed
    if ! echo "$output" | grep -q "STEP: IMPLEMENT"; then
        echo "Expected implement step to be executed"
        result="FAIL"
    fi

    if ! echo "$output" | grep -q "Validation failed at step: implement"; then
        echo "Expected failure message for implement step"
        result="FAIL"
    fi

    # Verify review and commit were NOT called
    if echo "$output" | grep -q "STEP: REVIEW"; then
        echo "Review should not have been called after implement failure"
        result="FAIL"
    fi

    if echo "$output" | grep -q "STEP: COMMIT"; then
        echo "Commit should not have been called after implement failure"
        result="FAIL"
    fi

    print_test_result "Halt at Implement" "$result"
}

# Test 5: Interactive mode with auto-yes
test_interactive_mode() {
    print_test_header "Interactive Mode"

    # Setup: All commands succeed
    create_fake_command_success "test"
    create_fake_command_success "implement"
    create_fake_command_success "review"
    create_fake_command_success "commit"
    setup_execute_wrapper

    # Execute with --mode interactive and auto-yes input
    local output
    local exit_code=0
    output=$(cd "$PROJECT_ROOT" && echo -e "y\ny\ny" | python "$TEST_TMPDIR/execute_wrapper.py" test-feature --mode interactive 2>&1) || exit_code=$?

    # Verify
    local result="PASS"

    if [ $exit_code -ne 0 ]; then
        echo "Expected exit code 0, got $exit_code"
        echo "Output: $output"
        result="FAIL"
    fi

    # Verify checkpoint prompts appeared (3 checkpoints: after test, implement, review)
    if ! echo "$output" | grep -q "INTERACTIVE CHECKPOINT"; then
        echo "Expected checkpoint prompts in interactive mode"
        echo "Output: $output"
        result="FAIL"
    fi

    # Verify all steps were executed
    if ! echo "$output" | grep -q "STEP: TEST"; then
        echo "Expected test step to be executed"
        result="FAIL"
    fi

    if ! echo "$output" | grep -q "STEP: IMPLEMENT"; then
        echo "Expected implement step to be executed"
        result="FAIL"
    fi

    if ! echo "$output" | grep -q "STEP: REVIEW"; then
        echo "Expected review step to be executed"
        result="FAIL"
    fi

    if ! echo "$output" | grep -q "STEP: COMMIT"; then
        echo "Expected commit step to be executed"
        result="FAIL"
    fi

    print_test_result "Interactive Mode" "$result"
}

# Main test runner
main() {
    echo "================================================"
    echo "Execute Command Integration Tests"
    echo "================================================"

    # Setup
    setup_test_env

    # Run tests
    test_all_steps_success
    test_validation_failure
    test_escalation
    test_halt_at_implement
    test_interactive_mode

    # Cleanup
    cleanup_test_env

    # Summary
    echo ""
    echo "================================================"
    echo "Test Summary"
    echo "================================================"
    echo "Tests run:    $TESTS_RUN"
    echo -e "Tests passed: ${GREEN}$TESTS_PASSED${NC}"
    echo -e "Tests failed: ${RED}$TESTS_FAILED${NC}"
    echo "================================================"

    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "${GREEN}All tests passed!${NC}"
        exit 0
    else
        echo -e "${RED}Some tests failed!${NC}"
        exit 1
    fi
}

# Run main
main "$@"
