# Contributor Guide

Thank you for your interest in improving this project.
This project is open-source under the [MIT license] and
welcomes contributions in the form of bug reports,
feature requests, and pull requests.

Here is a list of important resources for contributors:

- [Source Code]
- [Documentation]
- [Issue Tracker]
- [Code of Conduct]

[mit license]: https://opensource.org/licenses/MIT
[source code]: https://github.com/xransum/valkyrie-tools
[documentation]: https://valkyrie-tools.readthedocs.io/
[issue tracker]: https://github.com/xransum/valkyrie-tools/issues

## How to Report a Bug

Report bugs on the [Issue Tracker].

When filing an issue, make sure to answer these questions:

- Which operating system and Python version are you using?
- Which version of this project are you using?
- What did you do?
- What did you expect to see?
- What did you see instead?

The best way to get your bug fixed is to provide a test case,
and/or steps to reproduce the issue.

## How to Request a Feature

Request features on the [Issue Tracker].

## How to Setup your Development Environment

You need Python 3.8+ and [Poetry].

Install required system dependencies.

- **Ubuntu/Debian**:

  ```bash
  sudo apt install -y make build-essential libssl-dev zlib1g-dev \
  libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev \
  libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev python3-openssl git
  ```

- **CentOS/RHEL**:
  ```bash
  sudo yum install -y make gcc gcc-c++ openssl-devel zlib-devel \
  bzip2-devel readline-devel sqlite-devel wget curl llvm ncurses-devel \
  ncurses-libs xz-devel tk-devel libffi-devel xz git
  ```

Install [pyenv] to manage your Python versions:

```bash
curl https://pyenv.run | bash
```

Add the following [pyenv] environment variables your following
lines to your `~/.bashrc`:

```bash
# Pyenv environment variables
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
export PATH="$PYENV_ROOT/shims:$PATH"

# Pyenv init
eval "$(pyenv init --path)"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
```

Reload your terminal or run the following command:

```bash
source ~/.bashrc
```

Installing Poetry:

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

> **Info:** Use the following to uninstall Poetry:
>
> ```bash
> curl -sSL https://install.python-poetry.org | python3 - --uninstall
> ```

Reload your terminal or run the following command:

```bash
source ~/.bashrc
```

Install the Python package and all it's dependency requirements:

```bash
$ poetry install
```

> **Troubleshooting:** If you're using a GUI-based OS
> and you run commands like `poetry install`, `poetry upgrade`,
> or `poetry lock` and it's just loading forever at
> `Resolving dependencies...`, then add the flag `-vvv` to the
> command to see what's going on. If you see something where
> it's hanging on `keyring backends`.
>
> This is because the keyring package is trying to access
> your system's keyring, but it prompts a GUI popup for
> user credentials, but since you're not using the GUI,
> it hangs forever.
>
> However, to fix it either prepend this to every
> command you use or append it to your `~/.bashrc`:
>
> ```bash
> export PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring
> ```

You should now be able to drop into a [Python IDLE] shell within
the Poetry virtual environment using the following command:

```bash
poetry run python
```

Example Usage:

```bash
$ poetry run python
Python 3.11.6 (main, Oct 22 2023, 12:07:45) [GCC 11.4.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> from valkyrie_tools import __version__
>>> __version__
'0.1.0'
```

Or you can call [Nox] and run the `nox` sessions:

```bash
poetry run nox
```

Jump down to [How to Test the Project] for
more information on how to run the `nox` sessions.

## How to Test the Project

To test anything and everything within the project, we use [Nox]. Nox is a
Python automation toolkit that helps in automating tests, linting, code
formatting, security checks, code coverage, and so on.

> **Important:** Only use `nox` through the `poetry run nox` command, this
> will ensure that the `nox` command is using the correct Python version
> and the correct virtual environment, as this is what all of the Git
> actions use to test pull requests and commits.

To run the `nox` sessions, you can run the following command:

```bash
poetry run nox
```

Before ever pushing any changes to the project, you need to ensure all
nox sessions are passing without any errors or warnings, this is because
the Git actions will run the `nox` sessions to ensure that the project
is fully CI/CD compliant.

If you want to run a specific session, you can run the following command:

```bash
poetry run nox --session=<session_name>
# or
poetry run nox -s <session_name>
```

