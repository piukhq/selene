import os
import settings

from bigdatalib.schema import Schema
from cassandralib.client import Client

from app.csvfile import CSVReader
from app.utils import validate_uk_postcode

from app.visa import Visa
from app.amex import Amex
from app.source_format import SourceFormat


def export():
    files = fetch_files('csv')
    start_line = 2
    pcard = SourceFormat()
    reader = CSVReader(pcard.column_names, pcard.delimiter, pcard.column_keep)

    card_data = {"amex":[Amex(), [], []],
                 "visa": [Visa(), [], []],
                 }

    for txt_file in files:
        current_line = 0

        for row in reader(txt_file):
            current_line += 1

            if current_line >= start_line:
                for k, v in card_data.items():
                    if v[0].has_mid(row):
                        if validate_row_data(row):
                            v[1].append(row)
                        else:
                            v[2].append(row)

    for k, v in card_data.items():
        v[0].export_merchants(v[1], True)
        v[0].export_merchants(v[2], False)


def validate_row_data(row):
    """Validate data within a row from the csv file"""

    if row['Postcode'] != '':
        if not validate_uk_postcode(row['Postcode']):
            print("postcode fail", row['Postcode'])
            return False

    if row['Partner Name'] == '' or \
        row['Address (Building Name/Number, Street)'] == '' or \
        row['Town/City'] == '' or \
        row['Action'] == '':
        return False

    return True


def fetch_files(file_extension):
    file_path = settings.APP_DIR + '/provider_types'
    merchant_files = file_list(file_path, file_extension)
    return merchant_files


def file_list(file_path, file_ext):
    if not os.path.isdir(file_path):
        return []
    return [os.path.join(file_path, fn) for fn in next(os.walk(file_path))[2] if fn.endswith(file_ext)]


def sequential_file_number():
    db_client = Client(schema=Schema, hosts=settings.CASSANDRA_CLUSTER)
    # Get the currently logged files. This could be just the last file logged.
    # If returns nothing, then must be first file, so need to create the name.
    logged_files = db_client.select('file_logging', provider='amex', file_type='out')

    db_client.close()
    return len(logged_files.current_rows)


def insert_file_log(log):
    db_client = Client(schema=Schema, hosts=settings.CASSANDRA_CLUSTER)
    # Get the currently logged files. This could be just the last file logged.
    # If returns nothing, then must be first file, so need to create the name.
    db_client.insert('file_logging', [log])

    db_client.close()
