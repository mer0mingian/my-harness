# SpecKit Artifacts Reference

Complete catalog of files and directories created by SpecKit workflow phases.

## Directory Structure

```
project-root/
├── .specify/
│   ├── memory/
│   │   └── constitution.md         # Phase 0: Project principles
│   ├── extensions/                 # Extension configs
│   │   └── {ext-id}/
│   │       └── config.yml
│   └── workflows/                  # Workflow state
│       └── {workflow-id}/
│           └── state.json
├── specs/
│   └── {NNN-feature-name}/         # Feature directory
│       ├── spec.md                 # Phase 1: Requirements
│       ├── plan.md                 # Phase 3: Implementation strategy
│       ├── tasks.md                # Phase 4: Task breakdown
│       ├── research.md             # Phase 3: Tech validation
│       ├── data-model.md           # Phase 3: Entity definitions
│       ├── quickstart.md           # Phase 3: Validation scenarios
│       ├── contracts/              # Phase 3: API specifications
│       │   ├── api.json
│       │   ├── database-schema.sql
│       │   └── events.json
│       └── implementation-details/ # Phase 3: Complex algorithms
│           ├── algorithm-x.md
│           └── integration-y.md
└── .claude/commands/               # AI agent integration
    └── speckit.*.md
```

## Phase 0: Constitution

### `.specify/memory/constitution.md`

**Created by:** `/speckit.constitution`

**Purpose:** Immutable project principles that guide all feature decisions

**Sections:**
- **Preamble** - Project philosophy and goals
- **Articles** - Numbered principles (Article I, Article II, etc.)
- **Gates** - Pass/fail checkpoints for plan approval
- **Complexity Tracking** - Justified exceptions to principles

**Example:**

```markdown
# Project Constitution

## Preamble
This project values simplicity over abstraction, test coverage over 
implementation speed, and integration tests over unit tests.

## Article I: Library-First Architecture
All features begin as standalone libraries that can be composed.

## Article II: 3-Project Maximum
No feature shall require more than 3 projects (frontend, backend, shared).

## Article III: Test-Driven Development
Tests must exist before implementation. No production code without tests.

## Gates
- Simplicity Gate: ≤3 projects
- Anti-Abstraction Gate: Direct framework usage, no wrappers
- Integration-First Gate: Contract tests planned
```

## Phase 1: Specify

### `specs/{NNN-feature-name}/spec.md`

**Created by:** `/speckit.specify`

**Purpose:** Define WHAT to build and WHY (no implementation details)

**Sections:**
- **Overview** - Feature summary, target users
- **User Stories** - As a [user], I want [goal], so that [benefit]
- **Acceptance Criteria** - Testable success conditions
- **Success Metrics** - Measurable outcomes (usage, performance, etc.)
- **Out of Scope** - Explicitly excluded features
- **Dependencies** - External requirements (APIs, services, data)
- **Review & Acceptance Checklist** - Completeness validation

**Quality markers:**
- `[NEEDS CLARIFICATION]` - Underspecified areas requiring refinement
- `[RISK]` - Potential blockers or concerns
- `[ASSUMPTION]` - Unvalidated assumptions

**Example:**

```markdown
# Feature 001: Photo Album Organizer

## Overview
Users need a way to organize photos into albums grouped by date or event.

## User Stories

### US-1: Create Album
As a user, I want to create a new photo album with a name and date,
so that I can organize my photos by event.

**Acceptance Criteria:**
- [ ] User can click "New Album" button
- [ ] Form accepts album name (1-100 chars) and date (YYYY-MM-DD)
- [ ] Album appears in album list after creation
- [ ] Album name must be unique

### US-2: View Albums
As a user, I want to see all my albums in a grid layout,
so that I can quickly browse my collection.

**Acceptance Criteria:**
- [ ] Albums displayed in 3-column grid on desktop
- [ ] Each album shows: name, date, photo count, thumbnail
- [ ] Grid is responsive (2 cols on tablet, 1 col on mobile)

## Success Metrics
- Album creation completes in <500ms
- Grid renders in <200ms for 100 albums
- User can create 10 albums in first session

## Out of Scope
- Album sharing with other users (future v2 feature)
- Nested albums or album hierarchies
- Photo editing within albums

## Dependencies
- Photo storage system must be operational
- User authentication must be complete
```

## Phase 2: Refine/Clarify

**No new files created**

Updates `spec.md` to resolve `[NEEDS CLARIFICATION]` markers and fill gaps.

## Phase 3: Plan

### `specs/{NNN-feature-name}/plan.md`

**Created by:** `/speckit.plan`

**Purpose:** Define HOW to implement - tech stack, architecture, dependencies

**Sections:**
- **Tech Stack** - Frameworks, libraries, languages, versions
- **Architecture** - System design, component relationships
- **Data Model** - Entities, relationships (reference to data-model.md)
- **API Design** - Endpoints, contracts (reference to contracts/)
- **Testing Strategy** - Unit, integration, e2e test approach
- **Deployment** - Environment setup, CI/CD, infrastructure
- **Complexity Tracking** - Constitutional gate compliance

