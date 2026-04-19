# TDD Examples: Red-Green-Refactor

## Example Scenario: Adding an Email Validator

**Requirement Synthesis:** We need a utility function that validates if a string is a properly formatted email address.

### Step 1: Write the Failing Test (Red)
```python
# test_validators.py
import pytest
from utils.validators import is_valid_email

def test_is_valid_email_valid_cases():
    assert is_valid_email("test@example.com") == True
    assert is_valid_email("user.name+tag@domain.co.uk") == True

def test_is_valid_email_invalid_cases():
    assert is_valid_email("plainaddress") == False
    assert is_valid_email("@no-local-part.com") == False
    assert is_valid_email("Outlook Contact <outlook@test.com>") == False
    assert is_valid_email("") == False
```
*Run tests. They should fail (or raise an ImportError if the function doesn't exist yet).*

### Step 2: Write the Minimum Implementation (Green)
```python
# utils/validators.py
import re

def is_valid_email(email: str) -> bool:
    # Minimum code to pass the tests
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    if not email:
        return False
    return bool(re.match(pattern, email))
```
*Run tests. They should now pass.*

### Step 3: Refactor
```python
# utils/validators.py
import re

# Compile the regex pattern once for better performance
EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

def is_valid_email(email: str) -> bool:
    """Validates an email address against a standard regex pattern."""
    if not isinstance(email, str) or not email:
        return False
    return bool(EMAIL_PATTERN.match(email))
```
*Run tests. They should still pass, verifying the refactor didn't break functionality.*
