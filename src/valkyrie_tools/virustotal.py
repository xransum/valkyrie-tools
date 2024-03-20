"""Command-line script for interfacing with VirusTotal."""
import sys
from typing import Tuple
import click
import vt
import re
from datetime import datetime, timedelta

from valkyrie_tools import configs
from valkyrie_tools.commons import common_options, parse_input_methods
from valkyrie_tools.constants import HELP_SHORT_TEXT, NO_ARGS_TEXT



def is_md5_hash(value: str) -> bool:
    """Check if the text is an MD5 hash."""
    return re.search(r"^[a-fA-F\d]{32}$", value) is not None


def is_sha1_hash(value: str) -> bool:
    """Check if the text is a SHA1 hash."""
    return re.search(r"^[a-fA-F\d]{40}$", value) is not None


def is_sha256_hash(value: str) -> bool:
    """Check if the text is a SHA256 hash."""
    return re.search(r"^[a-fA-F\d]{64}$", value) is not None


def is_sha512_hash(value: str) -> bool:
    """Check if the text is a SHA512 hash."""
    return re.search(r"^[a-fA-F\d]{128}$", value) is not None


"""
vt scan url <url>
vt scan file <file-path>
vt search "positives:5+ type:pdf"
vt url <url>

vt url <url>
vt file <file-path>
vt file scan <file-path> --password=malware123

#########

vt analysis <id>    # Get analysis report for URL or file.
vt domain <domain>  # Get information on a domain.
vt download   # Download file(s)
vt hunting   # Modify malware hunting rules and notifications.
vt file   # Get info about files.
vt ip        # Get info on an IP address.
vt retrohunt  # Manage retro hunt jobs.
vt scan     # Scan URL(s) or a file(s).
vt search   # Search VirusTotal.
"""

"""
from valkyrie_tools.
"""

API_KEY = configs.get("GLOBAL", "virustotalApiKey")
client = vt.Client(API_KEY)
#values = parse_input_methods(values, interactive, ctx)

#url = "https://apexcorporategroup.com/"
#scan = client.scan_url(url, wait_for_completion=True)

#analysis = client.get_object(f"/urls/{scan.id.split('-')[1]}")



@click.group(help='Interact with VirusTotal API.', context_settings={'help_option_names': ['-h', '--help']})
@click.version_option(version='0.1.0', prog_name='virustotal')
def cli():
    pass

# vt scan <opt>
@cli.group(name="scan", help="Perform scans on URLs or files.")
def vtscan():
    pass

# vt scan url <opt>
@vtscan.command(name="url", help="Scan one or more URLs.")
@click.option("--full", is_flag=True, help="Show full analysis report.")
@click.argument('urls', nargs=-1)
def vtscan_url(full, urls):
    """
    Output A: vt scan url <url> --full
        > <url>
        Analysis URL: https://www.virustotal.com/gui/url/analysis/<id>
        URL has been flagged 3 times as malicious.
        Categories: Malicious, Malware, Phishing
        Sources:
            Avira: Malware
            CRDF: Malicious
            Criminal IP: Phishing
        History: Scanned 3 times in the past 30 days.
            Scanned 1 hour ago: Malicious (Current)
            Scanned 3 days ago: Clean
            Scanned 10 days ago: Malicious
            Scanned 30 days ago: Malicious

    Output B: vt scan url <url>
        VT: https://www.virustotal.com/gui/url/analysis/<id> - 3 hits (Malicious, Malware, Phishing)
    """
    results = []
    for url in urls:
        # Implement scanning URL functionality using VirusTotal API for each URL
        scan = client.scan_url(url, wait_for_completion=True)
        results.append((url, scan))

    if full:
        for url, scan in results:
            analysis = client.get_object(f"/urls/{scan.id.split('-')[1]}")
            print(url)
            print(f"Analysis URL: {analysis.permalink}")
            print(f"URL has been flagged {analysis.positives} times as malicious.")
            print(f"Categories: {', '.join(analysis.categories)}")
            print("Sources:")
            for source, category in analysis.sources.items():
                print(f"    {source}: {category}")
            print("History: Scanned 3 times in the past 30 days.")
            for scan_date, result in analysis.last_analysis_results.items():
                print(f"    Scanned {scan_date}: {result['result']} (Current)" if result['result'] == "malicious" else f"    Scanned {scan_date}: {result['result']}")
    else:
        for url, scan in results:
            analysis = client.get_object(f"/urls/{scan.id.split('-')[1]}")
            print(f"VT: {analysis.permalink} - {analysis.positives} hits ({', '.join(analysis.categories)})")

# vt scan file <opt>
@vtscan.command(name="file", help="Scan one or more files.")
@click.argument('file_paths', nargs=-1)
def vtscan_file(file_paths):
    for file_path in file_paths:
        # Implement scanning file functionality using VirusTotal API for each file
        if os.path.isfile(file_path):
            pass
        else:
            raise OSError("Invalid file path.")


# vt url <opt>
@cli.group(name="url", help="Interact with URLs.")
def vturl():
    pass

# vt search <opt>
@cli.command(name="search", help="Perform a search query.")
@click.argument('query')
def vtsearch(query):
    # Implement search functionality using VirusTotal API
    pass

client.close()