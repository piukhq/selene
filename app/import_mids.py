import re
import os
import settings
import arrow
import pysftp
import shutil

try:
    from os import scandir
except ImportError:
    from scandir import scandir

from app.utils import validate_uk_postcode, get_agent, format_json_input, update_amex_sequence_number
from app.email import send_email
from app.active import AGENTS


def upload_sftp(url, username, password, src_dir, dst_dir):
    """
    Upload all the files in the source directory to the sftp location url in the destination directory
    with appropriate user credentials
    """
    with pysftp.Connection(url, username=username, password=password) as sftp:
        files = os.listdir(src_dir)
        for filename in files:
            path = os.path.join(src_dir, filename)
            if os.path.isfile(path):
                src_path = path
                dst_path = os.path.join(dst_dir, filename)
                sftp.put(src_path, dst_path, preserve_mtime=True)


def initialize_card_data():
    card_data = {}
    for k, v in AGENTS.items():
        agent_instance = get_agent(k)
        valid_merchants = []
        invalid_merchants = []
        transaction_matched_merchants = []
        reasons = []
        card_data.update({k: [agent_instance, valid_merchants, invalid_merchants, transaction_matched_merchants,
                              reasons]})

    return card_data


def populate_card_data(file, ignore_postcode):
    card_data = initialize_card_data()

    for row in file:
        for k, v in card_data.items():
            has_mid = False
            if v[0].has_mid(row):
                has_mid = True
            validated, reasons, bad_post_code = validate_row_data(row)
            if validated and has_mid:
                if ignore_postcode:
                    bad_post_code = False
                if not bad_post_code:
                    v[1].append(row)
                else:
                    reasons += ''
                    v[2].append(row)
                    v[4].append(reasons)
                v[3].append(row)
            else:
                if not has_mid:
                    reasons += 'Missing MID. '
                reasons += ''
                v[2].append(row)
                v[4].append(reasons)
    return card_data


def export(file, ignore_postcode):
    card_data = populate_card_data(file, ignore_postcode)

    for k, v in card_data.items():
        v[0].export_merchants(v[1], True)
        v[0].export_merchants(v[2], False, v[4])

        if len(v[1]):
            v[0].write_transaction_matched_csv(v[3])


def validate_row_data(row):
    """Validate data within a row from the csv file"""

    validated = True
    bad_post_code = False
    reasons = ''

    if not validate_uk_postcode(row['Postcode'].strip('"')):
        reasons = "Invalid post code: '{}' ".format(row['Postcode'].strip('"'))
        bad_post_code = True

    if row['Partner Name'] == '':
        reasons += 'Invalid Partner Name. '
        validated = False
    if row['Town/City'] == '':
        reasons += 'Invalid Town/City. '
        validated = False
    if row['Action'] == '':
        reasons += 'Invalid Action. '
        validated = False

    return validated, reasons, bad_post_code


def get_partner_name(file):
    """Retrieve the partner name from the input csv file"""
    p_name = []
    for row in file:
            p_name.append(row['Partner Name'])

    partner_name = ', '.join(set(p_name))
    return partner_name


def get_attachment(folder_name):
    path = os.path.join(settings.WRITE_FOLDER, 'merchants', 'visa', folder_name)
    pattern = re.compile("^CAID_\w+_LoyaltyAngels_[0-9]{8}.xlsx$")

    for entry in scandir(path):
        if pattern.match(entry.name):
            attachment = os.path.join(path, entry.name)
            return attachment

    return None


def archive_files(src_dir, now):
    """Archive generated files"""
    dst_dir = os.path.join(settings.WRITE_FOLDER, 'merchants', src_dir, now)
    src_dir = os.path.join(settings.WRITE_FOLDER, 'merchants', src_dir)
    os.makedirs(dst_dir, exist_ok=True)
    copy_local(src_dir, dst_dir)


def copy_local(src_dir, dst_dir):
    """Copy files locally from one directory to another"""
    for entry in scandir(src_dir):
        if entry.is_file(follow_symlinks=False):
            shutil.move(entry.path, dst_dir)


def onboard_mids(file, send_export, ignore_postcode):
    file = format_json_input(file)
    export(file, ignore_postcode)

    # Amex only requires SFTP
    url, username, password, dst_dir = settings.TRANSACTION_MATCHING_FILES_CONFIG[2:]
    src_dir = os.path.join(settings.WRITE_FOLDER, 'merchants', 'amex')
    if send_export:
        upload_sftp(url, username, password, src_dir, dst_dir)

    partner_name = get_partner_name(file)
    content = 'Please load the attached MIDs for {} and confirm your forecast on-boarding date.'.format(partner_name)

    # Visa & MasterCard
    now = arrow.utcnow().format('DDMMYY_hhmmss')
    for src_dir in ['visa', 'mastercard', 'amex']:
        archive_files(src_dir, now)

    attachment = get_attachment(now)

    if send_export:
        update_amex_sequence_number()
        send_email('visa', partner_name, content, attachment)
        send_email('mastercard', partner_name, content)

    return now
