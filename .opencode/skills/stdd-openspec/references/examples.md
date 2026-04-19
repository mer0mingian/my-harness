# OpenSpec Artifact Examples

## 1. proposal.md
```markdown
# Feature: Dark Mode Support

## Why are we doing this?
Users have requested a dark mode to reduce eye strain in low-light environments.

## What is changing?
We will introduce a theme toggle in the main navigation bar. The application will support 'light', 'dark', and 'system' themes, persisting the user's preference in localStorage.
```

## 2. specs/requirements.md
```markdown
# Requirements: Dark Mode

## Job Story
When I am working in a dark room, I want to switch the application to dark mode, so I can reduce eye strain.

## Business Rules (EARS)
- The System shall default to the user's OS system theme if no preference is set.
- When the user clicks the theme toggle, the System shall cycle through Light -> Dark -> System themes.
- The System shall persist the theme preference in `localStorage`.
```

## 3. design.md
```markdown
# Design: Dark Mode Support

## Technical Approach
- Create a `ThemeProvider` context in React.
- Use CSS Variables (`--bg-color`, `--text-color`) for theming.
- Add a `ThemeToggle` component to the `TopBar`.
```

## 4. tasks.md
```markdown
# Implementation Tasks

- [ ] 1. Define CSS variables for light and dark themes in `globals.css`.
- [ ] 2. Create `ThemeProvider` context and hook.
- [ ] 3. Implement `ThemeToggle` UI component.
- [ ] 4. Write Playwright e2e tests for theme switching and persistence.
```