> **Important:** Do **not** change the `noxfile.py` file so that your code
> will pass the tests, the `noxfile.py` file is configured to run the tests
> on specific Python versions to ensure that the project is compatible with
> all the Python versions that are defined in the `noxfile.py` file.

## Understanding Nox Sessions

If you have a general understanding of how nox sessions work, you can
jump to [Linting and Code Formatting].

When you run the `nox` command, it will run the `default` session,
which is defined in the `noxfile.py` file as the following:

```python
nox.options.sessions = (
    # <session names>
)
```

You can view all of the available nox sessions defined by running the
following command:

```bash
poetry run nox --list-sessions
# or
poetry run nox -l
```

It may seem like a long list, but it's not that bad. The sessions are
grouped by the Python version(s) that they are running on.

Let me provide an example, let's create a session function named
`do_a_thing` within the `noxfile.py` file that has a session name
`do-a-thing` and utilizes Python versions `3.8` and `3.11`:

```python
@nox.session(name="do-a-thing", python=["3.11", "3.8"])
def do_a_thing(session):
    """Do a thing."""
    ...
```

Even though we added a session function, it will not show up in the list
of sessions, this is because we have not added it to the `nox.options.sessions`
tuple, so let's add it:

```python
nox.options.sessions = (
    "do-a-thing",
)
```

Now if we run the following command:

```bash
poetry run nox --list-sessions
# or
poetry run nox -l
```

You will see the following output:

```bash
Available sessions:
* do-a-thing-3.11 -> Do a thing.
* do-a-thing-3.8 -> Do a thing.
```

And finally, we can run all sessions by running the following command:

```bash
poetry run nox --session=do-a-thing
```

This will create 4 sessions, each session going by the namencalature of
`<session_name>-<python_version>` and in the order in which we defined
the Python versions in the decorator, for example:

```bash
* do-thing-3.11 -> Do a thing.
* do-thing-3.8 -> Do a thing.
* do-thing-3.9 -> Do a thing.
* do-thing-3.10 -> Do a thing.
```

If we were to call the session by just it's name `do-thing`, it will run
all 4 sessions, for example:

```bash
poetry run nox --session=do-thing
# or
poetry run nox -s do-thing
```

However, we can also call a specific session by it's name and Python version,
heavily reducing runtime on small changes, for example:

```bash
poetry run nox --session=do-thing-3.11
# or
poetry run nox -s do-thing-3.11
```

You can also lock the Python version to a specific version, for example:

```bash
poetry run nox --session=do-thing --python=3.11
# or
poetry run nox -s do-thing -p 3.11
```

## Linting and Code Formatting

To quickly lint and format your code, you can run the following command:

```bash
poetry run nox --session=pre-commit
# or
poetry run nox -s pre-commit
```

## Unit Testing

If you want to run the tests, you can run the following command:

```bash
poetry run nox --session=tests
# or
poetry run nox -s tests
```

If you want to run a test quickly without running the full test suite,
you can specify the Python version, for example:

```bash
poetry run nox --session=tests --python=3.11
# or
poetry run nox -s tests -p 3.11
```

If you want to quickly test your unit tests, you can specify the the Python
version and the test file, for example:

```bash
poetry run nox --session=tests --python=3.11 tests/test_example.py
# or
poetry run nox -s tests -p 3.11 tests/test_example.py
```

A very crude method to test your unit test is to call the `pytest` command
directly which will run the tests using your cached Poetry virtual environment,
for example:

```bash
poetry run pytest tests/test_example.py
```

> **Note:** Using pytest directly won't provide fully accurate results and doesn't
> provide a coverage report.

## Code Coverage

If you want to run the tests and generate a coverage report, you can run the
following command:

```bash
poetry run nox --session=coverage
# or
poetry run nox -s coverage
```

If you want to check if your changes to the sphinx documentation will build
properly, you can run the following command:

```bash
poetry run nox --session=docs-build
# or
poetry run nox -s docs-build
```

You can actually view the documentation locally by running the following command:

```bash
poetry run nox --session=docs
# or
poetry run nox -s docs
```

This will build the documentation and then open it in your default web browser
for you to view, however if it doesn't you can view it `http://127.0.0.1:8000`.

## How to Submit Changes

> **Requirement:** Before pushing any changes, you must ensure that all sessions
> pass and you've run `poetry run nox -s pre-commit`, see
> [How to Test the Project].

Create a branch for your changes:

```bash
$ git switch --create my-changes main
```

Make a series of small, single-purpose commits, try to avoid using `git add .` or
`git add [-a|--all]`:

