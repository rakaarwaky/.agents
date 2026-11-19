"""CLI entry point — the ``aa`` binary root dispatcher.

Thin root layer: it runs the import bootstrap (skill-authoring package
roots + shared ``shared.src`` namespace trees), then routes argv through
the dispatch table to the command handlers in
``modules.cli.src.root_cli_container``. The heavy per-verb bodies live in
that focused container module; this file keeps only the sentry +
correlation-id bootstrap and the global flag stripping (AES301).

Delegated actions (skill/connect/disconnect/daemon/service/backup)
keep calling the module surface functions, which contain the original
bodies as-is (see the module surface docstrings).
"""
from __future__ import annotations

import importlib
import os
import sys

from modules.shared.src.common.utility_logging_setup import (
    err,
    set_color_mode,
    set_verbosity,
)
from modules.shared.src.common.utility_paths_resolver import repo_root

ROOT = repo_root()

# The skills feature lives in TWO fully independent standalone packages
# (AES702, no shared layer): skills/skill-authoring/app/modules/
# exposes the design/discovery/governance/maintenance/observability/storage
# modules (each with its own agent),
# skills/skill-authoring/skill-traces/modules/ the `skills_traces` package.
# Each owns its own copies of the contract/taxonomy modules it needs; there
# is no cross-tree import. This entry point adds both namespace roots so
# either standalone package can be imported on demand.
for _skills_ns in (
    ROOT / "skills" / "skill-authoring" / "skill-traces" / "app" / "modules",
    ROOT / "skills" / "skill-authoring" / "skill-design" / "app" / "modules",
    ROOT / "skills" / "skill-authoring" / "skill-traces" / "modules",
    ROOT / "skills" / "skill-authoring" / "skill-design" / "modules",
    ROOT / "skills" / "skill-authoring" / "tools" / "modules",
):
    if _skills_ns.is_dir() and str(_skills_ns) not in sys.path:
        sys.path.insert(0, str(_skills_ns))

# The skill-authoring tools tree (tools/modules/) has discovery and cli
# packages with an inner src/ layout; add those so bare module imports
# like `from discovery.agent_discovery_orchestrator import ...` resolve
# alongside the flat layout packages (design, governance, maintenance, etc.).
for _skills_src in (
    ROOT / "skills" / "skill-authoring" / "tools" / "modules" / "discovery" / "src",
    ROOT / "skills" / "skill-authoring" / "tools" / "modules" / "cli" / "src",
):
    if _skills_src.is_dir() and str(_skills_src) not in sys.path:
        sys.path.insert(0, str(_skills_src))

# Extend shared.src.__path__ with ALL shared/src trees so
# shared.src.common.utility_skill_pack etc. resolve regardless of which
# standalone skills tree wins the ``shared`` namespace import.
for _shared_ns in (
    ROOT / "skills" / "skill-authoring" / "skill-traces" / "app" / "modules" / "shared",
    ROOT / "skills" / "skill-authoring" / "skill-traces" / "modules" / "shared",
    ROOT / "modules" / "shared",
    ROOT / "skills" / "skill-authoring" / "skill-design" / "app" / "modules" / "shared",
    ROOT / "skills" / "skill-authoring" / "skill-design" / "modules" / "shared",
):
    if _shared_ns.is_dir() and str(_shared_ns) not in sys.path:
        sys.path.insert(0, str(_shared_ns))
try:
    import shared.src as _shared_src_pkg
    _src_dirs = [
        ROOT / "skills" / "skill-authoring" / "skill-traces" / "app" / "modules" / "shared" / "src",
        ROOT / "skills" / "skill-authoring" / "skill-traces" / "modules" / "shared" / "src",
        ROOT / "modules" / "shared" / "src",
        ROOT / "skills" / "skill-authoring" / "skill-design" / "app" / "modules" / "shared" / "src",
        ROOT / "skills" / "skill-authoring" / "skill-design" / "modules" / "shared" / "src",
    ]
    for _ext in _src_dirs:
        if _ext.is_dir() and str(_ext) not in _shared_src_pkg.__path__:
            _shared_src_pkg.__path__.append(str(_ext))
except ImportError:
    pass

