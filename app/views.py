import arrow
import shutil
from flask import Blueprint, render_template, request, flash, redirect
from flask_uploads import UploadSet
import pandas as pd
from io import StringIO, BytesIO

from app.agents.mastercard import MasterCard
from app.agents.register import PROVIDERS_MAP

bp = Blueprint('selene', __name__)


files = UploadSet('files', extensions=('csv',))


@bp.route("/", methods=['GET', 'POST'])
def index():
    input_field_name = 'input_file'
    messages = None

    if request.method == 'POST':
        if input_field_name not in request.files:
            flash('No file part')
            return redirect(request.url)

        input_file = request.files[input_field_name]
        if input_file.filename == '':
            flash('No file selected')
            return redirect(request.url)

        basename = files.get_basename(input_file.filename)
        if files.file_allowed(input_file, basename):
            try:
                messages = process_mids_file(input_file)
                flash('File uploaded')
            except Exception as e:
                flash('Error: {}'.format(e))
                raise
        else:
            flash('Incorrect File type. Please upload a csv.')

    return render_template('index.html', messages=messages)


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
    valid_headers, invalid_headers = validate_headers(headers)

    if valid_headers:
        dataframes = {}

        for provider in PROVIDERS_MAP:
            columns_to_drop = [agent_class.mids_col_name for name, agent_class in PROVIDERS_MAP.items() if name != provider]
            dataframes[provider] = original_df.drop(columns_to_drop, axis=1)

            agent_instance = PROVIDERS_MAP[provider](dataframes[provider], timestamp)
            agent_instance.export()

            agent_instance.write_transaction_matched_csv()
            print('{} Cassandra file exported\n\n'.format(agent_instance.name))

            message = agent_instance.create_messages()
            messages.append(message)
    else:
        if is_handback_file(headers):
            b = BytesIO(bytes_content)
            df = pd.read_csv(b, sep='|', header=None, skipfooter=1, skiprows=1, dtype={23: str})

            agent_instance = MasterCard(df, timestamp, handback=True)
            messages = agent_instance.process_handback_file()
        else:
            messages = 'Following headers are invalid/misspelled: {}'.format(invalid_headers)

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

