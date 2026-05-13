# MATD Training Exercise: Job Recommendation Engine

**Status:** Planning  
**Created:** 2026-05-13  
**Purpose:** Minimal example system for training teams on matd-plugin and matd-extension workflows

---

## Overview

This document specifies a **training exercise** for teams to learn the MATD (Multi-Agent Test-Driven Development) workflow. Teams will build a Job Recommendation Engine from scratch using the matd-plugin (Claude Code) or matd-extension (SpecKit CLI), working through all four MATD phases.

**Key principle:** This is a **process training exercise**, not a production system. The goal is for teams to become familiar with:
- MATD workflow phases (Specification → Design → Refinement → Implementation)
- Agentic planning and refinement
- Contract-first development (OpenAPI + event schemas)
- V-model testing at all levels
- Multi-agent collaboration patterns

---

## Scope

### What Teams Build (During Exercise)

Teams will create **all artifacts** using MATD agents during the workshop:

**Phase 1 (Specification):**
- Product brief (using matd-specifier agent)
- Feature specifications with Job Stories + Gherkin scenarios
- Requirements documentation

**Phase 2 (Design):**
- Solution design with 4 architectural views
- ADRs (Architectural Decision Records) - teams decide topics during human/AI collaboration
- C4 diagrams (Context, Container, Component)

**Phase 3 (Refinement):**
- OpenAPI contracts (3 services)
- Event schemas (Redis Streams)
- Test designs
- Implementation plans

**Phase 4 (Implementation):**
- Code (3 microservices)
- Tests (unit, integration, contract, E2E)
- Task tracking (local Jira-style task files)
- Workflow summary

### What Is Pre-Created (Before Exercise)

**Foundation materials (provided to teams):**
1. **System Constitution** (`constitution/technical-constitution.md`) - Tech stack, NFRs, compliance
2. **Synthetic Data** (SQL seed files) - Deterministic dataset for consistent testing
3. **Database Schema** (complete) - User profiles, job listings, interactions, recommendations
4. **Gold Standard Dataset** - Expected recommendations for comparing team outputs
5. **V-Model Research Report** - Testing strategy guide (TBD: see Question 14)
6. **Initial Product Brief** - Task description to feed into MATD workflow

---

## Domain: Job Search (StepStone Terminology)

**System:** Job Recommendation Engine  
**Context:** StepStone job marketplace (simplified, local-only, synthetic data)

**Domain entities:**
- **Candidates** (job seekers) - Users with profiles (skills, experience, preferences)
- **Job Listings** (job ads) - Open positions from employers
- **Recommendations** - Personalized job suggestions for candidates
- **Interactions** - User searches, job views, profile updates

**StepStone terminology:**
- Use "candidate" (not "user") for job seekers
- Use "job listing" or "job ad" (not "posting")
- Use "skills" (not "competencies" unless technical context requires it)
- Use "application" only when referring to candidate applying to job (not the software system)

---

## Architecture

### System Boundaries

**3 microservices (distinct ownership):**

1. **User Profile Service**
   - **Owns:** Candidate profiles (skills, experience, preferences)
   - **Port:** 8001
   - **Database:** PostgreSQL schema `profiles`

2. **Job Catalog Service**
   - **Owns:** Job listings (titles, requirements, salary, location)
   - **Port:** 8002
   - **Database:** PostgreSQL schema `jobs`

3. **Recommendation Engine**
   - **Owns:** Recommendation scores and history
   - **Port:** 8003
   - **Database:** PostgreSQL schema `recommendations`

**Shared infrastructure:**
- PostgreSQL (single DB instance, multiple schemas)
- Redis (Streams for events, Cache for hot data)

