import os
import settings
import csv

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


def export_mastercard():
    files = fetch_files('psv')
    agent_instance = get_agent('mastercard')
    merchants = []
    footer_id = 30

    for txt_file in files:
        with open(txt_file, newline='') as csvfile:
            mcardreader = csv.reader(csvfile, delimiter='|')

            for count, row in enumerate(mcardreader):
                if count == 0:
                    continue
                elif footer_id == int(row[0]):
                    # EOF
                    break
                else:
                    merchant = {}
                    merchant['MasterCard MIDs'] = row[5]
                    merchant['Partner Name'] = row[7]
                    merchant['Town/City'] = row[13]
                    merchant['Scheme'] = row[39]

                    merchants.append(merchant)

        if len(merchants):
            agent_instance.write_transaction_matched_csv(merchants)


def export():
    files = fetch_files('csv')
    start_line = 2
    pcard = SourceFormat()
    reader = CSVReader(pcard.column_names, pcard.delimiter, pcard.column_keep)

    card_data = {}
    for k, v in AGENTS.items():
        if k != 'mastercard':
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
                for k, v in card_data.items():
                    has_mid = False
                    if k != 'mastercard':
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
        if k != 'mastercard':
            v[0].export_merchants(v[1], True)
            v[0].export_merchants(v[2], False, v[3])

            if len(v[1]):
                v[0].write_transaction_matched_csv(v[1])


def validate_row_data(row):
    """Validate data within a row from the csv file"""

    validated = True
    reasons = ''

    if not validate_uk_postcode(row['Postcode'].strip('"')):
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


def get_partner_name():
    """Retrieve the partner name from the input csv file"""
    csv_files = fetch_files('csv')
    start_line = 2
    pcard = SourceFormat()
    reader = CSVReader(pcard.column_names, pcard.delimiter, pcard.column_keep)

    pname = []
    for txt_file in csv_files:
        current_line = 0
        for row in reader(txt_file):
            current_line += 1
            if current_line >= start_line:
                pname.append(row['Partner Name'])

    partner_name = ', '.join(set(pname))

    return partner_name

def get_attachments(src_dir):
    """Send an email with generated MID data to each agent that requires it"""
    attachments = []
    for entry in scandir(src_dir):
        if entry.is_file(follow_symlinks=False):
            file_path = entry.path
            if not 'INVALID' in file_path and not 'cass' in file_path:
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
                       host=settings.EMAIL_SOURCE_CONFIG[2], port=settings.EMAIL_SOURCE_CONFIG[3],
                       smtp_starttls=False, smtp_skip_login=True)

    yag.send(settings.EMAIL_TARGETS[agent], agent.title() + ' MID files for on-boarding with ' + partner_name, contents, attachments)


def onboard_mids():
    export()

    # Amex only requires SFTP
    url, username, password, dst_dir = settings.TRANSACTION_MATCHING_FILES_CONFIG[2:]
    src_dir = os.path.join(settings.APP_DIR, 'merchants/amex')
    upload_sftp(url, username, password, src_dir, dst_dir)

    partner_name = get_partner_name()
    contents = ['Please load the attached MIDs for ' + partner_name + ' and confirm your forecast on-boarding date.']

    # VISA
    src_dir = os.path.join(settings.APP_DIR, 'merchants/visa')
    attachments = get_attachments(src_dir)
    send_email('visa', partner_name, contents, attachments)
    archive_files(src_dir)

    # MASTERCARD (requires no attachments)
    send_email('mastercard', partner_name, contents)

def process_mastercard_handback_file():
    export_mastercard()


if __name__ == '__main__':
    decision = input('Selene asks that you choose your fate from our funky laser display board:\n'
                     '1) Onboard MIDs\n'
                     '2) Process Mastercard handback file\n')
    if decision == '1':
        onboard_mids()
    elif decision == '2':
        process_mastercard_handback_file()
    else:
        print("Invalid choice, you must select 1 or 2.  Exiting program.")