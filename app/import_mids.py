import os
import settings
import arrow

from app import utils
from app.email import send_email
from app.active import AGENTS
from app.agents.amex import upload_sftp


def initialize_card_data():
    card_data = {}
    for k, v in AGENTS.items():
        agent_instance = utils.get_agent(k)
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

    if not utils.validate_uk_postcode(row['Postcode'].strip('"')):
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


def onboard_mids(file, send_export, ignore_postcode):
    file = utils.format_json_input(file)
    export(file, ignore_postcode)

    partner_name = get_partner_name(file)
    content = 'Please load the attached MIDs for {} and confirm your forecast on-boarding date.'.format(partner_name)

    # Visa & MasterCard
    now = arrow.utcnow().format('DDMMYY_hhmmss')
    for folder in ['visa', 'mastercard', 'amex']:
        utils.archive_files(folder, now)

    visa_path = os.path.join(settings.WRITE_FOLDER, 'merchants', 'visa', now)
    attachment = utils.get_attachment(visa_path, 'visa')
    url, username, password, dst_dir = settings.AMEX_SFTP_CONFIG

    if send_export:
        upload_sftp(url, username, password, now, dst_dir)
        utils.update_amex_sequence_number()
        send_email('visa', partner_name, content, attachment)
        send_email('mastercard', partner_name, content)

    return now