```bash
$ git add <path-to-file>
$ git commit -m "<short-for-your-change>"
```

Push your new branch with your changes to Github:

```bash
$ git push --set-upstream origin my-changes
```

Open a [pull request] to submit changes to this project.

You can also also use [Github CLI] to create a pull request:

```bash
$ gh pr create --base main --head my-changes
```

Your pull request needs to meet the following guidelines for acceptance:

- [ ] The Nox test suite must pass without errors and warnings.
- [ ] Include unit tests. **This project maintains 100% code coverage**.
- [ ] If your changes add functionality, update the documentation accordingly.

Feel free to submit early, though—we can always iterate on this.

> **Important:**<br>
> Before pushing any changes, you need to **run the pre-commit Nox session**
> and ensure [How to Test the Project] is followed,
> so that this will ensure your changes are properly linted and code
> formatting checks.

## Post-Merge Cleanup

After your pull request is merged, you can delete your branch:

```bash
$ git switch main
$ git branch --delete my-changes
```

If the branch was merged but not deleted automatically, you can delete it manually:

```bash
$ git push origin --delete my-changes
```

## Troubleshooting

### Poetry Issues

**Problem:** Sometimes you may have issues with Poetry and it's virtual environment where any
changes to the package or environment are not being reflected, this can sometimes
happen when changing major configs. I've found a complete nuke nuke of it's
cache and environments works:

```bash
rm -rf ~/.cache/pypoetry
poetry install
```

#### Incompatible Lock File

**Problem:** Poetry is complaining that the lock file is incompatible with the
current version of Poetry.

**Reason:** Perhaps you changed your Python version or Poetry version, but
you're getting an error that the lock file is incompatible with the current
version of Poetry.

**Error:**

```
  The lock file is not compatible with the current version of Poetry.
  Upgrade Poetry to be able to read the lock file or, alternatively, regenerate the lock file with the `poetry lock` command.
```

**Solution:**

```bash
$ rm poetry.lock
$ poetry lock
```

#### Forever Hung Resolving Dependencies

**Problem:** Poetry is hanging forever when resolving dependencies.

**Reason:** This can happen when your OS has a GUI, but you're not using it, so when Poetry
tries to access the keyring, prompting for credentials, it hangs forever.

**Error:**

```
Updating dependencies
Resolving dependencies... (76.4s)    <<< Counts up forever
```

**Debug:**

```
$ poetry <sub-cmd> -vvv
```

**Solution:**

```bash
export PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring
```

#### Invalid Group in Poetry Config

**Problem:** Poetry is complaining about an invalid group in the Poetry config.

**Reason:** This can happen when you're using a newer version of Poetry and
you're using an older version of the config file. Newer versions of Poetry
have changed the config file structure to use groups like `tool.poetry.group.<group>.<key>`,
but older versions of Poetry don't.

**Error:**

```
RuntimeError

The Poetry configuration is invalid:
   - Additional properties are not allowed ('group' was unexpected)
```

**Solution:**

```toml
[tool.poetry.group.dev.dependencies]
# <dependencies>
```

Move/change the key to:

```toml
[tool.poetry.dev-dependencies]
# <dependencies>
```

### Nox Issues

#### Nox Caching Problem

**Problem:** For some reason, Nox is not running the correct Python version or
the virtual environment is not changing or being used, even though you're
running the `nox` command through Poetry.

**Reason:** How this happens isn't entirely known, however it's a huge pain point
when changes aren't being reflected in the Nox sessions and clearing the cache
doesn't work.

**Solution:** You can try to run the following command to clear the entire Nox
cache:

```bash
$ rm -rf .nox/
$ poetry run nox
```

### No Changes are Working

When in doubt, just nuke all the cache files and directories and try again:

```bash
$ rm -rf ~/.cache/pypoetry/ .nox/ ~/.cache/pre-commit/ .mypy_cache/ .pytest_cache/ .coverage .coverage.*
```

<!-- github-only -->

[how to test the project]: ##how-to-test-the-project
[linting and code formatting]: ##linting-and-code-formatting
[pull request]: https://github.com/xransum/valkyrie-tools/pulls
[python idle]: https://docs.python.org/3/library/idle.html
[poetry]: https://python-poetry.org/
[pyenv]: https://github.com/pyenv/pyenv
[nox]: https://nox.thea.codes/
[github cli]: https://github.com/cli/cli
