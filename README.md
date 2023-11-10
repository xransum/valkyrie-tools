# Valkyrie Tools

<p align="center">
    <img src="https://raw.githubusercontent.com/xransum/valkyrie-tools/main/docs/images/logo.png" width="20%" style="border-radius: 10%">
</p>

[![Tests](https://github.com/xransum/valkyrie-tools/workflows/Tests/badge.svg)][tests]
[![Codecov](https://codecov.io/gh/xransum/valkyrie-tools/branch/main/graph/badge.svg)][codecov]

[![PyPI](https://img.shields.io/pypi/v/valkyrie-tools.svg)][pypi_]
[![Python Version](https://img.shields.io/pypi/pyversions/valkyrie-tools)][python version]

[![Python Black](https://img.shields.io/badge/code%20style-black-000000.svg?label=Style)](https://github.com/xransum/valkyrie-tools)
[![Read the documentation at https://valkyrie-tools.readthedocs.io/](https://img.shields.io/readthedocs/valkyrie-tools/latest.svg?label=Read%20the%20Docs)][read the docs]

[![Downloads](https://pepy.tech/badge/valkyrie-tools)](https://pepy.tech/project/valkyrie-tools)
[![License](https://img.shields.io/pypi/l/valkyrie-tools)][license]

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

- `valkyrie`: The main entrypoint for configuring the tools.
- `urlcheck`: Check the aliveness of a URL.
- `ipcheck`: Get information for an IP address. (_WIP_)
- `dnscheck`: Get dns records for a domain/IP address. (_WIP_)
- `whobe`: Get information for a domain/IP address. (_WIP_)

### CLI

You can call valkyrie-tools from the command line like so:

```bash
$ valkyrie
```

#### Passing Input

All supported methods of passing input to the script are:

**Text as argument:**

```bash
$ myscript "abc"
```

**Text from file:**

```bash
$ myscript test.txt
```

**Interactive mode:**

```bash
$ myscript -I
$ myscript --interactive
```

**Piped stdin input:**

```bash
$ echo "abc" | myscript
```

**Piped stdin input (alt):**

```bash
$ myscript <<<"abc"
```

**Input file:**

```bash
$ myscript <myfile.txt
```

**Process substitution by file descriptor:**

```bash
$ myscript <(cat myfile.txt)
```

### Import

You can import valkyrie-tools into your project and use it like so:

```python
import valkyrie_tools
```

### Scripts

#### urlcheck

Arguments:

```bash
$ urlcheck <url>
```

Example Usage:

```bash
$ urlcheck "https://google.com"
-> https://google.com
   HTTP/1.1 - 301 - Moved Permanently
>> https://www.google.com/
   HTTP/1.1 - 200 - OK
```

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

<!-- github-only -->

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
[license]: https://github.com/xransum/valkyrie-tools/blob/main/LICENSE
[contributor guide]: https://github.com/xransum/valkyrie-tools/blob/main/CONTRIBUTING.md