# Bridge the domain-package split in the skill-authoring tools tree:
# discovery keeps its agent+capability files under src/ while the
# contracts/taxonomy for every domain live in the shared kernel's
# same-named domain dir. Extending each domain package's __path__ lets
# `from <domain>.agent_*_orchestrator import ...` resolve across both
# halves in one import.
if os.path.isdir(ROOT / "skills" / "skill-authoring" / "tools" / "modules"):
    _tm = ROOT / "skills" / "skill-authoring" / "tools" / "modules"
    _sk = _tm / "shared" / "src"
    for _pkg_name, _extra in (
        ("discovery", (
            _tm / "discovery" / "src",
            _sk / "discovery",
        )),
        ("design", (
            _tm / "design" / "src",
            _sk / "design",
        )),
        ("governance", (
            _sk / "governance",
        )),
        ("maintenance", (
            _sk / "maintenance",
        )),
        ("observability", (
            _sk / "observability",
        )),
        ("storage", (
            _sk / "storage",
        )),
    ):
        try:
            _mod = importlib.import_module(_pkg_name)
            for _extra_path in _extra:
                _extra_str = str(_extra_path)
                if _extra_path.is_dir() and _extra_str not in _mod.__path__:
                    _mod.__path__.append(_extra_str)
        except ImportError:
            pass

from modules.cli.src.root_cli_container import (
    cmd_9router,
    cmd_backup,
    cmd_clean,
    cmd_completion,
    cmd_config,
    cmd_connect,
    cmd_daemon,
    cmd_disconnect,
    cmd_doctor,
    cmd_help,
    cmd_install,
    cmd_list,
    cmd_mcp,
    cmd_omniroute,
    cmd_reset,
    cmd_restore,
    cmd_run,
    cmd_service,
    cmd_skills,
    cmd_status,
    cmd_submodules,
    cmd_tool,
    cmd_uninstall,
    cmd_update,
    cmd_version,
)


def _dispatch(argv: list[str], ctx: dict | None = None) -> int:
    """Route argv[0] to the right action handler (1:1 port of the surface table)."""
    if not argv:
        return cmd_help([])
    cmd = argv[0]
    rest = argv[1:]
    dispatch_table = {
        # Meta / status
        "status": cmd_status, "doctor": cmd_doctor,
        "submodules": cmd_submodules, "clean": cmd_clean,
        "reset": cmd_reset, "version": cmd_version, "--version": cmd_version,
        "help": cmd_help, "-h": cmd_help, "--help": cmd_help,
        # Core noun-action (canonical)
        "tool": cmd_tool,
        "config": cmd_config,
        "skills": cmd_skills,
        "connect": cmd_connect, "disconnect": cmd_disconnect,
        "mcp": cmd_mcp, "completion": cmd_completion,
        # Daemons & services
        "9router": cmd_9router, "omniroute": cmd_omniroute,
        "service": cmd_service,
        "daemon": cmd_daemon,
        "backup": cmd_backup, "restore": cmd_restore,
        # Backward compat aliases → noun action (deprecated, prefer aa tool/aa skills)
        "install": cmd_install, "update": cmd_update, "uninstall": cmd_uninstall,
        "list": cmd_list, "ls": cmd_list, "run": cmd_run,
    }
    handler = dispatch_table.get(cmd)
    if not handler:
        err(f"Unknown command: {cmd}")
        print()
        cmd_help([])
        return 1
    return handler(rest)


def _gen_correlation_id() -> str:
    """Generate short correlation ID (P1-O4) for multi-step ops."""
    import uuid
    return uuid.uuid4().hex[:8]


def _init_sentry():
    """Opt-in Sentry error tracking (P1-O2), controlled by ARWAKY_SENTRY_DSN."""
    dsn = os.environ.get("ARWAKY_SENTRY_DSN", "")
    if not dsn:
        return
    try:
        import sentry_sdk
        sentry_sdk.init(dsn=dsn, traces_sample_rate=0.1)
    except ImportError:
        pass


def main(argv: list[str]) -> int:
    _init_sentry()
    os.environ["ARWAKY_CORRELATION_ID"] = _gen_correlation_id()
    if not argv:
        return cmd_help([])
    # Global flag: --no-color / --plain (P2-P1)
    if "--no-color" in argv or "--plain" in argv:
        set_color_mode(False)
        argv = [a for a in argv if a not in ("--no-color", "--plain")]
    if "--force-color" in argv:
        set_color_mode(True)
        argv = [a for a in argv if a != "--force-color"]
    # Global verbosity: -v / --verbose, -q / --quiet
    if "-v" in argv or "--verbose" in argv:
        set_verbosity("debug")
        argv = [a for a in argv if a not in ("-v", "--verbose")]
    if "-q" in argv or "--quiet" in argv:
        set_verbosity("warning")
        argv = [a for a in argv if a not in ("-q", "--quiet")]
    return _dispatch(argv)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))