**Example:**

```markdown
# Implementation Plan: Photo Album Organizer

## Tech Stack
- **Frontend**: React 18 + TypeScript 5.2
- **Backend**: Node.js 20 + Express 4.18
- **Database**: PostgreSQL 15
- **Testing**: Jest 29 + React Testing Library
- **Deployment**: Docker Compose (local), Azure App Service (prod)

## Architecture
### Components
1. **Web Client** (React SPA)
   - AlbumGrid component
   - AlbumForm component
   - PhotoTile component

2. **REST API** (Express)
   - `/api/albums` - CRUD endpoints
   - `/api/photos` - Photo management

3. **Database** (PostgreSQL)
   - albums table
   - photos table
   - album_photos junction table

### Data Flow
Client → REST API → Database
Client ← REST API ← Database

## Data Model
See [data-model.md](data-model.md) for full entity definitions.

**Key entities:**
- Album: id, name, date, user_id, created_at
- Photo: id, file_path, thumbnail_path, uploaded_at
- AlbumPhoto: album_id, photo_id, position

## API Design
See [contracts/api.json](contracts/api.json) for OpenAPI spec.

**Key endpoints:**
- `POST /api/albums` - Create album
- `GET /api/albums` - List albums
- `GET /api/albums/:id` - Get album details
- `PUT /api/albums/:id` - Update album
- `DELETE /api/albums/:id` - Delete album

## Testing Strategy
1. **Contract Tests** (First)
   - API contract tests for each endpoint
   - Database schema validation

2. **Integration Tests** (Second)
   - Full request/response cycle tests
   - Database integration tests

3. **Component Tests** (Third)
   - React component rendering
   - User interaction simulation

4. **E2E Tests** (Final)
   - Full user workflow tests
   - Cross-browser validation

## Deployment
**Local:**
- Docker Compose with 3 services (web, api, db)
- Seed data for development

**Production:**
- Azure App Service for web + api
- Azure Database for PostgreSQL
- Azure Blob Storage for photos

## Complexity Tracking
### Article VII: 3-Project Maximum
✅ PASS: 2 projects (web client, api server)

### Article VIII: Anti-Abstraction
✅ PASS: Using Express directly, no custom framework wrapper

### Article IX: Integration-First
✅ PASS: Contract tests planned before implementation
```

### `specs/{NNN-feature-name}/research.md`

**Created by:** `/speckit.plan`

**Purpose:** Tech stack validation, version compatibility, dependency analysis

**Sections:**
- **Technology Research** - Evaluated options and rationale
- **Version Compatibility** - Verified versions and breaking changes
- **Dependency Analysis** - Third-party libraries and their licenses
- **Performance Considerations** - Benchmarks and scalability notes
- **Risk Assessment** - Technical risks and mitigation strategies

### `specs/{NNN-feature-name}/data-model.md`

**Created by:** `/speckit.plan`

**Purpose:** Complete entity definitions, relationships, constraints

**Sections:**
- **Entity Definitions** - All domain entities with fields
- **Relationships** - Foreign keys, cardinality
- **Constraints** - Unique, not-null, check constraints
- **Indexes** - Performance optimization indexes
- **Migrations** - Schema evolution strategy

**Example:**

```markdown
# Data Model: Photo Album Organizer

## Entity: Album

| Field      | Type         | Constraints                    |
|------------|--------------|--------------------------------|
| id         | UUID         | Primary key, generated         |
| name       | VARCHAR(100) | NOT NULL, UNIQUE per user      |
| date       | DATE         | NOT NULL                       |
| user_id    | UUID         | Foreign key to users table     |
| created_at | TIMESTAMP    | NOT NULL, default now()        |
| updated_at | TIMESTAMP    | NOT NULL, default now()        |

## Entity: Photo

| Field          | Type         | Constraints             |
|----------------|--------------|-------------------------|
| id             | UUID         | Primary key, generated  |
| file_path      | VARCHAR(500) | NOT NULL, unique        |
| thumbnail_path | VARCHAR(500) | NOT NULL                |
| uploaded_at    | TIMESTAMP    | NOT NULL, default now() |

## Entity: AlbumPhoto (Junction)

| Field    | Type    | Constraints                     |
|----------|---------|---------------------------------|
| album_id | UUID    | Foreign key to albums           |
| photo_id | UUID    | Foreign key to photos           |
| position | INTEGER | NOT NULL, default 0             |

**Composite Primary Key:** (album_id, photo_id)

## Relationships

- Album `1` ← `M` AlbumPhoto
- Photo `1` ← `M` AlbumPhoto
- User `1` ← `M` Album

## Indexes

- `idx_albums_user_date` on albums(user_id, date DESC)
- `idx_album_photos_position` on album_photos(album_id, position)
- `idx_photos_uploaded` on photos(uploaded_at DESC)
```

