"""PreAudit Guard — static, offline preflight scanner for unknown codebases.

Run it BEFORE installing dependencies, running tests, or feeding a repository's
source to an AI agent. It is a *quarantine* tool: it reports pre-audit risk
signals (prompt-injection traps, malicious lifecycle/build scripts, exposed
secrets) so they can be reviewed before any code is executed or trusted.

Safety invariant: this package NEVER executes target code, installs
dependencies, or makes network calls. It is a pure static text scanner.
"""

__version__ = "0.1.0"
