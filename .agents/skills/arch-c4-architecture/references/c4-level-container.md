# C4 Level: Container

## Purpose

Container level shows the deployable units that execute code, representing the high-level technical building blocks of the system and how responsibilities are distributed across them.

## What to Include (Scope)

**Focus on deployment units:**
- Containers (deployable/executable units)
- High-level technology choices
- How responsibilities are distributed
- Container communication patterns
- Container interfaces (APIs)

**Key container types:**
- Web applications
- API applications
- Databases
- Message queues
- File systems
- Microservices
- Lambda functions

**Documentation elements:**
- Container descriptions and purposes
- Technology stacks (this is where tech details belong)
- Component mappings (which components in each container)
- API specifications (OpenAPI/Swagger)
- Container relationships and dependencies
- Deployment configurations
- Infrastructure requirements

## What to Exclude (Boundaries)

**Not at this level:**
- Code-level details (save for Code level)
- Business context (covered at Context level)
- Detailed component logic (Component level shows this)
- Implementation details within containers

**Avoid:**
- Function signatures
- Class hierarchies
- Individual code files
- Low-level protocols (unless critical to understanding)

## Key Elements to Show

### In Container Diagrams

Use Mermaid C4Container syntax:
- `Container()` for applications, services
- `ContainerDb()` for databases
- `Container_Queue()` for message queues
- `System_Boundary()` to group containers in your system
- `Container_Ext()` for external containers
- `System_Ext()` for external systems
- `Rel()` showing protocols (HTTP, gRPC, SQL, etc.)

### In Documentation

**Per Container:**
- Name and description
- Type (Web App, API, Database, Queue, etc.)
- Technology stack (Node.js, Python, PostgreSQL, etc.)
- Deployment type (Docker, Kubernetes, Lambda, etc.)
- Components contained
- Interfaces exposed (APIs with OpenAPI specs)
- Dependencies on other containers
- Infrastructure requirements

**API Specifications:**
- OpenAPI/Swagger for REST APIs
- GraphQL schemas
- gRPC proto files
- Message queue schemas
- Links from container docs to specs

**Deployment Details:**
- Links to Dockerfiles
- Kubernetes manifests
- Terraform configs
- Scaling strategies
- Resource requirements

## When to Use This Level

- Documenting deployment architecture
- Showing how system is distributed
- Defining API contracts between containers
- Planning infrastructure
- Understanding technology choices
- After Component-level documentation
- Before Context-level documentation

## Examples

### Good Container Diagram
```mermaid
C4Container
    title Container Diagram for E-Commerce Platform

    Person(customer, "Customer", "Shops online")
    System_Boundary(platform, "E-Commerce Platform") {
        Container(webApp, "Web Application", "React, TypeScript", "Customer-facing UI")
        Container(apiGateway, "API Gateway", "Node.js, Express", "Routes requests to services")
        Container(productService, "Product Service", "Python, FastAPI", "Manages products")
        Container(orderService, "Order Service", "Java, Spring Boot", "Handles orders")
        ContainerDb(productDb, "Product Database", "PostgreSQL", "Stores product data")
        ContainerDb(orderDb, "Order Database", "MongoDB", "Stores order data")
        Container_Queue(eventBus, "Event Bus", "RabbitMQ", "Async messaging")
    }
    System_Ext(paymentGateway, "Payment Gateway", "Processes payments")

    Rel(customer, webApp, "Uses", "HTTPS")
    Rel(webApp, apiGateway, "Makes API calls", "JSON/HTTPS")
    Rel(apiGateway, productService, "Routes to", "REST")
    Rel(apiGateway, orderService, "Routes to", "REST")
    Rel(productService, productDb, "Reads/writes", "SQL")
    Rel(orderService, orderDb, "Reads/writes", "NoSQL")
    Rel(orderService, eventBus, "Publishes events")
    Rel(orderService, paymentGateway, "Processes payment", "API")
```

### Good Container Documentation
```markdown
### API Gateway Container

- **Name**: API Gateway
- **Type**: API Application
- **Technology**: Node.js 18, Express 4.x, TypeScript
- **Deployment**: Docker container on Kubernetes

#### Purpose
Routes incoming HTTP requests to appropriate microservices. Handles authentication, rate limiting, and request transformation.

#### Components
- Request Router (c4-component-router.md)
- Auth Middleware (c4-component-auth.md)
- Rate Limiter (c4-component-ratelimit.md)

#### Interfaces

**REST API**
- **Specification**: [openapi-gateway.yaml](./specs/openapi-gateway.yaml)
- **Endpoints**:
  - `GET /api/products` - List products
  - `POST /api/orders` - Create order
  - `GET /api/orders/{id}` - Get order

#### Dependencies
- Product Service (REST API calls)
- Order Service (REST API calls)
- Auth Service (JWT validation)

#### Infrastructure
- **Deployment**: k8s/api-gateway-deployment.yaml
- **Scaling**: Horizontal (3-10 pods)
- **Resources**: 512MB RAM, 0.5 CPU
```

## Common Mistakes

**Missing technology details:**
- ❌ Not specifying tech stack
- ❌ Generic "Database" without type
- ✅ "PostgreSQL 15", "Redis 7", "React 18"
- ✅ This is WHERE technology belongs in C4

**No API specifications:**
- ❌ Just saying "provides API"
- ❌ Missing OpenAPI/Swagger docs
- ✅ Link to complete API specs
- ✅ Document all interfaces properly

**Confusing containers with components:**
- ❌ Showing logical groupings instead of deployment units
- ❌ Not matching actual deployment reality
- ✅ One container = one deployable/executable unit
- ✅ Map to actual Docker containers, services, processes

**Missing component mappings:**
- ❌ Not linking to contained components
- ❌ No traceability to Component level
- ✅ List all components in each container
- ✅ Link to component documentation

**Unclear communication protocols:**
- ❌ Just lines without protocols
- ❌ "Uses" without specifying how
- ✅ "REST over HTTPS", "gRPC", "SQL", "AMQP"
- ✅ Show technology choices clearly

**Not showing external systems:**
- ❌ Only showing internal containers
- ❌ Missing third-party services
- ✅ Include all external dependencies
- ✅ Show third-party APIs, databases, services

## Tips for Effective Container Diagrams

**Map to deployment reality:**
- Analyze Dockerfiles, K8s manifests, cloud configs
- One container = one process/deployment unit
- Match actual infrastructure
- Don't guess - check deployment configs

**Document all interfaces:**
- Create OpenAPI specs for REST APIs
- Document GraphQL schemas
- Specify message queue formats
- Link to API specifications

**Show technology choices:**
- This is the level for tech details
- Be specific: versions, frameworks, platforms
- Document why these technologies
- Show technology stack clearly

**Bridge components and deployment:**
- Map which components go in which containers
- Explain deployment groupings
- Show how components are packaged
- Link to Component documentation

**Think infrastructure:**
- How does this actually deploy?
- What needs to run for the system to work?
- What are the processes/services?
- What are the resource requirements?

## Workflow Position

- **Input**: Component documentation, deployment configs (Dockerfiles, K8s, Terraform)
- **After**: C4-Component level
- **Before**: C4-Context level
- **Output**: c4-container.md with container docs and API specs
- **Purpose**: Map logical components to physical deployment units
