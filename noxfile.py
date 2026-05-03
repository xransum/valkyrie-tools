"""Nox sessions."""

import functools
import gzip
import os
import re
import shlex
import shutil
import sys
import tempfile
import threading
import time
from contextlib import suppress
from datetime import datetime, timezone
from pathlib import Path
from textwrap import dedent
from typing import Any, Callable, Optional

import nox

try:
    import fcntl
    import pty
    import termios

    _HAVE_PTY = True
except ImportError:  # pragma: no cover - non-POSIX platforms
    _HAVE_PTY = False

package = "valkyrie_tools"

# ---------------------------------------------------------------------------
# Session log capture
#
# Each `nox` invocation writes its full stdout/stderr (installs, child
# commands, nox's own output) to etc/logs/nox.log. The first session of an
# invocation archives any pre-existing log to nox-<UTC-timestamp>.log.gz and
# prunes archives beyond LOG_RETENTION. Terminal colors are preserved via a
# pseudo-terminal when stdout is interactive; ANSI escapes and carriage
# returns are stripped from the log file so it stays grep-friendly. The
# etc/logs/ directory is gitignored.
# ---------------------------------------------------------------------------

LOG_DIR = Path("etc/logs")
LOG_FILE = LOG_DIR / "nox.log"
LOG_RETENTION = 10
LOG_OWNERSHIP_ENV = "_VALKYRIE_NOX_LOG_OWNED"

_LOG_INITIALIZED = False