**Explicitly OUT OF SCOPE (not part of system):**
- Authentication/Authorization (assumes pre-authenticated requests)
- Email/Notification delivery (Recommendation Engine publishes events only, doesn't send)
- Frontend UI (Swagger UI only for manual testing)
- External StepStone APIs (100% local, synthetic data only)

### Service Interactions (Boundaries)

**REST API calls (synchronous):**
- User Profile Service ↔ Job Catalog Service: **No direct calls** (decoupled)
- Recommendation Engine → User Profile Service: **GET /profiles/{user_id}** (fetch current profile when generating recommendations)
- Recommendation Engine → Job Catalog Service: **GET /jobs** (fetch job details for scoring)

**Event streams (asynchronous):**
- User Profile Service → Redis Stream: `profile.updated` event
- Job Catalog Service → Redis Stream: `job.viewed` event
- Recommendation Engine → Redis Stream: `recommendations.generated` event
- Recommendation Engine ← Redis Stream: Consumes `profile.updated` + `job.viewed` (triggers recommendation generation)

**Boundary pattern:** Hybrid (Option B)
- Services call REST APIs when needing current state
- Services emit events for state changes (triggers for downstream processing)
- Recommendation Engine maintains event-sourced view but calls upstream APIs for enrichment

### Service Contracts (To Be Generated by Teams)

Teams will create these contracts during Phase 3 (Refinement):

**OpenAPI contracts:**
- `contracts/user-profile-api.yaml`
- `contracts/job-catalog-api.yaml`
- `contracts/recommendation-api.yaml`

**Event schemas:**
- `contracts/events/profile-events.schema.json`
- `contracts/events/job-events.schema.json`
- `contracts/events/recommendation-events.schema.json`

**Note:** Data Producer/Consumer Contract templates are currently missing from the template library but will be added before the exercise.

---

## Technology Stack

**Language & Framework:**
- Python 3.12+
- FastAPI (web framework, OpenAPI auto-generation)
- asyncio + httpx (async runtime)

**Data Storage:**
- PostgreSQL 16+ (relational data)
- Redis 7+ (Streams for events, Cache for hot data)

**Testing:**
- pytest + pytest-asyncio (unit, integration)
- Schemathesis (contract testing - OpenAPI compliance)
- JSON Schema validators (event schema validation)
- Playwright (E2E testing)
- testcontainers (integration test isolation)

**Package Management:**
- uv (Python package manager)

**Deployment:**
- Docker + docker-compose (local runtime)
- Bind-mounted code (not copied into image)

**Rationale:**
- Aligns with existing harness-sandbox tooling (uv, deepwiki already installed)
- Team familiarity (Python for data science work)
- MATD agent support (matd-dev explicitly supports FastAPI + Python async patterns)
- Minimal learning curve for ML teams

---

## V-Model Testing Levels

**4 test levels mapping development phases to testing:**

| Development Phase | Test Level | Scope | Tools | Owner Agent |
|-------------------|------------|-------|-------|-------------|
| **Component Design** | **Unit Tests** | Individual functions, classes, endpoints in isolation | pytest, pytest-asyncio | matd-dev |
| **Architecture Design** | **Integration Tests** | Service-to-service calls, database interactions, Redis pub/sub | pytest, httpx, testcontainers | matd-dev |
| **System Design** | **Contract Tests** | OpenAPI spec compliance, event schema validation | Schemathesis, JSON Schema | matd-qa |
| **Requirements** | **E2E Tests** | Full user journeys through docker-compose stack | Playwright, docker-compose | matd-qa |

**Test coverage expectations:**
- **Unit:** 80%+ coverage for business logic (recommendation scoring, profile validation)
- **Integration:** All service-to-service interactions covered
- **Contract:** 100% OpenAPI endpoints validated, all event schemas validated
- **E2E:** Critical user flows (profile update → recommendation refresh)

**V-Model research report:** TBD - needs decision on creation approach (see Question 14)

---

## Recommendation Algorithm

**Complexity:** 4-factor weighted scoring with embedding similarity

**Algorithm:**
```
recommendation_score = 
  (skill_match_score * 0.4) +
  (location_match_score * 0.3) +
  (salary_match_score * 0.2) +
  (experience_match_score * 0.1)
```

**Scoring logic:**
- **Skill match:** Embedding similarity (local model only) between candidate skills and job required skills
  - Use sentence-transformers or similar local embedding model
  - No external API calls (HuggingFace local download acceptable)
- **Location match:** Binary (same city = 1.0, different = 0.5, remote = 1.0)
- **Salary match:** Overlap percentage between candidate expected range and job offered range
- **Experience match:** Inverse of absolute difference in years (closer = higher score)

**Rationale:**
- Simple enough to implement in workshop timeframe (2-3 hours)
- Complex enough to require unit tests for each scorer
- Realistic variation in recommendations (not trivial)
- ML-flavored (embeddings) without requiring model training
- Teams work with ML, so embedding similarity is familiar concept

---

## Synthetic Data Specification

### Format

**Option A: SQL seed files** (deterministic, PostgreSQL-native)

```
data/
├── seeds/
│   ├── 01_users.sql
│   ├── 02_jobs.sql
│   ├── 03_interactions.sql
│   └── 04_gold_standard.sql
└── schema/
    ├── profiles_schema.sql
    ├── jobs_schema.sql
    ├── interactions_schema.sql
    └── recommendations_schema.sql
```

Seeds loaded on container startup via `docker-entrypoint-initdb.d/` or init script.

### Database Schema (Pre-Defined)

**Profiles schema (User Profile Service):**
```sql
CREATE TABLE profiles.users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    skills JSONB NOT NULL,  -- ["Python", "FastAPI", "PostgreSQL"]
    experience_years INT NOT NULL,
    location VARCHAR(255) NOT NULL,
    preferred_salary_min INT,  -- euros per year
    preferred_salary_max INT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**Jobs schema (Job Catalog Service):**
```sql
CREATE TABLE jobs.listings (
    job_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    required_skills JSONB NOT NULL,  -- ["Python", "Docker", "Kubernetes"]
    location VARCHAR(255) NOT NULL,
    salary_min INT,  -- euros per year
    salary_max INT,
    company_name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**Interactions schema (shared, read by Recommendation Engine):**
```sql
CREATE TABLE interactions.user_searches (
    search_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES profiles.users(user_id),
    search_query TEXT,
    filters JSONB,  -- {"location": "Berlin", "min_salary": 60000}
    timestamp TIMESTAMP DEFAULT NOW()
);

CREATE TABLE interactions.job_views (
    view_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES profiles.users(user_id),
    job_id UUID NOT NULL REFERENCES jobs.listings(job_id),
    timestamp TIMESTAMP DEFAULT NOW()
);
```

**Recommendations schema (Recommendation Engine):**
```sql
CREATE TABLE recommendations.scores (
    recommendation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES profiles.users(user_id),
    job_id UUID NOT NULL REFERENCES jobs.listings(job_id),
    score FLOAT NOT NULL,  -- 0.0 to 1.0
    skill_match_score FLOAT,
    location_match_score FLOAT,
    salary_match_score FLOAT,
    experience_match_score FLOAT,
    generated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, job_id, generated_at)  -- allow re-scoring over time
);
```

### Data Volume

**Users (500 candidates):**
- Variety: Junior (0-2 years) to Senior (10+ years)
- Skills: Mix of backend, frontend, data science, DevOps, ML
- Locations: Berlin, Munich, Hamburg, Remote (25% each)
- Salary ranges: 40k-120k EUR (realistic German market)

**Jobs (2000 listings):**
- Roles: Backend Developer, Frontend Developer, Data Scientist, ML Engineer, DevOps Engineer, Product Manager, etc.
- Companies: 200 fictional company names (10 jobs per company on average)
- Locations: Berlin (40%), Munich (30%), Hamburg (20%), Remote (10%)
- Salary ranges: 45k-130k EUR

**Interactions (~5000 events):**
- User searches: 2000 events (avg 4 searches per user)
- Job views: 3000 events (avg 6 views per user)
- Timestamp range: Last 30 days (realistic recency)

**Gold Standard Dataset:**
- Pre-calculated recommendations for 50 "test users"
- Top 20 job recommendations per test user (1000 total recommendations)
- Purpose: Teams can compare their recommendation engine output against gold standard
- Format: CSV or JSON with `user_id, job_id, expected_score, expected_rank`

### Data Characteristics (All Synthetic)

**User profiles:**
- Names: Fictional (e.g., "Anna Müller", "Thomas Schmidt")
- Skills: Realistic combinations (e.g., "Python + FastAPI + PostgreSQL" for backend dev)
- No real PII (all generated)

**Job listings:**
- Titles: Realistic (e.g., "Senior Backend Engineer", "ML Platform Engineer")
- Descriptions: Template-based with variation
- Company names: Fictional (e.g., "TechStart GmbH", "DataFlow Solutions")
- No real company data

**Rationale for volume:**
- 500 users × 2000 jobs = 1M potential recommendations (realistic scale for local compute)
- Sufficient variety for testing edge cases (location mismatch, salary mismatch, skill gaps)
- Small enough to seed in <5 seconds, query in <1 second
- Allows deterministic comparison between team outputs

---

## Initial Product Brief (INPUT to MATD)

**What teams receive at workshop start:**

### Product Vision

StepStone's Job Recommendation Engine helps candidates discover relevant job opportunities by analyzing their skills, experience, and preferences against our job listing database. The system automatically generates personalized recommendations when candidates update their profiles or interact with job listings.

**User Problem:**
Candidates are overwhelmed by thousands of job listings and struggle to find positions matching their skills and career goals. Manual search is time-consuming and often misses relevant opportunities due to keyword mismatches or incomplete search filters.

**Solution:**
An intelligent recommendation engine that proactively surfaces relevant jobs by understanding candidate profiles holistically (skills, experience, location, salary expectations) and matching them against job requirements using semantic similarity rather than just keyword matching.

**Success Metrics:**
- Recommendation relevance score (comparison against gold standard dataset)
- System response time (<500ms for top-20 recommendations)
- Test coverage (all V-model levels passing)

### Technical Constraints (Non-Negotiable)

1. **Architecture:** 3 microservices (User Profile, Job Catalog, Recommendation Engine)
2. **Technology:** Python 3.12+, FastAPI, Redis Streams, PostgreSQL
3. **Deployment:** Docker-compose, runs locally with `docker compose up`
4. **Data:** Synthetic data only (500 users, 2000 jobs, pre-seeded)
5. **Streaming:** Must demonstrate Redis Streams event-driven pattern
6. **Isolation:** No external StepStone services or APIs
7. **Testing:** Must pass all 4 V-model test levels (unit, integration, contract, E2E)

### Non-Functional Requirements (Lax for Training)

**Performance:**
- Recommendation generation: <2 seconds for top-20 results
- API response times: <500ms (p95)
- No specific throughput requirements (single-user scenarios acceptable)

**Scalability:**
- Not required for v1 (local docker-compose only)
- Design should be stateless (for future horizontal scaling discussion)

**Reliability:**
- No HA requirements (single instance of each service acceptable)
- Basic error handling (don't crash on invalid input)

**Observability:**
- Structured logging (JSON format)
- Basic metrics (request count, response times) - nice-to-have

**Security:**
- No authentication/authorization (out of scope)
- Basic input validation (SQL injection prevention, JSON schema validation)

### Out of Scope (Clarifications)

**Explicitly NOT included in exercise:**
- User authentication/authorization
- Frontend UI (Swagger UI only)
- Email/notification delivery
- Real-time WebSocket updates
- Job application workflow
- Recruiter/employer features
- Analytics dashboards
- Production deployment (K8s, cloud)
- Integration with external StepStone services

### Domain Context

**StepStone Glossary:**
- **Candidate:** Job seeker with profile (skills, experience, preferences)
- **Job listing / Job ad:** Open position posted by employer
- **Application:** Candidate applying to specific job (out of scope for this exercise)
- **Recommendation:** Personalized job suggestion for candidate
- **Quality score:** Relevance score for job recommendation (0.0-1.0)
- **Interaction:** User action (search, job view, profile update)

**Example User Scenario:**
> Maria is a Senior Backend Engineer with 8 years of Python experience. She updates her profile to add "Kubernetes" to her skills list. The Recommendation Engine detects the profile update event, recalculates her recommendations, and surfaces 5 new DevOps-heavy backend roles that match her expanded skillset. Maria views the top 3 recommendations, which triggers job view events. These events will influence future recommendations (e.g., signal interest in remote-first companies).

---

## MATD Workflow Mapping

### Phase 0: Foundation (Pre-Exercise)

**Provided by organizers:**
- System Constitution (`constitution/technical-constitution.md`)
- Test Strategy (`qa/test-strategy.md`)
- Synthetic data + schema
- Gold standard dataset
- V-Model research report (TBD)
- Initial product brief (this document, condensed version)

### Phase 1: Specification (matd-specifier, matd-critical-thinker)

**Teams create:**
- Product summary (`docs/business/product-summary.md`)
- Feature specifications (`specs/job-recommendations.md`)
  - Job Stories format
  - Gherkin scenarios (Given/When/Then)
- Requirements validation (matd-critical-thinker red team review)

**MATD command:** `/matd-01-specification "Job Recommendation Engine with event-driven architecture"`

### Phase 2: Design (matd-architect, matd-c4-*)

**Teams create:**
- Solution design (`design/solution-design.md`)
  - 4 views: Decomposition, Dependency, Interface, Data
- ADRs (`design/adr-XXX-{topic}.md`)
  - **Note:** ADR topics are decided during human/AI collaboration (e.g., "Why Redis Streams over Kafka?", "Why embed model locally vs API?")
- C4 diagrams (Context, Container, Component)

**MATD command:** `/matd-02-design`

### Phase 3: Refinement (matd-architect, matd-qa)

**Teams create:**
- OpenAPI contracts (3 files)
- Event schemas (JSON Schema)
- Test design (`tests/test-design.md`)
- Implementation plan (`plan.md`)
- Task breakdown (local Jira-style task files)

**MATD command:** `/matd-03-refine`

### Phase 4: Implementation (matd-dev, matd-qa)

**Teams create:**
- Code (3 microservices)
- Unit tests (pytest)
- Integration tests (pytest + testcontainers)
- Contract tests (Schemathesis)
- E2E tests (Playwright)
- Implementation notes (`implementation-notes.md`)
- Workflow summary (`workflow-summary.md`)

**MATD command:** `/matd-04-implement`

---

## Template Mapping

**Available templates** (from analysis by subagent aaf2ca305103cf6ea):

### Phase 0 (Foundation)
- ✅ `system-constitution-template.md` - Tech radar, NFRs, compliance
- ✅ `qa/test-strategy-template.md` - Test pyramid, patterns, tools

### Phase 1 (Specification)
- ✅ `specs/product-brief-template.md` - Product vision, personas, KPIs
- ✅ `spec-template.md` - Feature specification (8 sections)

### Phase 2 (Design)
- ✅ `solution-design-template.md` - 4 views
- ✅ `adr-template.md` - ADR (2 versions: detailed 5.1K, simplified 2.8K)

### Phase 3 (Refinement)
- ✅ `test-design-template.md` - Test strategy, AC mapping
- ❌ OpenAPI contract template (MISSING - will be created)
- ⚠️ Event schema template (partial - embedded in solution-design)
- ❌ Data Producer Contract template (MISSING - will be added before exercise)
- ❌ Data Consumer Contract template (MISSING - will be added before exercise)

### Phase 4 (Implementation)
- ✅ `implementation-notes-template.md` - RED→GREEN evidence
- ✅ `arch-review-template.md` - Architecture review
- ✅ `code-review-template.md` - Code quality review
- ✅ `workflow-summary-template.md` - Artifact trail, metrics

**Gap mitigation:**
Templates missing for Phase 3 (OpenAPI, data contracts) will be created before workshop. These are critical for contract-first development.

---

## Open Questions

### Question 14: V-Model Research Report (PENDING DECISION)

**Options:**
- **A)** Create report now (pre-workshop research by spec author)
- **B)** Create report during workshop (first exercise for teams)
- **C)** Create report now, teams read as prerequisite material

