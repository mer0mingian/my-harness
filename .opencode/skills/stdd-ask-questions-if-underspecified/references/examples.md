# Examples of Clarifying Questions

## Example 1: Eliminating Branches of Work
**Context:** User asks "Build a user authentication system."

**Bad Question:** "How do you want me to build the authentication?"
*(Too open-ended, shifts burden to user)*

**Good Question (using `question` tool format):**
```json
{
  "question": "Which authentication strategy should we implement?",
  "header": "Auth Strategy",
  "multiple": false,
  "options": [
    {
      "label": "OAuth (Google/GitHub) (Recommended)",
      "description": "Fastest to build, most secure, offloads password management."
    },
    {
      "label": "Email/Password with JWT",
      "description": "Requires building password reset flows and secure storage."
    },
    {
      "label": "Magic Links",
      "description": "Passwordless, relies on email delivery."
    }
  ]
}
```

## Example 2: Clarifying Scope
**Context:** User asks "Refactor the database module."

**Good Question:**
```json
{
  "question": "What is the primary scope and goal of this refactor?",
  "header": "Refactor Scope",
  "multiple": false,
  "options": [
    {
      "label": "Improve Performance",
      "description": "Focus on indexing, query optimization, and N+1 issues."
    },
    {
      "label": "Migrate to New ORM (Recommended)",
      "description": "Switching from Raw SQL to SQLAlchemy."
    },
    {
      "label": "Add Typing/Tests",
      "description": "Just adding static types and unit tests, no logic changes."
    }
  ]
}
```
