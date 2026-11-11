#!/usr/bin/env python3
"""Resolve the official Ubuntu hosts when a CI runner's normal DNS is broken."""
import argparse
import ipaddress
import json
import subprocess
import urllib.request

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--dry-run', action='store_true')
parser.add_argument('--force', action='store_true', help='Exercise HTTPS DNS even if normal DNS works')
args = parser.parse_args()

for host in ('archive.ubuntu.com', 'security.ubuntu.com'):
    if not args.force:
        try:
            result = subprocess.run(['getent', 'ahostsv4', host], capture_output=True, timeout=5)
            if result.returncode == 0 and result.stdout:
                print(f'Normal DNS is available for {host}')
                continue
        except subprocess.TimeoutExpired:
            pass
    # No credentials or build secrets are sent. TLS verifies dns.google;
    # apt still verifies Ubuntu signatures and the original HTTPS hostname.
    request = urllib.request.Request(f'https://dns.google/resolve?name={host}&type=A')
    with urllib.request.urlopen(request, timeout=15) as response:
        data = json.load(response)
    if data.get('Status') != 0:
        raise SystemExit(f'HTTPS DNS could not resolve {host}')
    addresses = sorted({str(ipaddress.IPv4Address(item['data']))
                        for item in data.get('Answer', [])
                        if item.get('type') == 1 and item.get('name', '').rstrip('.').lower() == host})
    if not addresses:
        raise SystemExit(f'HTTPS DNS returned no IPv4 address for {host}')
    lines = ''.join(f'{address} {host}\n' for address in addresses)
    if args.dry_run:
        print(lines, end='')
    else:
        with open('/etc/hosts', 'a', encoding='ascii') as hosts:
            hosts.write('\n# Temporary official Ubuntu DNS fallback for this CI runner\n' + lines)
    print(f'HTTPS DNS fallback verified for {host}: {len(addresses)} IPv4 addresses')
