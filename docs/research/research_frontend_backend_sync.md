# Frontend-Backend Synchronization Research
## Design-First Workflows for STA2E VTT BMAD Integration

**Date**: 2026-04-26  
**Project**: Star Trek Adventures 2e Virtual Tabletop  
**Stack**: FastAPI + SQLAlchemy (async) + Pydantic | HTMX + Alpine.js + LCARS Design System  
**Testing**: pytest + pytest-playwright (E2E)

---

## Executive Summary

This research evaluates modern approaches to frontend-backend synchronization for rebuilding the STA2E VTT with a design-first workflow integrated into the BMAD (Breakthrough Method for Agile AI-Driven Development) methodology. The key findings recommend:

1. **DESIGN.md** as the UI design specification format for BMAD Analysis/PM phases
2. **OpenAPI 3.1** for API contract specification (FastAPI → HTMX frontend)
3. **WebSockets** for real-time multiplayer state synchronization (Momentum/Threat pools, bridge stations)
4. **Alpine.js global stores** for client-side state management synchronized with server state
5. **Contract testing** with OpenAPI validation to enforce frontend-backend contracts

---

## Section 1: DESIGN.md Workflow

### What is DESIGN.md?

DESIGN.md is an **open standard for design specifications** that combines machine-readable design tokens (YAML front matter) with human-readable design rationale (Markdown body). Recently [open-sourced by Google](https://blog.google/innovation-and-ai/models-and-research/google-labs/stitch-design-md/) through their Stitch project, it's becoming an industry standard for AI-assisted development workflows.

**Structure:**
```yaml
---
# Machine-readable design tokens
colors:
  primary: "#FF9900"
  secondary: "#CC6600"
typography:
  heading: "Orbitron"
  body: "Roboto"
spacing:
  unit: 8px
components:
  button:
    border-radius: 4px
    padding: "12px 24px"
---
# Design Rationale (Markdown)
## Why This Design System

LCARS interface requires high contrast, bold geometric shapes...
```

### Key Features

- **YAML Front Matter**: Colors, typography, spacing, border-radius, component definitions
- **Markdown Body**: Design rationale, usage guidelines, accessibility considerations
- **CLI Tools**: Validation (`lint`), version comparison (`diff`), Tailwind CSS generation (`tailwind`)
- **AI Agent Integration**: Files live alongside code, providing context for Claude/GPT/Gemini agents

### Workflow

1. **Prompt → Design Exploration** (using tools like [Shuffle.dev](https://shuffle.dev/design-md))
2. **Export DESIGN.md** from design tool
3. **Add to repository** alongside implementation code
4. **Agent consumption**: Coding agents (Claude Code, OpenCode) read DESIGN.md to preserve structure, component intent, and visual priorities

### Example Repositories Using DESIGN.md

- [getdesign.md](https://getdesign.md/) - Curated collection of DESIGN.md files for popular frameworks
- [Google Stitch examples](https://blog.google/innovation-and-ai/models-and-research/google-labs/stitch-design-md/)
- [Shuffle.dev DESIGN.md library](https://shuffle.dev/design-md)

### Benefits

- **Single source of truth** for design tokens and component specifications
- **Version control friendly** (plain text Markdown + YAML)
- **AI agent readable** - agents understand both tokens and rationale
- **Tooling support** - Generate Tailwind configs, validate WCAG contrast ratios
- **Human-readable** - Designers and developers can both review and edit

### Limitations

- **Emerging standard** - Still evolving, limited tooling ecosystem (2026)
- **Requires discipline** - Teams must keep DESIGN.md synchronized with implementation
- **Not a replacement for prototypes** - Static specification, not interactive mockups
- **Limited to visual design** - Doesn't cover behavioral specifications (state machines, API contracts)

**Recommendation for STA2E VTT**: Use DESIGN.md for LCARS design system specification (colors, typography, component geometry), but combine with OpenAPI for API contracts.

**Sources:**
- [Revolutionizing UI Design: Introducing the DESIGN.md Open Standard](https://www.franksworld.com/2026/04/22/revolutionizing-ui-design-introducing-the-design-md-open-standard/)
- [Google makes DESIGN.md open source](https://medium.com/design-bootcamp/google-makes-design-md-open-source-on-its-way-to-become-a-industry-standard-16119f2368dd)
- [getdesign.md — DESIGN.md collection for AI coding agents](https://getdesign.md/)

---

## Section 2: OpenDesign

### What is OpenDesign?

[OpenDesign (Open CoDesign)](https://github.com/OpenCoworkAI/open-codesign) is an **open-source alternative to Claude Design**, providing prompt-to-prototype capabilities with multi-model support and local-first workflows.

**Key Features:**
- **MIT Licensed** desktop app
- **Local-first architecture** - No cloud dependency
- **BYOK (Bring Your Own Key)** - Works with Claude, GPT, Gemini, DeepSeek, Kimi, GLM, Ollama
- **Built-in design skills** - Slide decks, dashboards, landing pages, SVG charts, data tables, calendars
- **Export formats** - HTML/CSS, React components, Tailwind classes

### Comparison to Claude Design

| Feature | Claude Design | OpenDesign |
|---------|--------------|------------|
| **License** | Proprietary (Anthropic) | MIT (Open Source) |
| **Hosting** | Cloud-only | Local-first |
| **Model Support** | Claude only | Multi-model (Claude, GPT, Gemini, Ollama) |
| **BYOK** | No | Yes |
| **Code Generation** | Limited (UI only) | Full-stack (UI + backend scaffolding) |
| **Offline Mode** | No | Yes (with local models) |

### Integration with AI-Assisted Development

OpenDesign fits into the **Design → Prototype → Implementation** workflow:

1. **Prompt Engineering** - Describe UI requirements in natural language
2. **Multi-Model Generation** - Use Claude Sonnet for complex layouts, GPT-4 for iterations, local Ollama for offline work
3. **Export Artifacts** - HTML/CSS, React components, or DESIGN.md format
4. **Agent Handoff** - Exported artifacts feed into BMAD's @make agent for implementation

### Workflow for STA2E VTT

```
User Prompt: "LCARS bridge station dashboard with Momentum/Threat pools"
    ↓
OpenDesign (Claude Sonnet) → Generate prototype
    ↓
Export → DESIGN.md + HTML/CSS components
    ↓
Review → Iterate with GPT-4 for refinements
    ↓
Commit → DESIGN.md to sta2e-vtt-lite/design/
    ↓
BMAD @make Agent → Read DESIGN.md, implement FastAPI + HTMX
```

### Limitations

- **Prototyping focused** - Not a replacement for contract specifications (OpenAPI)
- **Design quality varies** - Depends on model quality and prompt engineering
- **No state machine support** - Can't define multiplayer state transitions
- **Limited LCARS templates** - Custom Star Trek UI requires significant prompt engineering

**Recommendation for STA2E VTT**: Use OpenDesign for **rapid prototyping** during BMAD Analysis phase to validate UI concepts with stakeholders, but don't rely on it for production implementation. Export DESIGN.md artifacts for agent consumption.

**Sources:**
- [GitHub - OpenCoworkAI/open-codesign](https://github.com/OpenCoworkAI/open-codesign)
- [Open CoDesign | Open-Source AI Design Tool](https://opencoworkai.github.io/open-codesign/)
- [5 Claude Code Alternatives in 2026](https://www.builder.io/blog/claude-code-alternatives)

---

## Section 3: Recommended Approach for STA2E VTT

### 3.1 Design-First Architecture

**Core Principle**: Define contracts before implementation, using DESIGN.md for UI and OpenAPI for API.

```
┌─────────────────────────────────────────────────────────┐
│                    BMAD Analysis Phase                   │
│  - User stories (Mary the Analyst)                      │
│  - Competitor analysis                                   │
│  - Business requirements                                 │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ↓
┌─────────────────────────────────────────────────────────┐
│                    BMAD PM Phase                         │
│  - Feature prioritization                               │
│  - Design artifact creation:                            │
│    • DESIGN.md (LCARS UI specification)                 │
│    • OpenAPI 3.1 spec (API contracts)                   │
│    • State diagrams (scene lifecycle, bridge stations)  │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ↓
┌─────────────────────────────────────────────────────────┐
│                BMAD Architecture Phase                   │
│  - FastAPI project structure                            │
│  - SQLAlchemy models from OpenAPI schemas               │
│  - HTMX + Alpine.js component architecture              │
│  - WebSocket endpoints for real-time sync               │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ↓
┌─────────────────────────────────────────────────────────┐
│            BMAD Implementation (PRIES Loop)              │
│  PM: Validate OpenAPI contract → Pydantic models        │
│  Make: Generate FastAPI routes, HTMX templates          │
│  Test: Contract testing (OpenAPI), E2E (Playwright)     │
│  Review: API contract compliance, DESIGN.md adherence   │
│  Simplify: Refactor, optimize WebSocket handlers        │
└─────────────────────────────────────────────────────────┘
```

### 3.2 FastAPI + HTMX + Alpine.js Pattern

**Architecture Overview**: Server-driven UI with client-side state management.

#### Backend: FastAPI + Pydantic

**OpenAPI-First Approach:**
1. Define `openapi.yaml` upfront with all endpoints, schemas, and WebSocket paths
2. Generate Pydantic models from OpenAPI using [pydantic-to-typescript](https://github.com/phillipdupuis/pydantic-to-typescript)
3. Implement FastAPI routes that enforce the contract

**Example**: Momentum Pool API

```yaml
# openapi.yaml
paths:
  /api/momentum:
    get:
      summary: Get current Momentum pool
      responses:
        '200':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/MomentumPool'
    post:
      summary: Add Momentum point
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/MomentumAction'
      responses:
        '200':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/MomentumPool'

components:
  schemas:
    MomentumPool:
      type: object
      properties:
        player_momentum:
          type: integer
          minimum: 0
          maximum: 6
        gm_threat:
          type: integer
          minimum: 0
    MomentumAction:
      type: object
      required:
        - action_type
        - source_player_id
      properties:
        action_type:
          type: string
          enum: [add, spend, convert_to_threat]
        source_player_id:
          type: string
          format: uuid
```

**FastAPI Implementation:**

```python
# app/models/momentum.py (generated from OpenAPI)
from pydantic import BaseModel, Field

class MomentumPool(BaseModel):
    player_momentum: int = Field(ge=0, le=6)
    gm_threat: int = Field(ge=0)

class MomentumAction(BaseModel):
    action_type: Literal["add", "spend", "convert_to_threat"]
    source_player_id: UUID

# app/routes/momentum.py
from fastapi import APIRouter, HTTPException
from app.models.momentum import MomentumPool, MomentumAction

router = APIRouter(prefix="/api/momentum")

@router.get("", response_model=MomentumPool)
async def get_momentum():
    # Fetch from database
    return await db.get_momentum_pool()

@router.post("", response_model=MomentumPool)
async def update_momentum(action: MomentumAction):
    # Validate business logic
    pool = await db.get_momentum_pool()
    if action.action_type == "add":
        pool.player_momentum += 1
    # Broadcast to WebSocket clients
    await broadcast_momentum_update(pool)
    return pool
```

#### Frontend: HTMX + Alpine.js

**HTMX Pattern**: Server-driven UI updates via AJAX

```html
<!-- templates/components/momentum_pool.html -->
<div id="momentum-pool" 
     hx-get="/api/momentum" 
     hx-trigger="load, momentum-update from:body"
     hx-swap="outerHTML">
  <div class="lcars-panel momentum">
    <div class="momentum-player">
      <span class="label">Momentum</span>
      <span class="value">{{ player_momentum }}</span>
    </div>
    <div class="momentum-gm">
      <span class="label">Threat</span>
      <span class="value">{{ gm_threat }}</span>
    </div>
  </div>
  
  <!-- Add Momentum button -->
  <button 
    hx-post="/api/momentum" 
    hx-vals='{"action_type": "add", "source_player_id": "{{ player_id }}"}'
    hx-trigger="click"
    hx-target="#momentum-pool"
    class="lcars-button">
    Add Momentum
  </button>
</div>
```

**Alpine.js Pattern**: Client-side state for UI interactions

```html
<!-- Complex UI with local state -->
<div x-data="bridgeStation()" class="bridge-station">
  <!-- Alpine manages dropdown state -->
  <div x-show="stationMenuOpen" @click.away="stationMenuOpen = false">
    <button @click="stationMenuOpen = !stationMenuOpen">
      Select Station
    </button>
    <ul x-show="stationMenuOpen">
      <template x-for="station in stations">
        <li @click="selectStation(station)">{{ station.name }}</li>
      </template>
    </ul>
  </div>
  
  <!-- HTMX fetches server data when station changes -->
  <div 
    hx-get="/api/stations/:id/actions"
    hx-trigger="station-changed from:body"
    hx-swap="innerHTML">
    <!-- Server-rendered action list -->
  </div>
</div>

<script>
function bridgeStation() {
  return {
    stationMenuOpen: false,
    selectedStation: null,
    stations: Alpine.store('gameState').stations,
    
    selectStation(station) {
      this.selectedStation = station;
      this.stationMenuOpen = false;
      // Trigger HTMX request
      htmx.trigger(document.body, 'station-changed', {station_id: station.id});
    }
  }
}
</script>
```

### 3.3 Real-Time State Synchronization (Momentum/Threat Pools)

**Problem**: Multiplayer VTT requires instant state updates across all connected clients when Momentum/Threat changes.

**Solution**: WebSockets for real-time sync + HTMX for server-driven updates

#### WebSocket vs SSE Decision Matrix

| Feature | WebSocket | SSE | Recommendation |
|---------|-----------|-----|----------------|
| **Bi-directional** | Yes | No (server → client only) | **WebSocket** for multiplayer |
| **Latency** | <50ms typical | 100-200ms typical | **WebSocket** |
| **Browser Support** | Universal | Universal (HTTP/2) | Tie |
| **Firewall/Proxy** | May require port 80/443 | Works over HTTP | SSE easier |
| **Connection Overhead** | Persistent connection | Persistent connection | Tie |
| **Use Case Fit** | Real-time multiplayer | One-way notifications | **WebSocket** for VTT |

**Verdict**: Use **WebSockets** for Momentum/Threat pools due to bi-directional requirements (players and GM both send updates).

**Sources:**
- [HTMX Server-Sent Events vs WebSocket](https://htmx.org/extensions/sse/)
- [WebSockets vs. SSE vs. Long Polling](https://blog.openreplay.com/websockets-sse-long-polling/)
- [Server-Sent Events vs WebSockets 2026](https://www.nimbleway.com/blog/server-sent-events-vs-websockets-what-is-the-difference-2026-guide)

#### WebSocket Implementation

**FastAPI Backend:**

```python
# app/websocket/momentum.py
from fastapi import WebSocket, WebSocketDisconnect
from typing import List

class MomentumConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    async def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = MomentumConnectionManager()

@app.websocket("/ws/momentum")
async def momentum_websocket(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Receive action from client
            data = await websocket.receive_json()
            
            # Validate with Pydantic
            action = MomentumAction(**data)
            
            # Update database
            pool = await update_momentum_pool(action)
            
            # Broadcast to all clients
            await manager.broadcast({
                "type": "momentum_update",
                "data": pool.model_dump()
            })
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
```

**Frontend: HTMX + Alpine.js**

```html
<!-- Alpine.js global store for WebSocket state -->
<script>
document.addEventListener('alpine:init', () => {
  Alpine.store('gameState', {
    momentum: { player_momentum: 0, gm_threat: 0 },
    ws: null,
    
    init() {
      this.connectWebSocket();
    },
    
    connectWebSocket() {
      this.ws = new WebSocket('ws://localhost:8000/ws/momentum');
      
      this.ws.onmessage = (event) => {
        const msg = JSON.parse(event.data);
        if (msg.type === 'momentum_update') {
          this.momentum = msg.data;
          // Trigger HTMX refresh
          htmx.trigger(document.body, 'momentum-update');
        }
      };
    },
    
    sendAction(action) {
      this.ws.send(JSON.stringify(action));
    }
  });
});
</script>

<!-- HTMX component listens for WebSocket-triggered updates -->
<div id="momentum-pool" 
     hx-get="/api/momentum" 
     hx-trigger="momentum-update from:body"
     hx-swap="outerHTML"
     x-data>
  <div class="momentum-player">
    <span x-text="$store.gameState.momentum.player_momentum"></span>
  </div>
  <button @click="$store.gameState.sendAction({
    action_type: 'add',
    source_player_id: '{{ player_id }}'
  })">
    Add Momentum
  </button>
</div>
```

**Hybrid Pattern**:
1. **WebSocket** pushes real-time state changes to Alpine.js global store
2. **Alpine.js** updates reactive UI elements (numbers, counters)
3. **HTMX** handles complex UI re-renders triggered by WebSocket events
4. **FastAPI** serves as single source of truth (database + WebSocket broadcast)

**Sources:**
- [FastAPI WebSockets](https://fastapi.tiangolo.com/advanced/websockets/)
- [Managing Per-User WebSocket State in FastAPI](https://hexshift.medium.com/managing-per-user-websocket-state-in-fastapi-9ceaa2b312ac)

### 3.4 Alpine.js State Management Best Practices

**Core Principles** (from [Alpine.js state management guide](https://alpinejs.dev/essentials/state)):

1. **Use global stores only for cross-component state**
   - Momentum/Threat pools (shared across all players)
   - Bridge station assignments (multiple components need access)
   - Scene lifecycle (affects entire UI)

2. **Keep local x-data for component-specific state**
   - Dropdown open/closed state
   - Form validation errors
   - Modal visibility

3. **Persist state when necessary**
   - Use Alpine `$persist` plugin for user preferences (theme, station preference)
   - WebSocket reconnection logic should restore state from server

4. **Structure for multiplayer:**

```javascript
// Global store for shared game state
Alpine.store('gameState', {
  // Server-synchronized state (via WebSocket)
  momentum: { player_momentum: 0, gm_threat: 0 },
  scene: { id: null, status: 'inactive', bridges: [] },
  
  // Client-side connection state
  ws: null,
  connected: false,
  
  // Methods
  init() {
    this.connectWebSocket();
    this.loadPersistedPreferences();
  },
  
  // WebSocket handling
  connectWebSocket() { /* ... */ },
  
  // Actions that trigger server updates
  addMomentum(playerId) {
    this.ws.send(JSON.stringify({
      action_type: 'add',
      source_player_id: playerId
    }));
  }
});

// Per-component local state
function bridgeStationComponent() {
  return {
    // Local UI state (not synchronized)
    menuOpen: false,
    selectedAction: null,
    
    // Access global state
    get currentStation() {
      return Alpine.store('gameState').scene.bridges
        .find(b => b.player_id === this.playerId);
    },
    
    // Local actions
    toggleMenu() {
      this.menuOpen = !this.menuOpen;
    },
    
    // Actions that update server
    performAction(action) {
      fetch('/api/stations/action', {
        method: 'POST',
        body: JSON.stringify(action)
      }).then(response => {
        // Server will broadcast update via WebSocket
      });
    }
  }
}
```

**Sources:**
- [Alpine.js state management best practices](https://alpinejs.dev/essentials/state)
- [Alpine.js global stores usage guide](https://alpinedevtools.com/blog/stores-usage-guide)

### 3.5 Design-First Workflow File Structure

**Recommended Repository Structure** for sta2e-vtt-lite:

```
sta2e-vtt-lite/
├── design/
│   ├── DESIGN.md                    # LCARS UI specification
│   ├── openapi.yaml                 # API contract (single source of truth)
│   ├── state-machines/              # Mermaid diagrams for scene lifecycle
│   │   ├── scene-lifecycle.md
│   │   └── bridge-station-flow.md
│   └── prototypes/                  # OpenDesign exports (HTML/CSS)
│       ├── bridge-dashboard.html
│       └── character-sheet.html
│
├── backend/
│   ├── app/
│   │   ├── models/
│   │   │   ├── momentum.py          # Generated from openapi.yaml
│   │   │   ├── scene.py
│   │   │   └── station.py
│   │   ├── routes/
│   │   │   ├── momentum.py          # Implements OpenAPI contract
│   │   │   ├── scenes.py
│   │   │   └── stations.py
│   │   ├── websocket/
│   │   │   ├── momentum.py          # Real-time sync
│   │   │   └── scene.py
│   │   └── main.py
│   ├── tests/
│   │   ├── contract/                # OpenAPI validation tests
│   │   │   ├── test_openapi_compliance.py
│   │   │   └── conftest.py
│   │   └── e2e/
│   │       └── test_momentum_flow.py  # Playwright tests
│   └── pyproject.toml
│
├── frontend/
│   ├── static/
│   │   ├── css/
│   │   │   └── lcars.css            # Implements DESIGN.md tokens
│   │   ├── js/
│   │   │   ├── alpine-stores.js     # Global state management
│   │   │   └── websocket-client.js
│   │   └── images/
│   ├── templates/
│   │   ├── base.html
│   │   ├── components/
│   │   │   ├── momentum_pool.html   # HTMX component
│   │   │   ├── bridge_station.html
│   │   │   └── scene_lifecycle.html
│   │   └── pages/
│   │       ├── game_table.html
│   │       └── character_sheet.html
│   └── scripts/
│       └── generate-types.sh        # Pydantic → TypeScript (for future SPA)
│
└── docs/
    ├── BMAD-WORKFLOW.md             # Integration with BMAD phases
    └── API-USAGE.md                 # Generated from openapi.yaml
```

**Contract Enforcement:**

```yaml
# .github/workflows/contract-validation.yml
name: Contract Validation

on: [pull_request]

jobs:
  validate-contracts:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      # Validate OpenAPI spec
      - name: Validate OpenAPI
        run: |
          npx @stoplight/spectral-cli lint design/openapi.yaml
      
      # Validate FastAPI implements OpenAPI contract
      - name: Contract Testing
        run: |
          pytest tests/contract/ -v
      
      # Validate DESIGN.md tokens match CSS
      - name: Validate DESIGN.md
        run: |
          # Custom script to check DESIGN.md tokens vs lcars.css
          python scripts/validate-design-tokens.py
```

---

## Section 4: Integration with BMAD/PRIES

### 4.1 BMAD Phase Alignment

**BMAD Overview** (from [BMAD-METHOD documentation](https://docs.bmad-method.org/)):

BMAD defines specialized agents that mirror an agile team: Analyst (Mary), Product Manager (PM), Architect, Developer (@make), QA (@test), and an Orchestrator.

**Design Artifacts in BMAD Phases:**

```
┌───────────────────────────────────────────────────────────┐
│ Phase 1: Analysis (Mary the Analyst)                      │
├───────────────────────────────────────────────────────────┤
│ Inputs:                                                   │
│  - User stories                                           │
│  - Competitor analysis (TTRPG VTTs: Foundry, Roll20)      │
│  - Legacy documentation (sta2e_minimal_vtt/docs/)         │
│                                                           │
│ Outputs:                                                  │
│  - Product requirements document (PRD)                    │
│  - User journey maps (GM workflow, player workflow)       │
│  - Initial feature list                                   │
└───────────────────────────────────────────────────────────┘
                          │
                          ↓
┌───────────────────────────────────────────────────────────┐
│ Phase 2: Product Management (PM Agent)                    │
├───────────────────────────────────────────────────────────┤
│ Inputs:                                                   │
│  - PRD from Analysis phase                                │
│  - Design exploration (OpenDesign prototypes)             │
│                                                           │
│ Activities:                                               │
│  - Feature prioritization (Momentum/Threat → MVP)         │
│  - Design artifact creation:                              │
│    • DESIGN.md (LCARS specification)                      │
│    • openapi.yaml (API contracts)                         │
│    • State diagrams (Mermaid: scene lifecycle)            │
│                                                           │
│ Outputs:                                                  │
│  - design/DESIGN.md                                       │
│  - design/openapi.yaml                                    │
│  - design/state-machines/*.md                             │
│  - Prioritized backlog for Architecture phase             │
└───────────────────────────────────────────────────────────┘
                          │
                          ↓
┌───────────────────────────────────────────────────────────┐
│ Phase 3: Architecture (Architect Agent)                   │
├───────────────────────────────────────────────────────────┤
│ Inputs:                                                   │
│  - DESIGN.md (UI contracts)                               │
│  - openapi.yaml (API contracts)                           │
│  - State diagrams                                         │
│                                                           │
│ Activities:                                               │
│  - Generate Pydantic models from openapi.yaml             │
│  - Design SQLAlchemy schema (async)                       │
│  - Plan HTMX + Alpine.js component architecture           │
│  - Define WebSocket endpoints for real-time sync          │
│  - Create pytest + Playwright test strategy               │
│                                                           │
│ Outputs:                                                  │
│  - backend/app/models/*.py (Pydantic models)              │
│  - backend/app/db/models.py (SQLAlchemy ORM)              │
│  - backend/tests/contract/test_openapi.py                 │
│  - frontend/templates/components/*.html (stubs)           │
│  - Technical design document (TDD)                        │
└───────────────────────────────────────────────────────────┘
                          │
                          ↓
┌───────────────────────────────────────────────────────────┐
│ Phase 4: Implementation (PRIES Loop)                      │
├───────────────────────────────────────────────────────────┤
│ PM (Plan): Validate contracts                             │
│  - Read openapi.yaml                                      │
│  - Confirm Pydantic models match OpenAPI schemas          │
│  - Break down feature into tasks                          │
│                                                           │
│ Make (@make Agent): Implement feature                     │
│  - Read DESIGN.md for component styling                   │
│  - Generate FastAPI routes from openapi.yaml              │
│  - Create HTMX templates from design/prototypes/          │
│  - Implement WebSocket handlers                           │
│  - Write Alpine.js stores for client state                │
│                                                           │
│ Test (@test Agent): Validate implementation               │
│  - Contract tests (OpenAPI validation)                    │
│  - Unit tests (Pydantic model validation)                 │
│  - E2E tests (Playwright: Momentum flow)                  │
│  - WebSocket integration tests                            │
│                                                           │
│ Review: API contract compliance                           │
│  - Spectral lint openapi.yaml                             │
│  - Validate DESIGN.md tokens vs CSS                       │
│  - Code review (architecture adherence)                   │
│                                                           │
│ Simplify: Refactor                                        │
│  - Remove duplicate WebSocket handlers                    │
│  - Optimize Alpine.js global stores                       │
│  - Extract reusable HTMX components                       │
└───────────────────────────────────────────────────────────┘
```

### 4.2 PRIES Agents Consume Design Artifacts

**@make Agent** (Implementation):

```python
# Agent prompt context:
"""
You are implementing the Momentum pool feature.

Design contracts:
1. Read design/DESIGN.md for LCARS component styling (colors, typography, spacing)
2. Read design/openapi.yaml for API contract (/api/momentum endpoint)
3. Read design/state-machines/scene-lifecycle.md for Momentum rules

Implementation requirements:
- FastAPI route must match OpenAPI schema exactly
- HTMX template must use LCARS classes from DESIGN.md
- Pydantic model must validate Momentum constraints (0-6 player, 0+ threat)
- WebSocket broadcast must follow state diagram transitions

Validation:
- pytest tests/contract/test_openapi.py must pass
- DESIGN.md tokens must be present in lcars.css
"""
```

**@test Agent** (Validation):

```python
# Contract test generated from openapi.yaml
import pytest
from openapi_core import Spec
from openapi_core.validation.request import openapi_request_validator
from openapi_core.validation.response import openapi_response_validator

@pytest.fixture
def openapi_spec():
    with open('design/openapi.yaml') as f:
        return Spec.from_dict(yaml.safe_load(f))

def test_momentum_get_matches_contract(client, openapi_spec):
    """Validate /api/momentum GET response matches OpenAPI schema"""
    response = client.get("/api/momentum")
    
    # Validate against OpenAPI contract
    validator = openapi_response_validator.ResponseValidator(openapi_spec)
    result = validator.validate(
        request=MockRequest('/api/momentum', 'GET'),
        response=MockResponse(response.status_code, response.json())
    )
    
    assert not result.errors, f"OpenAPI contract violation: {result.errors}"

def test_momentum_post_enforces_schema(client, openapi_spec):
    """Validate /api/momentum POST enforces Pydantic schema"""
    invalid_payload = {
        "action_type": "invalid_action",  # Not in enum
        "source_player_id": "not-a-uuid"
    }
    
    response = client.post("/api/momentum", json=invalid_payload)
    assert response.status_code == 422  # Pydantic validation error
```

**Sources:**
- [BMAD Method Guide](https://docs.bmad-method.org/)
- [Integrating Specification-Driven Design into BMAD](https://github.com/bmad-code-org/BMAD-METHOD/issues/279)
- [API-First Development and Contract Testing 2026](https://dasroot.net/posts/2026/02/api-first-development-contract-testing/)

### 4.3 Validation Gates

**Contract Enforcement in CI/CD:**

```yaml
# .github/workflows/bmad-validation.yml
name: BMAD Contract Validation

on:
  pull_request:
    branches: [main, develop]

jobs:
  # Gate 1: Validate design artifacts exist and are valid
  design-artifacts:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Check DESIGN.md exists
        run: |
          if [ ! -f design/DESIGN.md ]; then
            echo "ERROR: design/DESIGN.md missing"
            exit 1
          fi
      
      - name: Validate OpenAPI spec
        run: |
          npx @stoplight/spectral-cli lint design/openapi.yaml \
            --ruleset https://stoplight.io/api/v1/projects/cHJqOjI/assets/rulesets/recommended
      
      - name: Validate DESIGN.md structure
        run: |
          # Check for required sections
          grep -q "^---" design/DESIGN.md || exit 1
          grep -q "colors:" design/DESIGN.md || exit 1
  
  # Gate 2: Ensure API implementation matches OpenAPI contract
  contract-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r backend/requirements.txt
          pip install pytest-openapi
      
      - name: Run contract tests
        run: |
          pytest backend/tests/contract/ -v --openapi-spec=design/openapi.yaml
  
  # Gate 3: Validate DESIGN.md tokens match CSS implementation
  design-token-validation:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Extract tokens from DESIGN.md
        run: |
          python scripts/extract-design-tokens.py \
            design/DESIGN.md > /tmp/design-tokens.json
      
      - name: Validate CSS matches tokens
        run: |
          python scripts/validate-css-tokens.py \
            /tmp/design-tokens.json \
            frontend/static/css/lcars.css
  
  # Gate 4: E2E tests with Playwright
  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r backend/requirements.txt
          playwright install
      
      - name: Run E2E tests
        run: |
          pytest backend/tests/e2e/ -v --headed
```

**Validation Script Examples:**

```python
# scripts/validate-css-tokens.py
import json
import re
import sys
import yaml

def extract_design_tokens(design_md_path):
    """Extract YAML front matter from DESIGN.md"""
    with open(design_md_path) as f:
        content = f.read()
    
    # Extract YAML front matter
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        raise ValueError("No YAML front matter found in DESIGN.md")
    
    return yaml.safe_load(match.group(1))

def validate_css_tokens(tokens, css_path):
    """Validate CSS variables match DESIGN.md tokens"""
    with open(css_path) as f:
        css_content = f.read()
    
    errors = []
    
    # Check colors
    for color_name, color_value in tokens.get('colors', {}).items():
        css_var = f"--color-{color_name}"
        if css_var not in css_content:
            errors.append(f"Missing CSS variable: {css_var}")
        elif color_value not in css_content:
            errors.append(f"Color value mismatch for {css_var}: expected {color_value}")
    
    # Check spacing
    spacing_unit = tokens.get('spacing', {}).get('unit')
    if spacing_unit and f"--spacing-unit: {spacing_unit}" not in css_content:
        errors.append(f"Spacing unit mismatch: expected {spacing_unit}")
    
    if errors:
        print("VALIDATION ERRORS:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    else:
        print("✓ All design tokens validated")

if __name__ == "__main__":
    tokens_json_path = sys.argv[1]
    css_path = sys.argv[2]
    
    with open(tokens_json_path) as f:
        tokens = json.load(f)
    
    validate_css_tokens(tokens, css_path)
```

### 4.4 Agent Handoff Points

**Key Handoff Points in BMAD Workflow:**

1. **Analysis → PM**
   - **Artifact**: Product Requirements Document (PRD)
   - **Validation**: PRD contains user stories, competitor analysis, feature list
   - **Next**: PM creates DESIGN.md and openapi.yaml

2. **PM → Architecture**
   - **Artifacts**: DESIGN.md, openapi.yaml, state diagrams
   - **Validation**: OpenAPI spec passes Spectral lint, DESIGN.md has required sections
   - **Next**: Architect generates Pydantic models, designs SQLAlchemy schema

3. **Architecture → Implementation (@make)**
   - **Artifacts**: Pydantic models, SQLAlchemy models, contract tests, HTMX templates (stubs)
   - **Validation**: Contract tests pass, models match OpenAPI schemas
   - **Next**: @make implements FastAPI routes, HTMX components, WebSocket handlers

4. **@make → @test**
   - **Artifacts**: Implemented features (FastAPI routes, HTMX templates, Alpine.js stores)
   - **Validation**: Contract tests pass, E2E tests pass, DESIGN.md tokens validated
   - **Next**: @test identifies bugs, @make fixes

5. **@test → Review**
   - **Artifacts**: Test reports (contract compliance, E2E results, code coverage)
   - **Validation**: All tests pass, OpenAPI contract enforced, DESIGN.md adherence verified
   - **Next**: Code review for architecture compliance

6. **Review → Simplify**
   - **Artifacts**: Code review feedback, refactoring opportunities
   - **Validation**: No regressions after refactoring (re-run contract + E2E tests)
   - **Next**: Merge to main, iterate with next PRIES cycle

**Agent Coordination Example:**

```bash
# BMAD orchestration script
# This would be invoked by the PRIES workflow plugin

# Step 1: PM creates design artifacts
echo "PM Agent: Creating design artifacts..."
claude-code /pm-agent \
  --input "design/PRD.md" \
  --output "design/DESIGN.md,design/openapi.yaml"

# Step 2: Validate design artifacts
echo "Validating design artifacts..."
npx @stoplight/spectral-cli lint design/openapi.yaml || exit 1

# Step 3: Architect generates models
echo "Architect Agent: Generating Pydantic models..."
claude-code /architect-agent \
  --input "design/openapi.yaml" \
  --output "backend/app/models/"

# Step 4: @make implements feature
echo "@make Agent: Implementing Momentum pool..."
claude-code /make \
  --context "design/DESIGN.md,design/openapi.yaml" \
  --task "Implement /api/momentum endpoint with WebSocket sync"

# Step 5: @test validates
echo "@test Agent: Running contract tests..."
pytest backend/tests/contract/ -v || exit 1

echo "@test Agent: Running E2E tests..."
pytest backend/tests/e2e/ -v || exit 1

# Step 6: Review
echo "Review: Validating DESIGN.md compliance..."
python scripts/validate-css-tokens.py \
  <(python scripts/extract-design-tokens.py design/DESIGN.md) \
  frontend/static/css/lcars.css
```

---

## Recommendations Summary

### For STA2E VTT BMAD Integration

1. **Use DESIGN.md** for LCARS UI specification
   - Create in BMAD PM phase
   - Define colors, typography, spacing, component geometry
   - Validate against CSS implementation in Review phase

2. **Use OpenAPI 3.1** for API contracts
   - Define upfront in BMAD PM phase
   - Generate Pydantic models in Architecture phase
   - Enforce with contract tests in PRIES loop

3. **Use WebSockets** for real-time state sync
   - Momentum/Threat pools require bi-directional communication
   - Broadcast state changes to all connected clients
   - Alpine.js global stores consume WebSocket messages

4. **Use Alpine.js global stores** for client state
   - Manage WebSocket connection state
   - Synchronize server state (Momentum, scenes) across components
   - Keep local x-data for UI-specific state (dropdowns, modals)

5. **Implement contract testing**
   - Validate FastAPI responses against OpenAPI schemas
   - Use pytest-openapi for automated validation
   - Enforce in CI/CD before merging

6. **Structure design artifacts for agent consumption**
   - DESIGN.md: LCARS visual tokens
   - openapi.yaml: API contracts
   - state-machines/*.md: Scene lifecycle, bridge station flows
   - All stored in `design/` directory, versioned alongside code

### Next Steps

1. **Phase 1: Legacy Documentation Extraction** (Completed per user context)
2. **Phase 2: BMAD Business Documentation** (In progress)
3. **Phase 3: Create Design Artifacts**
   - Use OpenDesign to prototype LCARS dashboard
   - Export DESIGN.md to `sta2e-vtt-lite/design/`
   - Define openapi.yaml for Momentum/Threat endpoints
4. **Phase 4: PRIES Workflow Plugin Design** (Opus agent task)
5. **Phase 5: Sandbox Attachment**
6. **Phase 6: Execute BMAD with design-first workflow**

---

## Blockers Encountered

**None**. All research queries returned comprehensive results. The recommended pattern (DESIGN.md + OpenAPI + WebSocket + Alpine.js) is well-documented with production examples.

---

## Additional Resources

### DESIGN.md
- [Shuffle.dev DESIGN.md](https://shuffle.dev/design-md)
- [Google Stitch Open Source Announcement](https://blog.google/innovation-and-ai/models-and-research/google-labs/stitch-design-md/)
- [getdesign.md Collection](https://getdesign.md/)

### OpenDesign
- [GitHub - OpenCoworkAI/open-codesign](https://github.com/OpenCoworkAI/open-codesign)
- [Open CoDesign Documentation](https://opencoworkai.github.io/open-codesign/)

### FastAPI + HTMX + Alpine.js
- [FastAPI + HTMX: The No-Build Full-Stack](https://blakecrosley.com/guides/fastapi-htmx)
- [HTMX FastAPI Patterns 2025](https://johal.in/htmx-fastapi-patterns-hypermedia-driven-single-page-applications-2025/)
- [Alpine.js State Management](https://alpinejs.dev/essentials/state)

### Real-Time Sync
- [FastAPI WebSockets](https://fastapi.tiangolo.com/advanced/websockets/)
- [HTMX SSE Extension](https://htmx.org/extensions/sse/)
- [WebSockets vs SSE 2026 Guide](https://www.nimbleway.com/blog/server-sent-events-vs-websockets-what-is-the-difference-2026-guide)

### Contract Testing
- [API-First Development and Contract Testing 2026](https://dasroot.net/posts/2026/02/api-first-development-contract-testing/)
- [Contract testing with OpenAPI](https://www.speakeasy.com/blog/contract-testing-with-openapi)

### BMAD Method
- [BMAD Method Documentation](https://docs.bmad-method.org/)
- [GitHub - BMAD-METHOD](https://github.com/bmad-code-org/BMAD-METHOD)
- [Integrating SDD into BMAD](https://github.com/bmad-code-org/BMAD-METHOD/issues/279)

---

**End of Research Document**
