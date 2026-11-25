"""Run from repository root: python tests/validate.py (Python 3.9+)."""
import sqlite3
from pathlib import Path
import csv
import sys

SQL = Path(__file__).resolve().parents[1] / 'sql' / 'top_customers_by_market.sql'

def validate():
    with sqlite3.connect(':memory:') as db:
        db.executescript('''
        PRAGMA foreign_keys = ON;
        CREATE TABLE country(country_id INTEGER PRIMARY KEY, country TEXT);
        CREATE TABLE city(city_id INTEGER PRIMARY KEY, city TEXT, country_id INTEGER REFERENCES country);
        CREATE TABLE address(address_id INTEGER PRIMARY KEY, city_id INTEGER REFERENCES city);
        CREATE TABLE customer(customer_id INTEGER PRIMARY KEY, first_name TEXT, last_name TEXT, address_id INTEGER REFERENCES address);
        CREATE TABLE payment(payment_id INTEGER PRIMARY KEY, customer_id INTEGER REFERENCES customer, amount NUMERIC);
        ''')
        db.executemany('INSERT INTO country VALUES (?,?)', [(i, f'Country {i}') for i in range(1,12)])
        db.executemany('INSERT INTO city VALUES (?,?,?)', [(i, 'Shared' if i in (1,11) else f'City {i}', i) for i in range(1,12)])
        db.executemany('INSERT INTO address VALUES (?,?)', [(i,i) for i in range(1,12)])
        db.executemany('INSERT INTO customer VALUES (?,?,?,?)', [(i,f'Customer {i}','Test',i) for i in range(1,12)])
        db.executemany('INSERT INTO payment VALUES (?,?,?)', [(i,i,v) for i,v in enumerate([60,90,80,70,60,50,40,30,20,10,999],1)] + [(12,1,40)])
        rows = db.execute(SQL.read_text(encoding='utf-8')).fetchall()
        assert [r[0] for r in rows] == [1,2,3,4,5], rows
        assert [r[5] for r in rows] == [100,90,80,70,60], rows
        assert all(r[6] == 80 for r in rows), rows
        db.execute('DELETE FROM payment')
        assert db.execute(SQL.read_text(encoding='utf-8')).fetchall() == []
    return rows

if __name__ == '__main__':
    rows = validate()
    print('PASS: geographic exclusion, deterministic ties, payment aggregation, group average, empty payments', file=sys.stderr)
    writer = csv.writer(sys.stdout, lineterminator='\n')
    writer.writerow(['customer_id','first_name','last_name','city','country','total_payment','average_top_customer_payment'])
    writer.writerows(rows)
