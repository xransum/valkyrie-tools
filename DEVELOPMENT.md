# DEVELOPMENT

## Requirements

This project uses **pyenv** for managing Python versions and **uv** for
dependency management.

- Install pyenv: https://github.com/pyenv/pyenv#installation
  - Supported Python versions: `>=3.8,<4.0`
- Install uv: https://docs.astral.sh/uv/getting-started/installation/

Project setup:

```bash
pyenv install <python-version>
pyenv local <python-version>
uv sync
```

## Versioning

This project follows [Semantic Versioning](https://semver.org/) (`MAJOR.MINOR.PATCH`).

| Bump    | When to use                                                          | Example            |
| ------- | -------------------------------------------------------------------- | ------------------ |
| `MAJOR` | Breaking change - removes or incompatibly changes a public API       | `1.3.1` -> `2.0.0` |
| `MINOR` | Backward-compatible new feature or capability                        | `1.3.1` -> `1.4.0` |
| `PATCH` | Backward-compatible bug fix, dependency update, or internal refactor | `1.3.1` -> `1.3.2` |

Use `uv version` to bump the version in `pyproject.toml`:

```bash
uv version patch   # 1.3.1 -> 1.3.2
uv version minor   # 1.3.1 -> 1.4.0
uv version major   # 1.3.1 -> 2.0.0
```

Or set an explicit version:

```bash
uv version 1.5.0
```

Bump the version as part of the same commit that introduces the change.
Do not open a separate "version bump" PR unless it is a release-only commit.
The CI release workflow (`release.yml`) detects the new version tag on push to
`main` and publishes to PyPI automatically.

## Security Scan

The `safety` nox session exports the resolved dependency set from
`uv.lock` and runs `safety check` against it. Any detected vulnerability
causes the session and CI to fail.

### Running the scan

```bash
uv run nox -s safety
```

Run this session any time you add, remove, or update a dependency. It runs
automatically as part of the default nox suite.

### Reading the output

A failing scan prints a table like:

```
+==============================================================================+
| REPORT                                                                       |
+============================+===========+==========================+==========+
| package                    | installed | affected                 | ID       |
+============================+===========+==========================+==========+
| somepackage                | 1.2.3     | <1.2.4                   | 12345    |
+----------------------------+-----------+--------------------------+----------+
```

Each row gives you:

- **package** - the name of the vulnerable package
- **installed** - the version currently locked in `uv.lock`
- **affected** - the version range that contains the vulnerability
- **ID** - the Safety vulnerability ID (e.g. `12345`)

### Determining whether a fix is available

Check whether a patched version exists and is compatible:

```bash
# See all available versions of the package
uv tree --package somepackage

# Or check PyPI directly
pip index versions somepackage
```

If a safe version exists within the constraints in `pyproject.toml`, update
the lock file:

```bash
uv lock --upgrade-package somepackage
```

Then re-run the scan to confirm it is resolved:

```bash
uv run nox -s safety
```

### Tracing transitive vulnerabilities

If the vulnerable package is not a direct dependency (i.e. it does not appear
in `pyproject.toml`) use uv's dependency tree to find what pulls it in:

```bash
uv tree | grep -B 10 somepackage
```

Options once you identify the parent:

1. **Update the parent** - if a newer version of the parent ships with a
   patched transitive dep, update it: `uv lock --upgrade-package <parent-package>`
2. **Pin the transitive dep directly** - add it to `[project.dependencies]`
   with a safe version constraint as an override
3. **Suppress it** - only if the vulnerability is genuinely not exploitable in
   this project's context (see below)

### Suppressing a violation

`.safety` is strictly for two categories of violations:

1. **Dev-only dependencies** - packages listed under
   `[dependency-groups]` in `pyproject.toml` that are never
   installed in a user environment (e.g. `pytest`, `black`, `nox`, `sphinx`).
   A vulnerability in a dev tool poses no risk to end users.

2. **Non-actionable packages** - packages where no patched version exists yet,
   the vulnerability does not apply to this project's usage, or the Safety
   database entry is a known false positive with upstream confirmation.

If a vulnerability is in a **runtime dependency** (anything under
`[project.dependencies]`) and a fix is available, it must be fixed, not
suppressed.

To suppress an eligible violation, add the Safety ID (the integer, one per
line) to `.safety`:

```
# .safety - IDs suppressed from safety check
# <package> <version> - dev-only dependency, not shipped to users
12345
```

The nox session reads `.safety` and passes each ID as `--ignore=<id>`.

> **Do not add a runtime dependency violation to `.safety`** unless there is
> no fix available and the vector is confirmed unreachable. When in doubt,
> open an issue to track it rather than suppressing it.

## Quality Gates

All contributions must pass the full nox suite before a PR can be merged. Run
the default sessions with:

```bash
uv run nox
```

This runs, in order: `pre-commit`, `safety`, `mypy`, `tests`, `xdoctest`, `docs-build`.

### Session reference

| Session      | Command                    | What it checks                                                                        | When to run                                                                      |
| ------------ | -------------------------- | ------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| `pre-commit` | `uv run nox -s pre-commit` | Formatting (black, isort), linting (flake8), docstring style (darglint), file hygiene | Before every commit; always run before pushing                                   |
| `safety`     | `uv run nox -s safety`     | Known CVEs in runtime dependencies                                                    | Whenever dependencies change in `pyproject.toml` or `uv.lock`                    |
| `tests`      | `uv run nox -s tests`      | Pytest suite across all supported Pythons (3.8-3.14)                                  | After any logic change to `src/` or `tests/`                                     |
| `coverage`   | `uv run nox -s coverage`   | Aggregated coverage report; fails if below 100%                                       | After running `tests`; run to see which lines are uncovered                      |
| `mypy`       | `uv run nox -s mypy`       | Static type checking (not in default suite)                                           | When adding or changing type annotations; run manually to confirm no regressions |
| `typeguard`  | `uv run nox -s typeguard`  | Runtime type checking via Typeguard                                                   | When adding new public functions or changing call signatures                     |
| `xdoctest`   | `uv run nox -s xdoctest`   | `Example:` blocks in docstrings execute without error                                 | After adding or modifying docstring `Example:` blocks                            |
| `docs-build` | `uv run nox -s docs-build` | Sphinx build - must produce zero warnings                                             | After any change to `docs/` or public API docstrings                             |
| `docs`       | `uv run nox -s docs`       | Live-reload docs server for local review                                              | During active docs writing; not part of CI                                       |

When to run the full suite vs. individual sessions:

- **Iterating locally** - run only the session relevant to the change (e.g.
  `pre-commit` after formatting edits, `tests` after logic changes).
- **Before pushing a branch** - run the full suite (`uv run nox`) to catch
  anything CI will reject.
- **After adding dependencies** - always run `safety` in addition to `tests`.
- **mypy and typeguard** are not in the default suite; run them manually when
  type-related changes are involved.

### Pinning to a single Python version

The default suite runs `tests`, `xdoctest`, `mypy`, and `typeguard` across all
supported Python versions (3.8-3.14), which is the full CI matrix. During local
iteration you can restrict the entire suite to one interpreter with `-p`:

```bash
uv run nox -p 3.11
```

This runs every default session but only for Python 3.11, cutting out the
multi-version matrix overhead. Use the Python version that matches your active
virtualenv for the quickest feedback loop.

The `-p` flag works with individual sessions too:

```bash
uv run nox -s tests -p 3.11
```

### Session logs

Every nox invocation tees its full stdout and stderr (installs, child
commands, and nox's own output) to a repo-local log file:

```
etc/logs/nox.log
```

`nox.log` always reflects the most recent invocation. When a new invocation
starts, the previous `nox.log` is renamed using its first session's start
timestamp and gzip-compressed in place:

```
etc/logs/nox.log                         # current invocation (active)
etc/logs/nox-20260503T151822Z.log.gz     # previous invocations (archived)
etc/logs/nox-20260503T143901Z.log.gz
...
```

Up to 10 archives are retained; older ones are pruned automatically. The
`etc/logs/` directory is gitignored.

Terminal colors are preserved on interactive runs via a pseudo-terminal, but
ANSI escape sequences and carriage returns are stripped from the log file so
it stays clean for `grep`, `less`, and editors.

Each session block inside a log is wrapped with header and footer markers so
individual sessions are easy to locate:

```
==== 2026-05-03T14:22:01Z session=tests python=3.11 posargs=[] ====
... output ...
==== 2026-05-03T14:23:47Z session=tests python=3.11 status=success duration=106s ====
```

Useful inspection commands:

```bash
tail -n 200 etc/logs/nox.log                           # current run
grep -n 'session=tests' etc/logs/nox.log               # by session
grep -n 'status=failure' etc/logs/nox.log              # only failures
zcat etc/logs/nox-20260503T151822Z.log.gz              # any historical run
zgrep -l 'status=failure' etc/logs/nox-*.log.gz        # failed past runs
ls -1t etc/logs/nox-*.log.gz | head                    # most recent archives
```

## Pre-commit Hooks

Install the hooks once after cloning so they run automatically on `git commit`:

```bash
uv run pre-commit install
```

To run all hooks against every file manually (same as the nox `pre-commit` session):

```bash
uv run pre-commit run --all-files --hook-stage=manual
```

The active hooks are:

- **black** - formats Python to 80-character line length
- **isort** - sorts imports (profile: `black`)
- **flake8** - lints with the plugins listed below
- **darglint** - checks docstring argument/return coverage
- **pyupgrade** - upgrades syntax to Python 3.7+ idioms
- **prettier** - formats non-Python files (YAML, JSON, Markdown)
- **check-yaml / check-toml** - validates config file syntax
- **end-of-file-fixer / trailing-whitespace** - enforces clean line endings

## Code Style

### Formatting

- **black** enforces a maximum line length of **80 characters**.
- **isort** sorts imports with `profile = black` (no conflicts with black).

Run both manually:

```bash
uv run black src tests
uv run isort src tests
```

### Linting (flake8)

Active rule sets: `B, B9, C, D, DAR, E, F, N, RST, S, W`
Ignored codes: `E203, E501, RST201, RST203, RST301, W503`
Maximum cyclomatic complexity: **10**

Run manually:

```bash
uv run flake8 src tests
```

Key plugins and what they enforce:

| Plugin                  | Codes   | Enforces                                  |
| ----------------------- | ------- | ----------------------------------------- |
| `flake8-bugbear`        | `B, B9` | Common bug patterns and opinionated style |
| `flake8-docstrings`     | `D`     | PEP 257 docstring presence and format     |
| `flake8-rst-docstrings` | `RST`   | Valid RST inside docstrings               |
| `flake8-bandit`         | `S`     | Security anti-patterns                    |
| `pep8-naming`           | `N`     | PEP 8 naming conventions                  |
| `darglint`              | `DAR`   | Docstring arg/return/raises completeness  |

## Docstring Standards

All public functions, classes, and modules **must** have docstrings.

- Style: **Google** (enforced via `flake8-docstrings` + `darglint`)
- Strictness: **short** (one-line summary is sufficient for simple functions;
  Args/Returns/Raises sections are required whenever arguments, return values,
  or exceptions are present)
- Docstring convention is set in `.flake8`: `docstring-convention = google`

### Required sections

| Element present                   | Required sections                |
| --------------------------------- | -------------------------------- |
| Function with arguments           | `Args:`                          |
| Function with a return value      | `Returns:`                       |
| Function that raises an exception | `Raises:`                        |
| Key public function               | `Example:` (strongly encouraged) |

### Example docstring

```python
def resolve(hostname: str, record_type: str = "A") -> List[str]:
    """Resolve a DNS record for the given hostname.

    Args:
        hostname: The hostname to query.
        record_type: The DNS record type (e.g. ``"A"``, ``"MX"``).

    Returns:
        A list of resolved values for the record.

    Raises:
        dns.resolver.NXDOMAIN: If the hostname does not exist.

    Example:
        >>> resolve("example.com")
        ['93.184.216.34']
    """
```

If an example requires a live network call, mark it so xdoctest skips it:

```python
    Example:
        >>> resolve("example.com")  # doctest: +SKIP
        ['93.184.216.34']
```

## Type Annotations

All function signatures (arguments and return types) **must** be fully
annotated. mypy runs in strict mode with the following flags enabled:

```
disallow_any_generics = true
disallow_subclassing_any = true
disallow_untyped_calls = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_return_any = true
no_implicit_reexport = true
strict_equality = true
```

Run mypy manually:

```bash
uv run mypy src tests docs/conf.py
```

> **Note**: mypy is not in the default nox session list; it is gated separately
> because some third-party stubs are incomplete. New code must still be fully
> annotated - do not use `# type: ignore` without a comment explaining why.

## Tests

Tests live in `tests/` and use pytest. Run them for the current Python version:

```bash
uv run pytest
```

With coverage:

```bash
uv run coverage run -m pytest
uv run coverage report
```

The nox `tests` session runs the suite across all supported Python versions
(3.8-3.14). If you only need to check one version locally, `pytest` directly
is sufficient during development.

## GitHub CLI

All GitHub interactions in this project are done through the
[GitHub CLI](https://cli.github.com/) (`gh`). Install it and authenticate once:

```bash
# Install (see https://cli.github.com/ for OS-specific instructions)
gh auth login
```

All commands below assume you are inside the repository directory.

### Viewing and managing issues

```bash
# List open issues
gh issue list

# List with a specific label
gh issue list --label bug
gh issue list --label enhancement

# View a specific issue
gh issue view 42

# Open an issue in the browser
gh issue view 42 --web

# Create an issue (opens an interactive prompt)
gh issue create

# Create an issue non-interactively
gh issue create \
  --title "[BUG] short description" \
  --label bug \
  --body "Steps to reproduce..."

# Close an issue
gh issue close 42 --comment "Fixed in #<PR number>"
```

### Working with pull requests

```bash
# List open PRs
gh pr list

# List all PRs (open + closed + merged)
gh pr list --state all

# View a PR
gh pr view 17

# Open a PR in the browser
gh pr view 17 --web

# Check the CI status on a PR
gh pr checks 17

# View the diff of a PR
gh pr diff 17

# Check out a PR locally to test it
gh pr checkout 17
```

#### Creating a PR (internal - branch on this repo)

```bash
gh pr create \
  --base main \
  --head <type>/<short-description> \
  --title "<type>: <summary>" \
  --body "$(cat <<'EOF'
## Summary
- <what changed and why>

## Testing
- <which nox sessions were run / what was verified>
EOF
)"
```

#### Creating a PR (external - branch on your fork)

```bash
gh pr create \
  --repo xransum/valkyrie-tools \
  --base main \
  --head <your-username>:<type>/<short-description> \
  --title "<type>: <summary>" \
  --body "$(cat <<'EOF'
## Summary
- <what changed and why>

## Testing
- <which nox sessions were run / what was verified>
EOF
)"
```

### Reviewing a PR

```bash
# Approve
gh pr review 17 --approve

# Request changes
gh pr review 17 --request-changes --body "Please address the following..."

# Leave a comment without a formal decision
gh pr review 17 --comment --body "Looks mostly good, one question..."
```

### Merging a PR

```bash
# Merge commit
gh pr merge 17

# Squash merge
gh pr merge 17 --squash

# Rebase merge
gh pr merge 17 --rebase

# Squash merge and delete the branch
gh pr merge 17 --squash --delete-branch
```

### Monitoring CI runs

```bash
# List recent workflow runs on the current branch
gh run list

# List runs for a specific workflow file
gh run list --workflow tests.yml

# Watch a run in real time
gh run watch

# View the logs of a specific run
gh run view <run-id> --log

# View only failed job logs
gh run view <run-id> --log-failed
```

### Releases

```bash
# List releases
gh release list

# View a specific release
gh release view v1.3.1

# Open the latest release in the browser
gh release view --web
```

---

## Contributing a Change

There are two workflows depending on whether you have write access to the
repository.

---

### Internal contributors (write access - branch + CR)

Use this workflow if you can push branches directly to `xransum/valkyrie-tools`.

#### 1. Sync main

```bash
git checkout main
git pull origin main
```

#### 2. Create a branch

```bash
git checkout -b <type>/<short-description>
```

Naming conventions:

- `feature/*` - new feature or capability
- `bugfix/*` - defect fix
- `hotfix/*` - urgent production fix

#### 3. Make changes, run quality gates

Run the full nox suite before pushing:

```bash
uv run nox
```

Fix any failures before continuing.

#### 4. Bump the version (if applicable)

If the change warrants a release, bump the version in `pyproject.toml`:

```bash
uv version patch   # bug fix or dependency update
uv version minor   # new backward-compatible feature
uv version major   # breaking change
```

Commit the version bump together with the change, not as a separate commit.

#### 5. Commit

```bash
git add -A
git commit -m "<type>: <summary>"
```

Commit message types and examples:

| Type    | Use for                          | Example                                            |
| ------- | -------------------------------- | -------------------------------------------------- |
| `feat`  | New feature                      | `feat: add DNS PTR record lookup`                  |
| `fix`   | Bug fix                          | `fix: handle None return from whois resolver`      |
| `chore` | Tooling, deps, CI, version bumps | `chore: bump safety ignores for dev tooling`       |
| `doc`   | Documentation only               | `doc: expand nox session reference in DEVELOPMENT` |

#### 6. Push the branch

```bash
git push -u origin <type>/<short-description>
```

#### 7. Open a CR (pull request)

```bash
gh pr create \
  --base main \
  --head <type>/<short-description> \
  --title "<type>: <summary>" \
  --body "$(cat <<'EOF'
## Summary
- <what changed and why>

## Testing
- <which nox sessions were run / what was verified>
EOF
)"
```

#### 8. Address review feedback

Push additional commits to the same branch; the PR updates automatically:

```bash
git add -A
git commit -m "fix: address PR feedback"
git push
```

---

### External contributors (no write access - fork + PR)

Use this workflow if you do not have push access to `xransum/valkyrie-tools`.

#### 1. Fork the repository

```bash
gh repo fork xransum/valkyrie-tools --clone
```

This creates `<your-username>/valkyrie-tools` and clones it locally. The
original repo is added as the `upstream` remote automatically by `gh`.

If you cloned manually, add the upstream remote yourself:

```bash
git remote add upstream https://github.com/xransum/valkyrie-tools.git
```

#### 2. Sync your fork with upstream

```bash
git checkout main
git fetch upstream
git merge upstream/main
git push origin main
```

#### 3. Create a branch on your fork

```bash
git checkout -b <type>/<short-description>
```

Use the same naming conventions as internal contributors (`feature/*`,
`bugfix/*`, `hotfix/*`).

#### 4. Make changes and run quality gates

Install dependencies and run the full nox suite:

```bash
uv sync
uv run nox
```

Fix any failures before continuing.

#### 5. Bump the version (if applicable)

```bash
uv version patch   # bug fix or dependency update
uv version minor   # new backward-compatible feature
uv version major   # breaking change
```

#### 6. Commit

```bash
git add -A
git commit -m "<type>: <summary>"
```

#### 7. Push to your fork

```bash
git push -u origin <type>/<short-description>
```

#### 8. Open a PR against the upstream repo

```bash
gh pr create \
  --repo xransum/valkyrie-tools \
  --base main \
  --head <your-username>:<type>/<short-description> \
  --title "<type>: <summary>" \
  --body "$(cat <<'EOF'
## Summary
- <what changed and why>

## Testing
- <which nox sessions were run / what was verified>
EOF
)"
```

#### 9. Address review feedback

Push additional commits to the branch on your fork:

```bash
git add -A
git commit -m "fix: address PR feedback"
git push
```

The PR in the upstream repo updates automatically.
