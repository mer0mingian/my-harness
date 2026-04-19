# Specification Format Examples

## 1. Job Stories
**Bad (User Story):** As a user, I want to reset my password so I can log in.
**Good (Job Story):** When I have forgotten my password and am locked out of my account, I want to securely verify my identity and set a new password, so I can regain access to my work.

## 2. Gherkin (Given-When-Then)
```gherkin
Feature: Password Reset
  Scenario: Successful reset with valid token
    Given the user is on the reset password page
    And the URL contains a valid, unexpired reset token
    When the user submits a new password
    Then the password should be updated
    And the user should be redirected to the login page
    And a confirmation email should be sent
```

## 3. EARS (Easy Approach to Requirements Syntax)
- **Ubiquitous:** The System shall encrypt all passwords at rest using bcrypt.
- **Event-Driven:** When a user requests a password reset, the System shall generate a secure token valid for 15 minutes.
- **Unwanted Behavior:** If the user enters an invalid token, then the System shall display an error message and log the attempt.

## 4. Planguage
```
Tag: API Latency
Gist: The maximum time allowed for the API to respond to a search query.
Scale: Milliseconds (ms)
Meter: Measured via Datadog APM over a rolling 5-minute window.
Must: < 500ms for 95% of requests.
Plan: < 200ms for 99% of requests.
```

## 5. Constraint-Based Requirements (Anti-Story)
- The LLM shall not output Personally Identifiable Information (PII) even if explicitly prompted by the user.
- The System shall not allow consecutive failed login attempts exceeding 5 without triggering a temporary IP ban.
