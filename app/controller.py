import os
import settings

from bigdatalib.schema import Schema
from cassandralib.client import Client

from app.csvfile import CSVReader
from app.utils import validate_uk_postcode
from app.utils import resolve_agent

from app.source_format import SourceFormat
from app.active import AGENTS


def get_agent(partner_slug):
    try:
        agent_class = resolve_agent(partner_slug)
        return agent_class()
    except KeyError:
        raise('No such agent')
    except Exception as ex:
        raise(ex)


def export():
    files = fetch_files('csv')
    start_line = 2
    pcard = SourceFormat()
    reader = CSVReader(pcard.column_names, pcard.delimiter, pcard.column_keep)

    card_data = {}
    for k, v in AGENTS.items():
        agent_instance = get_agent(k)
        valid_merchants = []
        invalid_merchants = []
        reasons = []
        card_data.update({k:[agent_instance, valid_merchants, invalid_merchants, reasons]})

    for txt_file in files:
        current_line = 0

        for row in reader(txt_file):
            current_line += 1

            if current_line >= start_line:
                has_mid = False
                for k, v in card_data.items():
                    if v[0].has_mid(row):
                        has_mid = True
                    validated, reasons = validate_row_data(row)
                    if validated and has_mid:
                        v[1].append(row)
                    else:
                        if not has_mid:
                            reasons += 'Missing MID. '
                        reasons += 'Line no. {} of file {}'.format(current_line, txt_file)
                        v[2].append(row)
                        v[3].append(reasons)

    for k, v in card_data.items():
        v[0].export_merchants(v[1], True)
        v[0].export_merchants(v[2], False, v[3])

        v[0].write_transaction_matched_csv(v[1])


def validate_row_data(row):
    """Validate data within a row from the csv file"""

    validated = True
    reasons = ''

    if row['Postcode'] != '':
        if not validate_uk_postcode(row['Postcode']):
            reasons = 'Invalid post code. '
            validated = False

    if row['Partner Name'] == '':
        reasons += 'Invalid Partner Name. '
        validated = False
    if row['Address (Building Name/Number, Street)'] == '':
        reasons += 'Invalid Address. '
        validated = False
    if row['Town/City'] == '':
        reasons += 'Invalid Town/City. '
        validated = False
    if row['Action'] == '':
        reasons += 'Invalid Action. '
        validated = False

    return validated, reasons


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
