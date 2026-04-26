"""harness-workflow-runtime — schemas, resolver, hooks, and commands for multi-agent CLI workflows."""

__version__ = "0.1.0"
# Workflow manifest schema major is tied to the runtime plugin's semver major.
# Workflows declare `runtime_min_version: "X.Y"`; runtime rejects on incompatible major.
__runtime_schema_major__ = 0
