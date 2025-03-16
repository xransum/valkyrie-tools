Valkyrie Tools
==============

.. toctree::
   :hidden:
   :maxdepth: 1

   reference
   contributing
   code_of_conduct
   license

This is an open-source project that being a collection of tools and scripts
for making the life of security analysts easier, faster, and more efficient.

The tools are built to be easily usable from the command line and also easily
integratable into your codebase. The documentation is still a work-in-progress
but the tools are fully functional and ready to be used.


Installation
------------

To install the Valkyrie tools, you simply need to run the following command:

.. code-block:: console

   $ pip install valkyrie-tools


Usage
-----

Valkyrie
^^^^^^^^

.. code-block:: console

    valkyrie [OPTIONS] COMMAND [ARGS]...


Global Options
""""""""""""""

- ``--version``  Show the version information and exit.
- ``--help``     Show the help message and exit.

Sub-commands
""""""""""""

``config``

Manage configuration values.

.. code-block:: console

    valkyrie config [COMMAND] [ARGS]...

Sub-commands:

- ``delete``  - Delete a configuration value.
- ``get``     - Get a configuration value.
- ``list``    - List configuration values.
- ``set``     - Set a configuration value.


URL Check
^^^^^^^^^

Check url(s) for their aliveness and status.

.. code-block:: console

    urlcheck [OPTIONS] [URL]...


Global Options
""""""""""""""

- ``-I``, ``--interactive``   Interactive mode.
- ``-t``, ``--no-truncate``   Disable header truncation.
- ``-S``, ``--show-headers``  Disable header truncation.
- ``-h``, ``--help``          Show this message and exit.

Examples
""""""""

.. code-block:: console

    urlcheck "https://example.com"
    -> https://example.com
    HTTP/1.1 - 200 - OK

.. code-block:: console

    urlcheck "https://example.com" "https://example.org"
    -> https://example.com
    HTTP/1.1 - 200 - OK

    -> https://example.org
    HTTP/1.1 - 200 - OK


IP Check
^^^^^^^^

Get ip address info.

.. code-block:: console

    ipcheck [OPTIONS] [IP_ADDR]...


Global Options
""""""""""""""

- ``-I``, ``--interactive``   Interactive mode.
- ``-h``, ``--help``          Show this message and exit.


Examples
""""""""

.. code-block:: console

    ipcheck 8.8.8.8
    > 8.8.8.8
    ip       : 8.8.8.8
    hostname : dns.google
    city     : Mountain View
    region   : California
    country  : US
    loc      : 38.0088,-122.1175
    org      : AS15169 Google LLC
    postal   : 94043
    timezone : America/Los_Angeles
    readme   : https://ipinfo.io/missingauth
    anycast  : True


DNS Check
^^^^^^^^^

Check DNS records for domains and IP addresses.

.. code-block:: console

    dnscheck [OPTIONS] [IP_ADDR]...


Global Options
""""""""""""""

- ``-I``, ``--interactive``   Interactive mode.
- ``-t``, ``--rtypes``        DNS record type to query.
- ``-h``, ``--help``          Show this message and exit.


Examples
""""""""

.. code-block:: console

    dnscheck google.com
    > google.com
    A   : 142.251.32.110
    AAAA: 2404:6800:4003:c00::8a
    AAAA: 2404:6800:4003:c00::71
    AAAA: 2404:6800:4003:c00::64
    AAAA: 2404:6800:4003:c00::8b
    MX  : smtp.google.com.


Whobe
^^^^^

Check whois on domains and ip addresses.

.. code-block:: console

    whobe [OPTIONS] [IP_ADDR]...


Global Options
""""""""""""""

- ``-I``, ``--interactive``   Interactive mode.
- ``-h``, ``--help``          Show this message and exit.


Examples
""""""""

.. code-block:: console

    whobe google.com
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
