# Valkyrie Tools

[![PyPI](https://img.shields.io/pypi/v/valkyrie-tools.svg)][pypi_]
[![Python Version](https://img.shields.io/pypi/pyversions/valkyrie-tools)][python version]
[![License](https://img.shields.io/pypi/l/valkyrie-tools)][license]
[![Read the documentation at https://valkyrie-tools.readthedocs.io/](https://img.shields.io/readthedocs/valkyrie-tools/latest.svg?label=Read%20the%20Docs)][read the docs]
[![Tests](https://github.com/xransum/valkyrie-tools/workflows/Tests/badge.svg)][tests]
[![Codecov](https://codecov.io/gh/xransum/valkyrie-tools/branch/main/graph/badge.svg)][codecov]

[pypi_]: https://pypi.org/project/valkyrie-tools/
[python version]: https://pypi.org/project/valkyrie-tools
[read the docs]: https://valkyrie-tools.readthedocs.io/
[tests]: https://github.com/xransum/valkyrie-tools/actions?workflow=Tests
[codecov]: https://app.codecov.io/gh/xransum/valkyrie-tools

## Installation

Install `valkyrie-tools` from the Python Package Index:

```bash
$ pip install valkyrie-tools
```

or

```bash
$ python3 -m pip install valkyrie-tools
```

## Requirements

- Python 3.8+

## Usage

All of the command line tools are available under directly and should be
available in your path after installation.

```bash
$ valkyrie
```

All commands were built with the intention of being used in a CI/CD pipeline.
As such, they all have a `--help` flag that will print out the available
options.

```bash
$ valkyrie --help
```

### Commands

- `valkyrie` - The main entrypoint for configuring the tools.

### CLI

You can call valkyrie-tools from the command line like so:

```bash
$ valkyrie
```

### Import

You can import valkyrie-tools into your project and use it like so:

```python
import valkyrie_tools
```

Each module within valkyrie-tools is documented with a docstring.

## Contributing

Contributions are very welcome.
To learn more, see the [Contributor Guide].

## License

Distributed under the terms of the [MIT license][license],
_valkyrie-tools_ is free and open source software.

## Issues

If you encounter any problems,
please [file an issue] along with a detailed description.

## Credits

This project was built off of the sweat and tears
of the the bad actors it was built to fight.

[@xransum]: https://github.com/xransum
[nox]: https://nox.thea.codes/
[poetry]: https://python-poetry.org/
[constraints file]: https://pip.pypa.io/en/stable/user_guide/#constraints-files
[file an issue]: https://github.com/xransum/valkyrie-tools/issues
[keyword-only parameter]: https://docs.python.org/3/glossary.html#keyword-only-parameter
[nox.sessions.session.install]: https://nox.thea.codes/en/stable/config.html#nox.sessions.Session.install
[nox.sessions.session.run]: https://nox.thea.codes/en/stable/config.html#nox.sessions.Session.run
[pip install]: https://pip.pypa.io/en/stable/reference/pip_install/
[pip]: https://pip.pypa.io/
[pipx]: https://pipxproject.github.io/pipx/

<!-- github-only -->

[license]: https://github.com/xransum/valkyrie-tools/blob/main/LICENSE
[contributor guide]: https://github.com/xransum/valkyrie-tools/blob/main/CONTRIBUTING.md