**Report structure:**
1. V-Model overview (development ↔ testing mapping)
2. 4 test levels for microservices (unit/integration/contract/E2E)
3. Testing tools for each level
4. Concrete examples for Job Recommendation Engine
5. Code examples vs concepts only

**Location:** `/home/minged01/repositories/harness-workplace/harness-tooling/docs/deep-research/v-model-testing-microservices.md`

---

## Next Steps

1. **Decide:** V-Model research report creation approach (Question 14)
2. **Create:** System Constitution (tech stack, NFRs, compliance)
3. **Generate:** Synthetic data SQL seeds (500 users, 2000 jobs, interactions)
4. **Define:** Complete database schema (4 schemas: profiles, jobs, interactions, recommendations)
5. **Calculate:** Gold standard recommendations (50 test users × top-20 jobs)
6. **Write:** Initial product brief (condensed version of this document)
7. **Create:** Missing Phase 3 templates (OpenAPI, data contracts)
8. **Package:** Workshop materials (foundation docs + initial brief)
9. **Test:** Run through MATD workflow end-to-end (validation)

---

## References

- MATD Plugin Spec: [matd-plugin-spec.md](matd-plugin-spec.md)
- MATD Workflow Commands: [harness-tooling/.agents/commands/matd-*.md](../../.agents/commands/)
- SpecKit Extension: [harness-tooling/spec-kit-multi-agent-tdd/](../../spec-kit-multi-agent-tdd/)
- Template Analysis: Subagent aaf2ca305103cf6ea (2026-05-13)
- StepStone AI Risk Assessor: `/mnt/c/obsidian_work/claude-code/.claude/skills/ai-risk-assessor/SKILL.md`
