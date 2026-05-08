# System Constitution: {{system_name}}

**System Name:** {{system_name}}  
**Version:** {{version|default("1.0")}}  
**Status:** {{status|default("draft")}}  
**Created:** {{timestamp}}

## Tech Radar

_Inventory of technologies, frameworks, and tools adopted by the system. Include version constraints, maturity levels (adopted/trial/assess), and reasoning for each choice._

**Technologies & Frameworks:**
- _Technology name_ (version: X.Y.Z, maturity: adopted/trial/assess) - _brief rationale_

**Platforms & Infrastructure:**
- _Platform name_ (maturity: adopted/trial/assess) - _brief rationale_

**Tools & Utilities:**
- _Tool name_ (version: X.Y.Z, maturity: adopted/trial/assess) - _brief rationale_

## Team Tech Skills

_Document the technical competencies and expertise areas of the team. Include skill gaps and planned training._

**Core Competencies:**
- _Skill/technology_ - proficiency level (beginner/intermediate/expert), team members qualified
- _Skill/technology_ - proficiency level (beginner/intermediate/expert), team members qualified

**Emerging Skills (Training Plan):**
- _Skill/technology_ - target proficiency level, training path/timeline

**Skill Gaps & Mitigation:**
- _Gap description_ - mitigation strategy or hiring plan

## Compliance & Governance

_Legal, regulatory, and organizational requirements. Include data protection, security standards, audit trails, and approval workflows._

**Data Protection & Privacy:**
- _Requirement_ - compliance framework (GDPR/CCPA/other), implementation status

**Security Standards:**
- _Standard name_ - scope and enforcement mechanism

**Audit & Compliance:**
- _Requirement_ - verification method and frequency

**Approval & Sign-Off Workflows:**
- _Process name_ - stakeholders and conditions for approval

## Non-Functional Requirements

### Observability

_Monitoring, logging, metrics, and tracing strategy. Include collection tools, retention policies, and alerting thresholds._

**Logging:**
- _What is logged_ - centralized system and retention policy

**Metrics & Monitoring:**
- _Metric name_ - collection method and alerting rules

**Tracing:**
- _Tracing requirements_ - tool and sampling strategy

**Dashboards & Alerting:**
- _Dashboard/alert name_ - purpose and on-call escalation

### Testing Strategy

_Test types, coverage targets, and validation frameworks. Include unit, integration, e2e, performance, security, and chaos testing._

**Test Coverage:**
- Unit test target: {{unit_test_coverage|default("80%")}}
- Integration test target: {{integration_test_coverage|default("60%")}}
- E2E test target: {{e2e_test_coverage|default("40%")}}

**Test Types:**
- _Test type_ - scope and validation criteria

**Test Environments:**
- _Environment name_ - configuration and data refresh strategy

**Test Data:**
- _Data type_ - generation method and privacy handling

### Performance

_Response time targets, throughput expectations, resource consumption limits, and optimization strategies._

**Response Time SLA:**
- {{response_time_p50|default("p50")}} {{response_time_p99|default("ms")}}
- {{response_time_p99|default("p99")}} {{response_time_p99_value|default("ms")}}

**Throughput & Capacity:**
- Expected requests per second: {{rps|default("TBD")}}
- Peak concurrent users: {{peak_concurrent|default("TBD")}}

**Resource Constraints:**
- Memory per instance: {{memory_limit|default("TBD")}}
- CPU per instance: {{cpu_limit|default("TBD")}}
- Storage per {{storage_unit|default("month")}}: {{storage_limit|default("TBD")}}

**Optimization Priorities:**
- _Priority area_ - target metric and approach

### Scalability

_Horizontal and vertical scaling capabilities, auto-scaling policies, and growth projections._

**Scaling Strategy:**
- Horizontal scaling: {{horizontal_scaling|default("enabled/disabled")}}, min/max instances: {{min_instances|default("TBD")}}/{{max_instances|default("TBD")}}
- Vertical scaling: {{vertical_scaling|default("yes/no")}}, max resource allocation: {{max_resources|default("TBD")}}

**Auto-Scaling Triggers:**
- Metric: {{scaling_metric|default("CPU/Memory/RPS")}}, threshold: {{scaling_threshold|default("TBD")}}

**Growth Projections:**
- Expected user growth: {{user_growth|default("TBD")}} per {{growth_period|default("quarter")}}
- Capacity planning horizon: {{planning_horizon|default("12 months")}}

**Bottleneck Identification:**
- Known bottlenecks and planned solutions: _list_

### Reliability

_Availability targets, fault tolerance, recovery strategies, and incident response procedures._

**Availability SLA:**
- Target uptime: {{uptime_target|default("99.9%")}}
- Planned maintenance windows: {{maintenance_window|default("TBD")}}

**Fault Tolerance:**
- Redundancy level: {{redundancy|default("single/multi-region/active-active")}}
- Failover mechanism: {{failover_mechanism|default("TBD")}}
- Recovery time objective (RTO): {{rto|default("TBD")}}
- Recovery point objective (RPO): {{rpo|default("TBD")}}

**Incident Response:**
- Incident severity levels: {{severity_levels|default("P1/P2/P3/P4")}} with response time SLAs
- Escalation path: {{escalation_path|default("TBD")}}
- Incident postmortem process: {{postmortem_process|default("TBD")}}

**Backup & Disaster Recovery:**
- Backup frequency: {{backup_frequency|default("TBD")}}
- Backup retention: {{backup_retention|default("TBD")}}
- Disaster recovery test cadence: {{dr_test_cadence|default("quarterly")}}

---

**Verification Checklist:**
- [ ] All sections populated with system-specific values
- [ ] Tech Radar reflects current technology stack
- [ ] Team skills documented with proficiency levels
- [ ] Compliance requirements aligned with legal team
- [ ] NFR targets are measurable and achievable
- [ ] Scalability and reliability strategies validated with ops team
- [ ] All placeholders ({{...}}) replaced with actual values or "TBD"
