# Usage

All of the command line tools are available directly after installation and should be callable from thw command-lone interface.

All commands were built with the intention of being used in a CI/CD pipeline.
As such, they all have a `--help` flag that will print out the available
options.

## Valkyrie

This script is used to manage user configs used for scripts in this toolset.

Arguments:

```bash
$ valkyrie <sub-command>
```

### Config

Arguments:

```bash
$ valkyrie config <sub-command>
```

### Config Set

For setting the value for a given key.

Arguments:

```bash
$ valkyrie config set <key> <value>
```

### Config Get

For getting the value for a given key.

Arguments:

```bash
$ valkyrie config get <key>
```

### Config Remove

For removing a specific config value.

Arguments:

```bash
$ valkyrie config remove <key>
```

### Config List

For listing all config keys set in the users config.

Arguments:

```bash
$ valkyrie config list <opt: key>
```

### Config Clear

For clearing all values set in the users config.

Arguments:

```bash
$ valkyrie config clear
```

## URLCheck

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

## IPCheck

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

## Whobe

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

## DNSCheck

This script will get DNS records for a given domain or IP address.

Arguments:

```bash
$ dnscheck <domain/ip>
```

Example Usage:

```
$ dnscheck google.com
  A   : 142.250.31.138
  A   : 142.250.31.139
  A   : 142.250.31.113
  A   : 142.250.31.101
  A   : 142.250.31.102
  A   : 142.250.31.100
  AAAA: 2607:f8b0:4004:c07::8a
  AAAA: 2607:f8b0:4004:c07::71
  AAAA: 2607:f8b0:4004:c07::65
  AAAA: 2607:f8b0:4004:c07::66
  MX  : smtp.google.com.
```
