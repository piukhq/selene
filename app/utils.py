from io import BytesIO

import arrow
import pandas as pd
import re
from azure.storage.blob import BlockBlobService, ContentSettings

import settings
from app.agents.mastercard import MasterCard
from app.agents.register import PROVIDERS_MAP
from app.models import Sequence, db


bbs = BlockBlobService(
        account_name=settings.AZURE_ACCOUNT_NAME,
        account_key=settings.AZURE_ACCOUNT_KEY
    )


def validate_uk_postcode(postcode):
    # validate post code using regex
    pattern = re.compile(
        '^[A-Z]{2}[0-9][A-Z] *?[0-9][A-Z]{2}$'
        '|^[A-Z][0-9][A-Z] *?[0-9][A-Z]{2}$'
        '|^[A-Z][0-9] *?[0-9][A-Z]{2}$'
        '|^[A-Z][0-9]{2} *?[0-9][A-Z]{2}$'
        '|^[A-Z]{2}[0-9] *?[0-9][A-Z]{2}$'
        '|^[A-Z]{2}[0-9]{2} *?[0-9][A-Z]{2}$'
    )

    if not re.match(pattern, postcode):
        return False

    return True


def update_amex_sequence_number():
    sequence = Sequence.query.filter_by(scheme_provider='amex').first()
    sequence.next_seq_number += 1
    db.session.commit()


def process_mids_file(file):
    timestamp = arrow.utcnow().format('DDMMYY_hhmmssSSS')

    # MIDs columns default to float type which could cause issues e.g removing leading 0s
    datatype_conversion = {agent_class.mids_col_name: str for agent_class in PROVIDERS_MAP.values()}
    datatype_conversion.update({'Scheme ID': str})

    bytes_content = file.stream.read()
    file = BytesIO(bytes_content)
    original_df = pd.read_csv(file, dtype=datatype_conversion)

    messages = []
    headers = list(original_df.columns.values)
    is_valid_headers, invalid_headers = validate_headers(headers)

    if is_valid_headers:
        dataframes = {}

        for provider in PROVIDERS_MAP:
            columns_to_drop = [agent_class.mids_col_name for name, agent_class in PROVIDERS_MAP.items()
                               if name != provider]

            dataframes[provider] = original_df.drop(columns_to_drop, axis=1)
            agent_instance = PROVIDERS_MAP[provider](dataframes[provider], timestamp)

            agent_instance.export()
            agent_instance.write_transaction_matched_csv()

            message = agent_instance.create_messages()
            messages.append(message)
    else:
        if is_handback_file(headers):
            file_copy = BytesIO(bytes_content)
            dataframe_with_footer = pd.read_csv(file_copy, sep='|', header=None, skiprows=1, dtype={23: str})
            dataframe = dataframe_with_footer.iloc[:-1]

            agent_instance = MasterCard(dataframe, timestamp, handback=True)
            messages = agent_instance.process_handback_file()
        else:
            raise ValueError('Following headers are invalid/misspelled: {}'.format(invalid_headers))

    return messages


def validate_headers(headers):
    is_valid = True
    expected_headers = ['Partner Name', 'American Express MIDs', 'MasterCard MIDs', 'Visa MIDs',
                        'Address (Building Name/Number, Street)', 'Postcode', 'Town/City', 'County/State',
                        'Country', 'Action', 'Scheme', 'Scheme ID']

    if len(headers) != len(expected_headers):
        is_valid = False

    invalid_headers = []
    for header in headers:
        if header not in expected_headers:
            invalid_headers.append(header)

    if invalid_headers:
        is_valid = False

    return is_valid, invalid_headers


def is_handback_file(headers):
    return headers[0].startswith('10') and 'BINK' in headers[0]


def save_blob(content, container, filename, content_type='text', path=''):
    """
    Saves a file to the Azure Blob Storage.

    :param content: string or bytes to store as blob.
    :param container: string. Name of the blob storage container to save in.
    :param filename: string. Name of file.
    :param content_type: string. Must be either 'text' or 'bytes' depending on the content type.
    :param path: string. Folder path to store the file within the container.
    :return: None
    """
    if path:
        if path[0] == '/':
            path = path[1:]
        if path[-1] != '/':
            path = path + '/'

    args = {
        'container_name': container,
        'blob_name': '{}{}'.format(path, filename),
        'content_settings': ContentSettings(content_type='text/csv'),
    }

    if content_type == 'text':
        args.update(text=content)
        bbs.create_blob_from_text(**args)
    elif content_type == 'bytes':
        args.update(blob=content)
        bbs.create_blob_from_bytes(**args)