# CSI sequences (covers SGR colors) and other 7-bit single-char escapes.
_ANSI_RE = re.compile(rb"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
# An ANSI escape that begins but does not yet terminate at end of buffer.
_DANGLING_ESC_RE = re.compile(rb"\x1B(?:\[[0-?]*[ -/]*)?$")
# Header line we write before each session, used to recover invocation start.
_HEADER_TS_RE = re.compile(
    rb"==== (\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z) session="
)


def _utc_iso() -> str:
    """Return the current UTC time as an ISO-8601 string."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _compact_ts(iso: str) -> str:
    """Convert ``2026-05-03T15:18:22Z`` to ``20260503T151822Z``."""
    return iso.replace("-", "").replace(":", "")


def _sanitize_for_log(data: bytes) -> bytes:
    """Strip ANSI escapes and normalize line endings for log storage."""
    cleaned = _ANSI_RE.sub(b"", data)
    cleaned = cleaned.replace(b"\r\n", b"\n").replace(b"\r", b"")
    return cleaned


def _extract_run_timestamp(path: Path) -> str:
    """Return the compact UTC timestamp of an existing log's first session.

    Falls back to the file's mtime if the header cannot be parsed.
    """
    with suppress(OSError):
        with open(path, "rb") as fp:
            head = fp.read(1024)
        match = _HEADER_TS_RE.search(head)
        if match:
            return _compact_ts(match.group(1).decode("ascii"))
    try:
        mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    except OSError:
        mtime = datetime.now(timezone.utc)
    return _compact_ts(mtime.strftime("%Y-%m-%dT%H:%M:%SZ"))


def _unique_archive_path(timestamp: str) -> Path:
    """Return a non-colliding archive path for the given timestamp."""
    candidate = LOG_DIR / f"nox-{timestamp}.log.gz"
    if not candidate.exists():
        return candidate
    counter = 1
    while True:
        candidate = LOG_DIR / f"nox-{timestamp}-{counter}.log.gz"
        if not candidate.exists():
            return candidate
        counter += 1


def _compress_to_gz(src: Path, dst: Path) -> bool:
    """Gzip-compress ``src`` to ``dst``; remove ``src`` on success."""
    try:
        with open(src, "rb") as src_fp:
            data = src_fp.read()
        with open(dst, "wb") as dst_fp:
            dst_fp.write(gzip.compress(data, compresslevel=6))
    except OSError as exc:
        sys.stderr.write(f"warning: failed to compress {src} -> {dst}: {exc}\n")
        return False
    with suppress(OSError):
        src.unlink()
    return True


def _prune_archives(max_keep: int = LOG_RETENTION) -> None:
    """Delete oldest archived runs beyond ``max_keep``."""
    try:
        archives = sorted(
            LOG_DIR.glob("nox-*.log.gz"),
            key=lambda p: p.stat().st_mtime,
        )
    except OSError:
        return
    excess = len(archives) - max_keep
    if excess <= 0:
        return
    for stale in archives[:excess]:
        with suppress(OSError):
            stale.unlink()


def _initialize_log_for_invocation() -> None:
    """Archive any prior ``nox.log`` and prune old archives.

    Called exactly once per nox invocation (gated by ``_LOG_INITIALIZED``).
    Skipped entirely when the ownership env var indicates a parent nox
    process already owns the active log file.
    """
    if os.environ.get(LOG_OWNERSHIP_ENV) == "1":
        return
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    if LOG_FILE.exists():
        try:
            size = LOG_FILE.stat().st_size
        except OSError:
            size = 0
        if size == 0:
            with suppress(OSError):
                LOG_FILE.unlink()
        else:
            timestamp = _extract_run_timestamp(LOG_FILE)
            archive = _unique_archive_path(timestamp)
            _compress_to_gz(LOG_FILE, archive)
    _prune_archives()
    os.environ[LOG_OWNERSHIP_ENV] = "1"


class _TeeFD:
    """Context manager that tees FDs 1/2 to ``etc/logs/nox.log``.

    On POSIX with an interactive stdout, a pseudo-terminal is used so child
    processes see a TTY and emit colors. The pump thread forwards raw bytes
    (with ANSI) to the original terminal FD and writes a sanitized copy
    (ANSI-stripped, CR-normalized) to the log file.
    """

    def __init__(self) -> None:
        self._log_fp: Any = None
        self._saved_stdout_fd: int = -1
        self._saved_stderr_fd: int = -1
        self._read_fd: int = -1
        self._write_fd: int = -1
        self._master_fd: int = -1
        self._slave_fd: int = -1
        self._use_pty: bool = False
        self._ansi_pending: bytes = b""
        self._thread: Optional[threading.Thread] = None

    def _flush_pending_to_log(self) -> None:
        """Write any buffered partial-escape bytes to the log."""
        if not self._ansi_pending:
            return
        cleaned = _sanitize_for_log(self._ansi_pending)
        self._ansi_pending = b""
        if cleaned:
            with suppress(OSError, ValueError):
                self._log_fp.write(cleaned)
                self._log_fp.flush()

    def _process_chunk(self, chunk: bytes) -> None:
        """Forward to terminal raw, write sanitized copy to log."""
        with suppress(OSError):
            os.write(self._saved_stdout_fd, chunk)
        buf = self._ansi_pending + chunk
        self._ansi_pending = b""
        match = _DANGLING_ESC_RE.search(buf)
        if match:
            self._ansi_pending = buf[match.start() :]
            buf = buf[: match.start()]
        cleaned = _sanitize_for_log(buf)
        if cleaned:
            with suppress(OSError, ValueError):
                self._log_fp.write(cleaned)
                self._log_fp.flush()

    def _pump(self) -> None:
        while True:
            try:
                chunk = os.read(self._read_fd, 4096)
            except OSError:
                break
            if not chunk:
                break
            self._process_chunk(chunk)
        self._flush_pending_to_log()

    def _open_pty(self) -> int:
        """Open a PTY pair and copy parent terminal window size."""
        self._master_fd, self._slave_fd = pty.openpty()
        with suppress(OSError):
            size = fcntl.ioctl(
                self._saved_stdout_fd, termios.TIOCGWINSZ, b"\0" * 8
            )
            fcntl.ioctl(self._slave_fd, termios.TIOCSWINSZ, size)
        self._read_fd = self._master_fd
        return self._slave_fd

    def __enter__(self) -> "_TeeFD":
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        self._log_fp = open(LOG_FILE, "ab", buffering=0)  # noqa: SIM115

        sys.stdout.flush()
        sys.stderr.flush()

        self._saved_stdout_fd = os.dup(1)
        self._saved_stderr_fd = os.dup(2)

        self._use_pty = _HAVE_PTY and os.isatty(self._saved_stdout_fd)
        if self._use_pty:
            write_fd = self._open_pty()
        else:
            self._read_fd, write_fd = os.pipe()

        os.dup2(write_fd, 1)
        os.dup2(write_fd, 2)
        os.close(write_fd)
        self._slave_fd = -1
        self._write_fd = -1

        self._thread = threading.Thread(target=self._pump, daemon=True)
        self._thread.start()
        return self

    def write(self, data: str) -> None:
        """Write a status line directly to the log (and terminal)."""
        payload = data.encode("utf-8", errors="replace")
        with suppress(OSError):
            os.write(self._saved_stdout_fd, payload)
        with suppress(OSError, ValueError):
            self._log_fp.write(_sanitize_for_log(payload))
            self._log_fp.flush()

    def _restore_fds(self) -> None:
        """Restore stdout/stderr FDs and release the saved duplicates."""
        with suppress(OSError):
            os.dup2(self._saved_stdout_fd, 1)
        with suppress(OSError):
            os.dup2(self._saved_stderr_fd, 2)
        for fd in (self._saved_stdout_fd, self._saved_stderr_fd):
            if fd != -1:
                with suppress(OSError):
                    os.close(fd)
        self._saved_stdout_fd = -1
        self._saved_stderr_fd = -1

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        with suppress(Exception):
            sys.stdout.flush()
            sys.stderr.flush()

        self._restore_fds()

        if self._read_fd != -1:
            with suppress(OSError):
                os.close(self._read_fd)
            self._read_fd = -1
            self._master_fd = -1

        if self._thread is not None:
            self._thread.join(timeout=2.0)

        if self._log_fp is not None:
            with suppress(OSError):
                self._log_fp.close()
            self._log_fp = None


def logged_session(func: Callable[..., None]) -> Callable[..., None]:
    """Tee a nox session's full output to ``etc/logs/nox.log``."""

    @functools.wraps(func)
    def wrapper(session: nox.Session, *args: Any, **kwargs: Any) -> None:
        global _LOG_INITIALIZED
        if not _LOG_INITIALIZED:
            _initialize_log_for_invocation()
            _LOG_INITIALIZED = True

        name = getattr(session, "name", func.__name__)
        py = getattr(session, "python", None) or "default"
        posargs = list(getattr(session, "posargs", []) or [])
        header = (
            f"\n==== {_utc_iso()} session={name} python={py} "
            f"posargs={posargs} ====\n"
        )

        tee = _TeeFD()
        started = time.monotonic()
        status = "success"
        exc_repr = ""
        with tee:
            tee.write(header)
            try:
                func(session, *args, **kwargs)
            except BaseException as e:
                status = "failure"
                exc_repr = f"{type(e).__name__}: {e}"
                raise
            finally:
                duration = int(time.monotonic() - started)
                footer_status = status
                if exc_repr:
                    footer_status = f"{status} ({exc_repr})"
                footer = (
                    f"==== {_utc_iso()} session={name} python={py} "
                    f"status={footer_status} duration={duration}s ====\n"
                )
                tee.write(footer)

    return wrapper


python_versions = [
    "3.11",
    "3.10",
    "3.9",
    "3.8",
    "3.12",
    "3.13",
    "3.14",
]

nox.needs_version = ">= 2022.11.21"
nox.options.sessions = (
    "pre-commit",
    "safety",
    "mypy",
    "tests",
    "xdoctest",
    "docs-build",
)
nox.options.default_venv_backend = "uv"
nox.options.reuse_existing_virtualenvs = True


def activate_virtualenv_in_precommit_hooks(session: nox.Session) -> None:
    """Activate virtualenv in hooks installed by pre-commit.

    This function patches git hooks installed by pre-commit to activate the
    session's virtual environment. This allows pre-commit to locate hooks in
    that environment when invoked from git.

    Args:
        session: The Session object.
    """
    assert session.bin is not None  # noqa: S101

    # Only patch hooks containing a reference to this session's bindir. Support
    # quoting rules for Python and bash, but strip the outermost quotes so we
    # can detect paths within the bindir, like <bindir>/python.
    bindirs = [
        bindir[1:-1] if bindir[0] in "'\"" else bindir
        for bindir in (repr(session.bin), shlex.quote(session.bin))
    ]

    virtualenv = session.env.get("VIRTUAL_ENV")
    if virtualenv is None:
        return

    headers = {
        # pre-commit < 2.16.0
        "python": f"""\
            import os
            os.environ["VIRTUAL_ENV"] = {virtualenv!r}
            os.environ["PATH"] = os.pathsep.join((
                {session.bin!r},
                os.environ.get("PATH", ""),
            ))
            """,
        # pre-commit >= 2.16.0
        "bash": f"""\
            VIRTUAL_ENV={shlex.quote(virtualenv)}
            PATH={shlex.quote(session.bin)}"{os.pathsep}$PATH"
            """,
        # pre-commit >= 2.17.0 on Windows forces sh shebang
        "/bin/sh": f"""\
            VIRTUAL_ENV={shlex.quote(virtualenv)}
            PATH={shlex.quote(session.bin)}"{os.pathsep}$PATH"
            """,
    }

    hookdir = Path(".git") / "hooks"
    if not hookdir.is_dir():
        return

    for hook in hookdir.iterdir():
        if hook.name.endswith(".sample") or not hook.is_file():
            continue

        if not hook.read_bytes().startswith(b"#!"):
            continue

        text = hook.read_text()

        if not any(
            Path("A") == Path("a")
            and bindir.lower() in text.lower()
            or bindir in text
            for bindir in bindirs
        ):
            continue

        lines = text.splitlines()

        for executable, header in headers.items():
            if executable in lines[0].lower():
                lines.insert(1, dedent(header))
                hook.write_text("\n".join(lines))
                break


@nox.session(name="pre-commit", python=python_versions[0])
@logged_session
def precommit(session: nox.Session) -> None:
    """Lint using pre-commit."""
    args = session.posargs or [
        "run",
        "--all-files",
        "--hook-stage=manual",
        # "--show-diff-on-failure",
    ]
    session.install(
        "black",
        "darglint",
        "flake8",
        "flake8-bandit",
        "flake8-bugbear",
        "flake8-docstrings",
        "flake8-rst-docstrings",
        "isort",
        "pep8-naming",
        "pre-commit",
        "pre-commit-hooks",
        "pyupgrade",
    )
    session.run("pre-commit", *args)
    if args and args[0] == "install":
        activate_virtualenv_in_precommit_hooks(session)


@nox.session(python=python_versions[0])
@logged_session
def safety(session: nox.Session) -> None:
    """Scan dependencies for insecure packages."""
    with tempfile.NamedTemporaryFile(
        suffix=".txt", delete=False
    ) as requirements_file:
        requirements_path = requirements_file.name

    session.run(
        "uv",
        "export",
        "--format=requirements-txt",
        "--no-dev",
        "--no-hashes",
        f"--output-file={requirements_path}",
        external=True,
    )
    session.install("safety")
    args = [
        "safety",
        "check",
        "--full-report",
        f"--file={requirements_path}",
    ]
    if os.path.exists(".safety") is True:
        with open(".safety", encoding="utf-8") as f:
            lines = [
                line.strip()
                for line in f.readlines()
                if line.strip() != "" and not line.strip().startswith("#")
            ]
            if len(lines) > 0:
                vulns = ",".join(lines)
                args.append(f"--ignore={vulns}")
    session.run(*args)


@nox.session(python=python_versions)
@logged_session
def mypy(session: nox.Session) -> None:
    """Type-check using mypy."""
    args = session.posargs or [
        "src",
        "tests",
        "docs/conf.py",
    ]
    session.install(
        ".",
        "mypy",
        "pytest",
        "importlib-metadata",
        "types-requests",
        "types-beautifulsoup4",
    )
    session.run("mypy", *args)
    if not session.posargs and session.python == python_versions[0]:
        session.run(
            "mypy", f"--python-executable={sys.executable}", "noxfile.py"
        )


@nox.session(python=python_versions)
@logged_session
def tests(session: nox.Session) -> None:
    """Run the test suite."""
    session.install(".")
    session.install(
        "coverage[toml]",
        "pytest",
        "pytest-datadir",
        "pygments",
        "typing_extensions",
    )

    try:
        session.run(
            "coverage", "run", "--parallel", "-m", "pytest", *session.posargs
        )
    finally:
        if session.interactive:
            session.notify("coverage", posargs=[])


@nox.session(python=python_versions[0])
@logged_session
def coverage(session: nox.Session) -> None:
    """Produce the coverage report."""
    args = session.posargs or ["report"]

    session.install("coverage[toml]")

    if not session.posargs and any(Path().glob(".coverage.*")):
        session.run("coverage", "combine")

    session.run("coverage", *args)


@nox.session(python=python_versions)
@logged_session
def typeguard(session: nox.Session) -> None:
    """Runtime type checking using Typeguard."""
    session.install(".")
    session.install("pytest", "typeguard", "pygments")
    session.run("pytest", f"--typeguard-packages={package}", *session.posargs)


@nox.session(python=python_versions)
@logged_session
def xdoctest(session: nox.Session) -> None:
    """Run examples with xdoctest."""
    if session.posargs:
        args = [package, *session.posargs]
    else:
        args = [f"--modname={package}", "--command=all"]
        if "FORCE_COLOR" in os.environ:
            args.append("--colored=1")

    session.install(".")
    session.install("xdoctest[colors]")
    session.run("python", "-m", "xdoctest", *args)


@nox.session(name="docs-build", python=python_versions[0])
@logged_session
def docs_build(session: nox.Session) -> None:
    """Build the documentation."""
    args = session.posargs or ["docs", "docs/_build"]
    if not session.posargs and "FORCE_COLOR" in os.environ:
        args.insert(0, "--color")

    session.install(".")
    session.install("sphinx", "furo", "myst-parser")

    build_dir = Path("docs", "_build")
    if build_dir.exists():
        shutil.rmtree(build_dir)

    session.run("sphinx-build", *args)


@nox.session(python=python_versions[0])
@logged_session
def docs(session: nox.Session) -> None:
    """Build and serve the documentation with live reloading on file changes."""
    args = session.posargs or ["--open-browser", "docs", "docs/_build"]
    session.install(".")
    session.install("sphinx", "sphinx-autobuild", "furo", "myst-parser")

    build_dir = Path("docs", "_build")
    if build_dir.exists():
        shutil.rmtree(build_dir)

    session.run("sphinx-autobuild", *args)
