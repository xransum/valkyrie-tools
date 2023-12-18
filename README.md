<div align="center">

# Valkyrie Tools

A collection of tools and scripts for making the life of security analysts
easier, faster, and more efficient.

  <img src="https://raw.githubusercontent.com/xransum/valkyrie-tools/main/docs/images/logo.png" width="20%" style="border-radius: 10%">

  <br />

[![Tests](https://github.com/xransum/valkyrie-tools/workflows/Tests/badge.svg)][tests]
[![Codecov](https://codecov.io/gh/xransum/valkyrie-tools/branch/main/graph/badge.svg)][codecov]
[![PyPI](https://img.shields.io/pypi/v/valkyrie-tools.svg)][pypi_]
[![Python Version](https://img.shields.io/pypi/pyversions/valkyrie-tools)][python version]

[![Python Black](https://img.shields.io/badge/code%20style-black-000000.svg?label=Style)](https://github.com/xransum/valkyrie-tools)
[![Read the documentation at https://valkyrie-tools.readthedocs.io/](https://img.shields.io/readthedocs/valkyrie-tools/latest.svg?label=Read%20the%20Docs)][read the docs]
[![Downloads](https://pepy.tech/badge/valkyrie-tools)](https://pepy.tech/project/valkyrie-tools)
[![License](https://img.shields.io/pypi/l/valkyrie-tools)][license]

</div>

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

### Command Line Scripts

A list of all available command line scripts:

- **[valkyrie](#valkyrie)**
- **[urlcheck](#urlcheck)**
- **[ipcheck](#ipcheck)**
- **[whobe](#whobe)**

Once you've installed the package, you can run any of the scripts like so:

```bash
$ <script-name> <args>
```

#### Valkyrie

This script has not yet been implemented.

#### URLCheck

This script will check the aliveness of a URL and follow any redirects.

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

#### IPCheck

This script will get information for an IP address.

Arguments:

```bash
$ ipcheck <ip>
```

Example Usage:

```bash
$ ipcheck 1.1.1.1
> 1.1.1.1
  ip       : 1.1.1.1
  hostname : one.one.one.one
  anycast  : True
  city     : Los Angeles
  region   : California
  country  : US
  loc      : 34.0522,-118.2437
  org      : AS13335 Cloudflare, Inc.
  postal   : 90076
  timezone : America/Los_Angeles
  readme   : https://ipinfo.io/missingauth
```

#### WhoBe

This script will get information for a domain or IP address.

Arguments:

```bash
$ whobe <domain/ip>
```

Example Usage:

```bash
$ whobe google.com
> google.com
   Registrar: MarkMonitor Inc. (None)
   Emails:
      - abusecomplaints@markmonitor.com
   Name: None
   Address: None, None, None None, None
   Creation Date: 1997-09-15 04:00:00
   Expiration Date: 2028-09-14 04:00:00
   Updated Date: 2019-09-09 15:39:04
   Name Servers:
      - NS1.GOOGLE.COM
      - NS2.GOOGLE.COM
      - NS3.GOOGLE.COM
      - NS4.GOOGLE.COM
$
$ whobe 1.1.1.1
> 1.1.1.1
   ASN: 13335 (AU)
   CIDR: 1.1.1.0/24
   Description: 1.1.1.0/24
   Networks:
      - APNIC-LABS (AA1412-AP)
        CIDR: 1.1.1.0/24
        Netrange: (1.1.1.0 - 1.1.1.255) - 24 Hosts
        Address: PO Box 3646 South Brisbane, QLD 4101 Australia, AU
        Emails:
          - resolver-abuse@cloudflare.com
          - helpdesk@apnic.net
          - research@apnic.net
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