### `specs/{NNN-feature-name}/contracts/`

**Created by:** `/speckit.plan`

**Purpose:** API specifications, database schemas, event definitions

**Files:**
- `api.json` - OpenAPI 3.0 spec for REST APIs
- `graphql-schema.graphql` - GraphQL schema (if applicable)
- `database-schema.sql` - DDL for database tables
- `events.json` - Event schemas for async messaging (if applicable)

### `specs/{NNN-feature-name}/quickstart.md`

**Created by:** `/speckit.plan`

**Purpose:** Validation scenarios to test the feature works end-to-end

**Sections:**
- **Setup** - How to run the application locally
- **Test Scenarios** - Step-by-step user workflows
- **Expected Outcomes** - What should happen for each scenario
- **Cleanup** - How to reset state after testing

## Phase 4: Tasks

### `specs/{NNN-feature-name}/tasks.md`

**Created by:** `/speckit.tasks`

**Purpose:** Ordered, executable task list with dependencies

**Structure:**
- Grouped by user story
- Ordered by dependencies (data → logic → interface)
- Marked `[P]` for parallel-safe tasks
- File paths specified
- Test tasks before implementation tasks
- Checkpoint validations between stories

**Example:**

```markdown
# Tasks: Photo Album Organizer

## User Story 1: Create Album

### Database Layer
- [ ] Create albums table migration (`migrations/001_create_albums.sql`)
- [ ] Create photos table migration (`migrations/002_create_photos.sql`)
- [ ] Create album_photos junction table (`migrations/003_create_album_photos.sql`)

### Contract Tests
- [ ] [P] Write contract test for POST /api/albums (`tests/contracts/albums.test.ts`)
- [ ] [P] Write contract test for GET /api/albums (`tests/contracts/albums.test.ts`)

### Backend Implementation
- [ ] Create Album model (`src/models/Album.ts`)
- [ ] Create AlbumRepository (`src/repositories/AlbumRepository.ts`)
- [ ] Create AlbumService (`src/services/AlbumService.ts`)
- [ ] Create POST /api/albums endpoint (`src/routes/albums.ts`)
- [ ] Create GET /api/albums endpoint (`src/routes/albums.ts`)

### Frontend Implementation
- [ ] [P] Create AlbumForm component (`src/components/AlbumForm.tsx`)
- [ ] [P] Create AlbumGrid component (`src/components/AlbumGrid.tsx`)
- [ ] Wire AlbumForm to API (`src/components/AlbumForm.tsx`)
- [ ] Wire AlbumGrid to API (`src/components/AlbumGrid.tsx`)

### Integration Tests
- [ ] Test album creation flow (`tests/integration/album-creation.test.ts`)
- [ ] Test album list display (`tests/integration/album-list.test.ts`)

### Checkpoint: User Story 1 Complete
- [ ] Run all tests: `npm test`
- [ ] Manual test: Create album via UI
- [ ] Manual test: View albums in grid
- [ ] Commit: "Implement US-1: Create Album"

## User Story 2: View Albums

### Backend Implementation
- [ ] Create GET /api/albums/:id endpoint (`src/routes/albums.ts`)
- [ ] Add photo count to album response (`src/services/AlbumService.ts`)

### Frontend Implementation
- [ ] Create AlbumDetail component (`src/components/AlbumDetail.tsx`)
- [ ] Add navigation from AlbumGrid to AlbumDetail (`src/App.tsx`)

### Integration Tests
- [ ] Test album detail view (`tests/integration/album-detail.test.ts`)

### Checkpoint: User Story 2 Complete
- [ ] Run all tests: `npm test`
- [ ] Manual test: Click album to view details
- [ ] Commit: "Implement US-2: View Albums"
```

## Phase 5: Implementation

**No new files created**

Executes tasks from `tasks.md` and creates application code.

Updates `tasks.md` with task status (in_progress → completed).

## AI Agent Integration

### `.claude/commands/speckit.*.md`

**Created by:** `specify init --integration claude`

**Purpose:** AI agent commands that wrap SpecKit CLI

**Files:**
- `speckit.constitution.md` - Phase 0 command
- `speckit.specify.md` - Phase 1 command
- `speckit.clarify.md` - Phase 2 command
- `speckit.plan.md` - Phase 3 command
- `speckit.tasks.md` - Phase 4 command
- `speckit.implement.md` - Phase 5 command

Similar structure for other AI agents (`.gemini/`, `.copilot/`, etc.)

## Summary: Artifact Lifecycle

| Phase | Creates | Updates |
|-------|---------|---------|
| 0: Constitution | constitution.md | - |
| 1: Specify | spec.md | - |
| 2: Clarify | - | spec.md |
| 3: Plan | plan.md, research.md, data-model.md, contracts/, quickstart.md | - |
| 4: Tasks | tasks.md | - |
| 5: Implement | Application code | tasks.md (status) |
