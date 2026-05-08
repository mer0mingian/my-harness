# C4 Model Best Practices Reference

Comprehensive guide to the C4 model for software architecture based on Simon Brown's official guidelines and community best practices.

## Table of Contents

1. [Core Principles](#core-principles)
2. [The Four Levels](#the-four-levels)
3. [Progressive Disclosure](#progressive-disclosure)
4. [Notation Guidelines](#notation-guidelines)
5. [Common Anti-Patterns](#common-anti-patterns)
6. [Tool Recommendations](#tool-recommendations)
7. [Microservices Architectures](#microservices-architectures)
8. [Real-World Examples](#real-world-examples)
9. [Consistency Guidelines](#consistency-guidelines)
10. [References](#references)

## Core Principles

The C4 model is a lean graphical notation technique for modeling the architecture of software systems, created by Simon Brown in the early 2010s (around 2007). It provides "a set of hierarchical abstractions" for describing software architecture.

### Key Characteristics

- **Developer-friendly**: Designed specifically for technical teams
- **Easy to learn**: Accessible approach to architecture diagramming
- **Notation independent**: Flexible in visual representation; colors and styles are customizable
- **Tooling independent**: Not locked to specific software; works with whiteboards, code, or diagrams

### Fundamental Philosophy

"Good architecture is more than just good code—it's clear communication." The C4 model emphasizes storytelling over mere documentation. As Simon Brown states: "If a diagram with a dozen boxes is hard to understand, don't draw a diagram with a dozen boxes! Instead, switch from diagramming to modelling, think about what the story is you're trying to tell."

The model complements UML rather than replacing it, and the iconic blue-and-gray color scheme is optional, not mandatory.

## The Four Levels

The name "C4" stands for **Context, Container, Component, and Code** — four hierarchical diagram types that support progressive disclosure.

### Level 1: System Context

**Purpose**: Show the system in scope and its relationship with users and other systems.

**Audience**: Non-technical stakeholders, executives, product owners

**Key Guidelines**:
- Show the system boundary as a single box (black box view)
- Include external users (people) and external systems
- Limit to 5-10 external dependencies maximum
- Use business-friendly language; avoid technical jargon
- Focus on high-level business capabilities

**When to Stop Here**: Initial system boundary discussions, integration point identification, presentations to executives

**Example Elements**:
- User (Person)
- Mobile App User (Person)
- Internet Banking System (Software System, in scope)
- Mainframe Banking System (Software System, external)
- Email System (Software System, external)

### Level 2: Container

**Purpose**: Decompose a system into interrelated containers (applications and data stores).

**Audience**: Technical leads, architects, DevOps engineers

**Key Concept**: A "container" in C4 terminology is NOT a Docker container. It refers to any separately runnable or deployable unit:
- Web application
- Mobile app
- Database
- Message queue
- Serverless function
- Microservice

**Key Guidelines**:
- Show technology choices for each container
- Illustrate communication protocols between containers
- Container diagrams are the "workhorses of C4" — most commonly referenced for day-to-day architecture conversations
- Each container should be independently deployable or runnable

**When to Stop Here**: For most software development teams, Context + Container diagrams are sufficient. Only proceed to Component/Code when they genuinely add value.

**Example Containers**:
- Single Page Application (JavaScript, Angular)
- Web Application (Java, Spring MVC)
- API Application (Java, Spring Boot)
- Database (Oracle Database Schema)

### Level 3: Component

**Purpose**: Decompose containers into interrelated components and relate them to other containers or systems.

**Audience**: Developers, QA engineers

**Key Concept**: A component in C4 terms is a grouping of related code that lives behind a well-defined interface (non-deployable element):
- Controller
- Service layer
- Repository
- Authentication gateway
- Payment facade

**Key Guidelines**:
- Only create for containers with complex internal structure
- Components must belong to exactly one container
- Show relationships between components and external dependencies
- Document key responsibilities

**When to Stop Here**: Technical documentation needs, deep-dive implementation planning, onboarding developers to specific modules

**Common Anti-Pattern**: Confusing containers (deployable) vs components (non-deployable). Mixing these abstractions leads to modeling errors.

### Level 4: Code

**Purpose**: Provide additional details about the design of architectural elements that can be mapped to code.

**Audience**: Individual developers working on specific modules

**Key Guidelines**:
- Typically uses UML class diagrams or entity-relationship diagrams
- Often auto-generated from source code
- Only create for complex algorithms or critical components
- Most teams never need this level

**When to Stop Here**: Complex algorithm documentation, critical security components requiring detailed review

**Practical Reality**: Many organizations stop at Container or Component level, as code-level diagrams often add little value beyond what's in the source code itself.

## Progressive Disclosure

Progressive disclosure is the core design principle behind the C4 model's four-level hierarchy. It involves revealing information or complexity gradually rather than all at once.

### Why Four Levels?

The C4 model has four levels rather than one enormous diagram because:

1. **Audience Matching**: Different stakeholders need different levels of detail
2. **Cognitive Load Management**: Human comprehension limits require bounded complexity per diagram
3. **Navigation Efficiency**: Start broad, drill down only where needed
4. **Maintainability**: Smaller, focused diagrams are easier to keep up-to-date

### Hierarchical Approach in Practice

1. Start with System Context to align stakeholders on business scope
2. Progress to Container diagrams for technical team discussions
3. Create Component diagrams selectively for complex containers
4. Generate Code diagrams only for critical, complex components

### Nested Layouts

Progressive disclosure supports nested layouts: embedding smaller diagrams within the nodes of a larger diagram. This creates clickable drill-down navigation from Context → Containers → Components.

### Defining the Right Level

**Before creating any diagram, ask**:
- Who will read this diagram?
- What decisions do they need to make?
- What level of technical detail do they have?

## Notation Guidelines

The C4 model is notation independent, but consistency and clarity are essential.

### Diagram-Level Requirements

Every diagram must include:

1. **Title**: Descriptive title indicating type and scope
   - Example: "System Context diagram for Internet Banking System"
   - Example: "Container diagram for API Application"

2. **Legend/Key**: Explanation of notation elements
   - Shapes (boxes, cylinders, people icons)
   - Colors and their meanings
   - Line styles (solid, dashed, arrows)
   - Acronyms or abbreviations

3. **Element Metadata**:
   - Name
   - Type (Person, Software System, Container, Component)
   - Technology (for Containers and Components)
   - Description (brief, key responsibilities)

### Relationship Notation

- **Lines represent unidirectional relationships only**
- **Every line requires a label** consistent with direction and intent
  - Good: "Reads from and writes to"
  - Good: "Makes API calls to [HTTPS/REST]"
  - Bad: Unlabeled arrows
- **Container-to-container relationships must show technology/protocol**
  - HTTPS/REST
  - gRPC
  - Message Queue (Kafka, RabbitMQ)
  - SQL/JDBC

### Visual Design Principles

**Colors**:
- No prescribed color scheme (blue/gray is optional)
- Maintain consistency across diagrams
- Consider accessibility (colorblind-safe, black/white printing)
- Use color to group related elements or indicate layers

**Shapes**:
- People: Person icon or stick figure
- Software Systems: Rectangular boxes
- Databases: Cylinders
- Containers/Components: Rounded rectangles

**Layout**:
- Left-to-right or top-to-bottom flow for relationships
- Group related elements visually
- Minimize line crossings

### Self-Describing Diagrams

All diagrams should be self-contained and comprehensible without extensive explanation. Any notation used should be as self-describing as possible, but always include a key/legend to make notation explicit.

## Common Anti-Patterns

### Context Diagram Mistakes

#### 1. Showing Internal Containers

**Anti-Pattern**: Adding internal containers (individual services, databases) inside the system box.

**Why It's Wrong**: This indicates you've slipped into Container-level thinking. At Context level, the system box should be a black box.

**Fix**: Show only the system boundary as a single box; save internal decomposition for Container diagrams.

#### 2. Databases as External Systems

**Anti-Pattern**: Showing databases as external systems in Context diagrams.

**Why It's Wrong**: A database is part of your system, not an external dependency.

**Fix**: Databases belong in Container diagrams, not Context diagrams.

#### 3. Overloaded Context Diagrams

**Anti-Pattern**: Context diagram with 20+ external systems and 30+ interaction arrows.

**Why It's Wrong**: Unreadable and defeats the purpose of high-level overview.

**Fix**: 
- Group related external systems
- Create separate Context diagrams for different subsystems
- Focus on primary integration points

### Abstraction and Modeling Issues

#### 4. Adding Undefined Abstraction Levels

**Anti-Pattern**: Creating custom layers like "subcomponents," "subsystems," or "modules" between C4 levels.

**Why It's Wrong**: Reintroduces the chaos C4 aims to avoid. Each level in C4 serves a distinct, defined purpose.

**Fix**: Stick to the four defined levels. If a container is too complex, create a separate Component diagram for it.

#### 5. Confusing Containers vs Components

**Anti-Pattern**: Modeling non-deployable elements as containers or deployable units as components.

**Key Distinction**:
- **Container**: Deployable/runnable unit (web app, database, API service)
- **Component**: Non-deployable code grouping inside a container (controller, service, repository)

**Fix**: Ask "Can this be deployed independently?" If yes, it's a container. If no, it's a component.

#### 6. Overusing Subsystems

**Anti-Pattern**: Vague "subsystem" groupings that don't map to actual deployment or code structure.

**Why It's Wrong**: Produces superficial diagrams lacking meaningful architectural insight.

**Fix**: Use concrete C4 abstractions (System, Container, Component) instead of ambiguous groupings.

### External System Modeling Issues

#### 7. Over-Detailing External Systems

**Anti-Pattern**: Showing internal implementation details of external dependencies.

**Why It's Wrong**: Introduces coupling and volatility. External systems can change without your input.

**Fix**: Focus on boundaries and abstract interactions. Show only the interface you consume, not their internals.

### Container/Component Modeling Mistakes

#### 8. Shared Libraries as Containers

**Anti-Pattern**: Modeling reusable code libraries as separate containers.

**Why It's Wrong**: Libraries are not independently deployable; they're compiled into containers.

**Fix**: Represent shared libraries as components used by multiple containers, or simply note the technology stack.

#### 9. Single-Container Message Brokers

**Anti-Pattern**: Showing Kafka/RabbitMQ as a single "Message Broker" container when multiple topics/queues exist.

**Why It's Wrong**: Obscures pub/sub relationships and actual message flows.

**Fix**: Model individual topics/queues as separate containers to illustrate true producer-consumer relationships.

### General Diagram Quality Issues

#### 10. The Single Mega-Diagram

**Anti-Pattern**: Creating one diagram attempting to show everything — all containers, all relationships, all external systems.

**Why It's Wrong**: Particularly problematic for complex systems; results in unreadable diagrams.

**Fix**: 
- Create multiple focused diagrams
- Use progressive disclosure (Context → Container → Component)
- For microservices, create individual Container diagrams per service

#### 11. Removing Explanatory Text

**Anti-Pattern**: Stripping out element descriptions and relationship labels for "cleaner" diagrams.

**Why It's Wrong**: Creates ambiguity. Viewers must guess intent and responsibilities.

**Fix**: Adding detail improves clarity despite increased visual complexity. Every element and relationship should have descriptive text.

#### 12. Omitting Metadata

**Anti-Pattern**: Removing classification labels (like "Container," "Software System") or technology tags.

**Why It's Wrong**: Makes diagrams harder to interpret correctly. Viewers can't distinguish abstraction levels.

**Fix**: Always include type labels and technology choices on elements.

### Misunderstanding C4's Purpose

#### 13. Confusing Decision Documentation

**Anti-Pattern**: Using architecture diagrams to document decision-making processes.

**Why It's Wrong**: Architecture diagrams illustrate outcomes, not decision rationale.

**Fix**: Decisions belong in separate Architecture Decision Records (ADRs). Diagrams show the "what" and "how," ADRs explain the "why."

## Tool Recommendations

Simon Brown advocates for a **tool-agnostic approach** using the Structurizr DSL to define models once, then rendering across multiple tools.

### Tool Comparison Matrix

| Tool | Type | Pros | Cons | Best For |
|------|------|------|------|----------|
| **Structurizr** | DSL (code) | Single model, multiple views; no duplication; version control; official C4 reference | Steeper learning curve; requires text editing | Code-first teams; version-controlled architectures; single source of truth |
| **PlantUML** | DSL (code) | Free/open source; C4 support via library; CI/CD friendly; developer-focused | Auto-layout limitations; fixed styles | Diagrams in code repositories; automated generation |
| **Mermaid** | DSL (code) | Lightweight; Markdown-compatible; native GitHub/GitLab/Notion support | C4 support incomplete; complex diagrams hard to read | Documentation-embedded diagrams; quick sketches |
| **Visual C4** | Visual editor | Drag-and-drop; real-time collaboration; native ADR support | Commercial (free tier limited) | Teams integrating architecture decisions with diagrams |
| **IcePanel** | Visual editor | Interactive exploration; team collaboration; auto-sync | Commercial | Enterprise teams; stakeholder presentations |
| **draw.io** | Visual editor | Free; no account required; offline capable | No model consistency; manual updates | Quick ad-hoc diagrams; low-commitment exploration |

### General-Purpose Tool Warning

Simon Brown explicitly cautions against using Visio, Lucidchart, and similar general-purpose tools for software architecture, citing:

- No guidance or constraints
- Content and presentation mixed (can't separate data from styling)
- No model, no consistency across diagram levels
- Hard to diff in version control
- Limited automation capabilities
- Time-consuming to maintain

### Recommended Approach

1. **Define once with Structurizr DSL**: Write your architecture model in text
2. **Render everywhere**: Export to PlantUML, Mermaid, or interactive tools
3. **Version control the DSL source**: Treat architecture as code
4. **Choose presentation tool per audience**: Static diagrams for docs, interactive for workshops

**Key Quote from Simon Brown**:
> "Each diagramming tool has its own pros and cons, so using a tool agnostic format to define your model and views provides an easy way to try them all out, and reduce lock-in."

### Structurizr DSL Quick Example

```dsl
workspace "Internet Banking System" {
    model {
        user = person "Personal Banking Customer"
        
        internetBankingSystem = softwareSystem "Internet Banking System" {
            webApp = container "Web Application" {
                technology "Java and Spring MVC"
            }
            database = container "Database" {
                technology "Oracle Database Schema"
            }
        }
        
        user -> webApp "Uses"
        webApp -> database "Reads from and writes to"
    }
    
    views {
        systemContext internetBankingSystem {
            include *
            autolayout lr
        }
        
        container internetBankingSystem {
            include *
            autolayout lr
        }
        
        styles {
            element "Person" {
                shape person
            }
            element "Database" {
                shape cylinder
            }
        }
    }
}
```

## Microservices Architectures

The C4 model is particularly useful for microservices, but the approach depends on **organizational structure**, not just technical architecture.

### Pattern 1: Single Team, Single Software System

**When to Use**: One engineering team builds all microservices.

**Approach**: Treat microservices as an implementation detail:
- All microservices remain containers within a single software system boundary
- System Context diagram unchanged (microservices invisible externally)
- Container diagram shows all microservices
- Use color coding or grouping to show service boundaries

**Example**:
- System: "E-Commerce Platform"
- Containers: Order Service, Inventory Service, Payment Service, User Service, Notification Service (all within one system)

**Rationale**: Reflects single-team ownership and shared codebase reality.

### Pattern 2: Multiple Teams, Distributed Ownership

**When to Use**: Teams separately own microservices with autonomous deployment.

**Approach**: "Promote" microservices to independent software systems:
- Each microservice becomes its own software system with separate diagrams
- Create System Context diagrams from each team's perspective
- Reflects Conway's Law alignment (architecture mirrors org structure)
- Services interact as peer systems, not internal components

**Example**:
- Software System: "Order Management Service" (owned by Team A)
- Software System: "Inventory Management Service" (owned by Team B)
- Software System: "Payment Processing Service" (owned by Team C)
- Each has its own Context and Container diagrams

**Rationale**: Reflects organizational boundaries and autonomous team operation.

### Practical Guidance for Microservices

1. **Start with business capabilities**: System Context shows what the system does, not how it's implemented
2. **Choose approach based on ownership**: Single team = one system; multiple teams = multiple systems
3. **Don't show every microservice on one diagram**: Create focused views per service or business domain
4. **Model message brokers properly**: Individual topics/queues as containers, not a single "Kafka" box
5. **Show API gateways explicitly**: As containers that route to backend services

### Microservices Anti-Patterns Recap

- Showing 50 microservices on one Container diagram (unreadable)
- Modeling all microservices as separate systems when one team owns them (organizational mismatch)
- Treating service-to-service HTTP calls as "external system" relationships
- Omitting shared infrastructure (API gateway, service mesh, message broker)

## Real-World Examples

### Startup Evolution Case Study

**Phase 1: Monolith (Single Container)**
- System: "Ride-Sharing Platform"
- Container: Monolithic Web Application + Database
- One engineering team, simple deployment

**Phase 2: Microservices, Single Team**
- System: "Ride-Sharing Platform" (unchanged boundary)
- Containers: 
  - Ride Matching Service
  - Payment Service
  - Notification Service
  - User Service
  - Three databases (one per service)
- Still one team, but internal decomposition visible

**Phase 3: Distributed Ownership**
- Software System: "Ride Matching Service" (Team A)
- Software System: "Payment Service" (Team B)
- Software System: "Notification Service" (Team C)
- Each team has autonomy, separate release cycles

### E-Commerce Application Example

**System Context**:
- Person: "Customer"
- Software System: "E-Commerce Platform" (in scope)
- Software System: "Payment Gateway" (external, Stripe)
- Software System: "Email Service" (external, SendGrid)
- Software System: "Inventory Management" (external, legacy system)

**Container Diagram**:
- Web Application (React SPA)
- API Gateway (Node.js/Express)
- Product Catalog Service (Python/FastAPI)
- Order Processing Service (Java/Spring Boot)
- PostgreSQL Database (Product Data)
- MongoDB Database (Order Data)
- Redis Cache

### QR-Based Metro Ticket System

**System Context**:
- Person: "Commuter"
- Software System: "Metro Ticket System"
- Software System: "Payment Provider" (external)
- Software System: "Station Gate Controller" (external hardware)

**Container Diagram**:
- Mobile App (React Native)
- Ticketing API (Go)
- QR Code Generator Service (Python)
- Ticket Validation Service (Rust)
- PostgreSQL Database
- Redis Session Store

## Consistency Guidelines

### Across All Diagrams

1. **Notation Consistency**: Use the same shapes, colors, and line styles across all levels
2. **Naming Consistency**: Element names should remain consistent from Context → Container → Component
3. **Technology Labels**: Always specify technology stack at Container and Component levels
4. **Relationship Descriptions**: Use consistent terminology for similar interactions

### Setting Style Rules

Establish style guidelines that determine:
- Element shapes per type (Person = stick figure, Database = cylinder)
- Color schemes per layer or team ownership
- Line styles for different communication types (sync vs async)
- Font sizes and label placement

### Metadata Standards

Every diagram should include:
- **Title**: Clear, descriptive
- **Version/Date**: Last updated timestamp
- **Author/Owner**: Responsible team or individual
- **Legend**: Key for all notation used
- **Scope Statement**: What this diagram covers

### Integration with Definition of Done

- Architecture diagrams are living documentation
- Update diagrams when code changes architecture
- Assign ownership per major component
- Review diagrams during design reviews and retrospectives

### Template Approach

Create diagram templates rather than starting from blank canvases:
- Pre-defined styles for each element type
- Standard layout patterns
- Boilerplate legend and title blocks

## When to Create C4 Diagrams

### Always Create

1. **System Context**: For every new system or major platform
2. **Container Diagram**: For any system with multiple deployable units
3. **Onboarding Documentation**: Essential for new team members

### Create Selectively

1. **Component Diagrams**: Only for complex containers with intricate internal structure
2. **Code Diagrams**: Rarely; usually auto-generated for critical algorithms
3. **Dynamic Diagrams**: For complex workflows requiring sequence/flow visualization
4. **Deployment Diagrams**: When infrastructure and deployment topology matter

### Don't Create

1. **For Simple Systems**: A single-container web app may only need Context + Container
2. **For Stable, Well-Understood Architecture**: If the team knows it well and it rarely changes
3. **For Every Feature**: Not every user story requires a diagram update
4. **To Replace ADRs**: Diagrams show structure; ADRs document decisions

## Maintenance and Evolution

### Keeping Diagrams Current

**Strategies**:
- Embed diagram source (DSL) in code repositories
- Automate diagram generation from code where possible
- Include "update architecture diagrams" in Definition of Done
- Schedule quarterly architecture review sessions

**Warning Signs of Stale Diagrams**:
- Developers stop referencing them
- Diagrams contradict actual deployed systems
- New team members confused by diagrams
- Technology labels outdated (references deprecated frameworks)

### Versioning Diagrams

- Store diagrams in version control alongside code
- Tag diagram versions with software releases
- Maintain historical snapshots for legacy system understanding
- Use branches for proposed architectural changes

## Integration with Other Practices

### Architecture Decision Records (ADRs)

- **Diagrams**: Show the "what" and "how" of architecture
- **ADRs**: Document the "why" behind decisions
- **Integration**: Reference relevant diagrams in ADRs; link to ADRs from diagram documentation

### Documentation Systems

- Embed diagrams in:
  - README files (using Mermaid for GitHub rendering)
  - Confluence pages
  - Internal wikis
  - API documentation portals
- Use interactive tools (Structurizr Cloud, IcePanel) for explorable documentation

### Agile/Scrum Integration

- **Sprint Planning**: Reference Container diagrams for technical scope
- **Backlog Refinement**: Update diagrams when stories change architecture
- **Retrospectives**: Review diagram accuracy and usefulness
- **Definition of Done**: Include "architecture diagrams updated" where applicable

## Advanced Topics

### Large-Scale Systems

For systems with dozens of containers:
- Create focused views per business domain
- Use system landscape diagrams (zoom out from System Context)
- Implement filtering (show only security-related containers, only data flow, etc.)
- Use interactive tools for exploration

### Distributed Systems

For microservices/SOA:
- Show deployment topology separately from logical architecture
- Highlight synchronous vs asynchronous communication
- Model API gateways, service meshes, and proxies explicitly
- Document resilience patterns (circuit breakers, retries)

### Security Modeling

- Add trust boundaries to diagrams
- Show authentication/authorization flows
- Highlight data classification (PII, sensitive, public)
- Document encryption in transit and at rest

### Deployment Diagrams

Separate from Container diagrams, show:
- Infrastructure nodes (servers, VMs, containers, serverless)
- Container instances and scaling configuration
- Network topology and security groups
- Geographic distribution (regions, availability zones)

## Summary Checklist

When creating C4 diagrams, ensure:

- [ ] Diagram has a clear title indicating type and scope
- [ ] Legend/key explains all notation elements
- [ ] Every element has name, type, and description
- [ ] Containers and Components specify technology
- [ ] All relationships have directional labels
- [ ] Diagram matches intended audience level
- [ ] Notation is consistent across all diagrams
- [ ] Acronyms are defined
- [ ] Diagram is self-describing without extensive explanation
- [ ] External systems shown as black boxes
- [ ] No mixing of abstraction levels (e.g., containers and components on same diagram)
- [ ] Version/date stamp included
- [ ] Source stored in version control

## References

### Official C4 Model Resources

- [C4 Model Official Website](https://c4model.com/)
- [C4 Model Book (Simon Brown)](https://www.oreilly.com/library/view/the-c4-model/9798341660113/)
- [Visualising Software Architecture (PDF/iPad/Kindle)](https://leanpub.com/visualising-software-architecture)
- [Simon Brown's Website](https://simonbrown.je/)
- [C4 Model Wikipedia](https://en.wikipedia.org/wiki/C4_model)

### Best Practices and Guides

- [The Comprehensive Guide to the C4 Model - ArchiMetric](https://www.archimetric.com/the-comprehensive-guide-to-the-c4-model-for-software-architecture/)
- [C4 Model Diagrams: Practical Tips - Revision](https://revision.app/blog/practical-c4-modeling-tips)
- [Understanding C4 Model Levels - Visual C4](https://visual-c4.com/blog/4-cluster-understanding-c4-model-levels)
- [Diagramming Distributed Architectures with C4 - DEV Community](https://dev.to/simonbrown/diagramming-distributed-architectures-with-the-c4-model-51cm)
- [C4 Diagram Guide - CodeSee](https://www.codesee.io/learning-center/c4-diagram)

### Common Mistakes and Anti-Patterns

- [Misuses and Mistakes of the C4 Model - Working Software](https://www.workingsoftware.dev/misuses-and-mistakes-of-the-c4-model/)
- [C4 Model Misconceptions, Misuses, and Mistakes - GOTO 2024 (Video)](https://www.classcentral.com/course/youtube-the-c4-model-misconceptions-misuses-mistakes-simon-brown-goto-2024-310904)
- [GOTO 2024 Talk Session](https://gotocph.com/2024/sessions/3326/the-c4-model-misconceptions-misuses-and-mistakes)

### Progressive Disclosure

- [Progressive Disclosure - NN/G](https://www.nngroup.com/articles/progressive-disclosure/)
- [Progressive Disclosure - DevIQ](https://deviq.com/principles/progressive-disclosure/)
- [The Art and Science of Architecture Diagrams - Catio](https://www.catio.tech/blog/the-art-and-science-of-architecture-diagrams)
- [Optimizing AI Agents with Progressive Disclosure - Ardalis](https://ardalis.com/optimizing-ai-agents-with-progressive-disclosure/)

### Tools

- [Structurizr Official Documentation](https://docs.structurizr.com/)
- [Structurizr DSL Tutorial](https://docs.structurizr.com/dsl/tutorial)
- [Getting Started with Structurizr DSL - DEV](https://dev.to/simonbrown/getting-started-with-the-structurizr-dsl-34dh)
- [Software Architecture Diagrams - Which Tool? - DEV](https://dev.to/simonbrown/software-architecture-diagrams-which-tool-should-we-use-29e)
- [C4 Model Tools Comparison 2026 - Visual C4](https://visual-c4.com/blog/c4-model-tools-comparison-2026)
- [Top 9 Tools for C4 Model Diagrams - IcePanel](https://icepanel.io/blog/2025-08-28-top-9-tools-for-c4-model-diagrams)
- [Comparison of C4 Tooling - Optimal Relations](https://optimalrelations.se/blog/comparison-c4-tooling)
- [C4 Models with Structurizr - Dan Does Code](https://www.dandoescode.com/blog/c4-models-with-structurizr)

### Microservices and Real-World Examples

- [Microservices | C4 Model](https://c4model.com/abstractions/microservices)
- [Understanding Software Architecture with C4 - Real-World Examples - Medium](https://codefarm0.medium.com/understanding-software-architecture-a-journey-through-c4-model-with-real-world-examples-4a337fcbce26)
- [C4 Model for Software Architecture - InfoQ](https://www.infoq.com/articles/C4-architecture-model/)
- [Designing Microservices Architecture with C4 - vinisantos.dev](https://vinisantos.dev/posts/awesome-backend-part2-desining-microservices-architecture)

### Additional Learning Resources

- [C4 Model Intro - Samman Coaching](https://sammancoaching.org/learning_hours/architecture/simon_brown_4c_context.html)
- [C4 Model Complete Guide - Miro](https://miro.com/diagramming/c4-model-for-software-architecture/)
- [What is the C4 Model? - Visual Paradigm](https://www.visual-paradigm.com/guide/what-is-the-c4-model-a-comprehensive-guide-to-visualizing-software-architecture/)
- [C4 Model for Software Architecture - Medium (Franz Verdi)](https://franz-ajit.medium.com/the-c4-model-for-software-architecture-eab85e8f0491)

---

**Last Updated**: 2026-05-08

**Maintained By**: arch-c4-architecture skill

**License**: This reference document compiles publicly available information about the C4 model. The C4 model itself was created by Simon Brown and is freely available for use.
