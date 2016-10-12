import os
import settings
try:
    from os import scandir
except ImportError:
    from scandir import scandir

from bigdatalib.schema import Schema
from cassandralib.client import Client
import yagmail
import pysftp
import shutil

from app.csvfile import CSVReader
from app.utils import validate_uk_postcode
from app.utils import resolve_agent

from app.source_format import SourceFormat
from app.active import AGENTS


def upload_sftp(url, username, password, src_dir, dst_dir):
    """Upload all the files in the source directory to the sftp location url in the destination directory
    with appropriate user credentials"""
    with pysftp.Connection(url, username=username, password=password) as sftp:
        files = os.listdir(src_dir)
        for filename in files:
            path = os.path.join(src_dir, filename)
            if os.path.isfile(path):
                src_path = path
                dst_path = os.path.join(dst_dir, filename)
                sftp.put(src_path, dst_path, preserve_mtime=True)


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
        card_data.update({k:[agent_instance, valid_merchants, invalid_merchants]})

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

        v[0].write_transaction_matched_csv(v[1])


def validate_row_data(row):
    """Validate data within a row from the csv file"""

    if row['Postcode'] != '':
        if not validate_uk_postcode(row['Postcode']):
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


def get_partner_name():
    """Retrieve the partner name from the input csv file"""
    csv_files = fetch_files('csv')
    start_line = 2
    pcard = SourceFormat()
    reader = CSVReader(pcard.column_names, pcard.delimiter, pcard.column_keep)

    pname = []
    partner_name = ''
    first = True
    plural = False
    for txt_file in csv_files:
        current_line = 0
        if first:
            first = False
        for row in reader(txt_file):
            current_line += 1
            if current_line >= start_line:
                pname.append(row['Partner Name'])

    partner_name = ', '.join(set(pname))

    return partner_name

def get_attachments(src_dir):
    """Send an email with generated MID data to each agent that requires it"""
    files = os.listdir(src_dir)

    attachments = []
    for f in files:
        file_path = os.path.join(src_dir, f)
        if not os.path.isdir(file_path):
            if not 'INVALID' in f and 'cass' not in f:
                attachments.append(file_path)

    return attachments


def archive_files(src_dir):
    """Archive generated files"""
    dst_dir = src_dir + '/archive'
    os.makedirs(dst_dir, exist_ok=True)
    copy_local(src_dir, dst_dir)


def copy_local(src_dir, dst_dir):
    """Copy files locally from one directory to another"""
    for entry in scandir(src_dir):
        if entry.is_file(follow_symlinks=False):
            shutil.move(entry.path, dst_dir)


def send_email(agent, partner_name, contents, attachments=None):
    """Send an email with MIDs"""
    yag = yagmail.SMTP(user=settings.EMAIL_SOURCE_CONFIG[0], password=settings.EMAIL_SOURCE_CONFIG[1],
                       host=settings.EMAIL_SOURCE_CONFIG[2], port=settings.EMAIL_SOURCE_CONFIG[3])

    yag.send(settings.EMAIL_TARGETS[agent], 'MID files for on-boarding with ' + partner_name, contents, attachments)


if __name__ == '__main__':
    export()

    # Amex only requires SFTP
    #url, username, password, dst_dir = settings.TRANSACTION_MATCHING_FILES_CONFIG[2:]
    #src_dir = os.path.join(settings.APP_DIR, 'merchants/amex')
    #upload_sftp(url, username, password, src_dir, dst_dir)

    partner_name = get_partner_name()
    contents = ['Please load the attached MIDs for ' + partner_name + ' and confirm your forecast on-boarding date.']

    # VISA
    src_dir = os.path.join(settings.APP_DIR, 'merchants/visa')
    attachments = get_attachments(src_dir)
    send_email('visa', partner_name, contents, attachments)
    archive_files(src_dir)

    # MASTERCARD (requires no attachments)
    send_email('mastercard', partner_name, contents)
