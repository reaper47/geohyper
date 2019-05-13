import codecs
import csv
import ipaddress
import math
import sqlite3
import urllib.request
import database
from difflib import SequenceMatcher

rirs = ['https://ftp.arin.net/pub/stats/arin/delegated-arin-extended-latest',
        'https://ftp.ripe.net/ripe/stats/delegated-ripencc-extended-latest',
        'https://ftp.apnic.net/stats/apnic/delegated-apnic-extended-latest',
        'https://ftp.apnic.net/stats/afrinic/delegated-afrinic-extended-latest',
        'https://ftp.apnic.net/stats/lacnic/delegated-lacnic-extended-latest']


def size_to_cidr_mask(c):
    return int(-math.log2(c) + 32)


def parse_rir_files():
    for url in rirs:
        ftpstream= urllib.request.urlopen(url)
        lines = list(map(lambda x: x[0].split('|'), csv.reader(codecs.iterdecode(ftpstream, 'utf-8'))))
        for line in lines:
            try:
                rir, iso, ipv, ip, mask, *_ = line
            except ValueError:
                continue

            if ip == '*':
                continue

            if ipv == 'ipv4':
                length = int(mask)
                addr = ipaddress.ip_address(ip)
                yield {
                    'ip_low': addr,
                    'ip_high': addr + length - 1,
                    'rir': rir,
                    'country': iso,
                    'range': f'{ip}/{size_to_cidr_mask(length)}',
                }


def lookup(ip: str):
    try:
        ip_addr = ipaddress.ip_address(ip)
        if not ip_addr.is_global or ip_addr.is_multicast:
            return {}
    except ValueError:
        return {}

    entries = database.get_ip_entry(ip)
    if not entries:
        return {}

    scores = [SequenceMatcher(None, ip, x['ip_low']).ratio() for x in entries]
    max_index = max(enumerate(scores), key=lambda x: x[1])[0]
    return entries[max_index]
