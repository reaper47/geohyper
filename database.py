import sqlite3
import os
import geoip

DB_NAME = 'geoip.db'
TABLE = 'geoips'


def create_database():
    if not os.path.exists(DB_NAME):
        conn = sqlite3.connect(DB_NAME)
        conn.execute(f'CREATE TABLE {TABLE} (ip_low, ip_high, range, country, rir)')
        conn.close()
        print('GeoIP database created')
    else:
        print('GeoIP database already created')


def build_database():
    print('Fetching all entries...')
    data = list(geoip.parse_rir_files())

    print('Sorting entries...')
    data.sort(key=lambda x: x['ip_low'])

    print('Do you want to wipe the database? (y/n)')
    wipe = input()
    if 'y' in wipe:
        print('Wiping database...')
        wipe_database()

    print('Building database...')
    for entry in data:
        add_entry(ip_low=str(entry['ip_low']), ip_high=str(entry['ip_high']),
                  range_=entry['range'], country=entry['country'], rir=entry['rir'])
    print('Done.')


def wipe_database():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(f'DELETE FROM {table}')
        conn.commit()


def add_entry(ip_low: str, ip_high: str, range_: str, country: str, rir: str):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(f'INSERT INTO {TABLE} (ip_low, ip_high, range, country, rir) '
                       'VALUES (?,?,?,?,?)', (ip_low, ip_high, range_, country, rir))
        conn.commit()


def get_ip_entry(ip: str):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(f'SELECT ip_low, ip_high, range, country, rir FROM {TABLE} '
                        'WHERE ? >= ip_low AND ? <= ip_high', (ip,ip,))
        rows = cursor.fetchall()
        return [{'ip': ip, 'ip_low': low, 'ip_high': high, 'range': range_, 'country': iso, 'rir': rir}
                for (low, high, range_, iso, rir) in rows]


if __name__ == '__main__':
    create_database()
    build_database()
