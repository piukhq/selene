import pandas as pd
from io import BytesIO

import arrow
from flask import Blueprint, render_template, request, flash, redirect
from flask_uploads import UploadSet

from app.agents.mastercard import MasterCard
from app.agents.register import PROVIDERS_MAP
from app.utils import validate_headers, is_handback_file

bp = Blueprint('selene', __name__)
files = UploadSet('files', extensions=('csv',))


@bp.route("/mids", methods=['GET', 'POST'])
def index():
    input_field_name = 'input_file'
    messages = None

    if request.method == 'POST':
        if input_field_name not in request.files:
            flash('No file part', 'warning')
            return redirect(request.url)

        input_file = request.files[input_field_name]
        if input_file.filename == '':
            flash('No file selected', 'warning')
            return redirect(request.url)

        basename = files.get_basename(input_file.filename)
        if files.file_allowed(input_file, basename):
            try:
                messages = process_mids_file(input_file)
                flash('File uploaded', 'success')
            except Exception as e:
                flash('Error: {}'.format(e), 'danger')
        else:
            flash('Incorrect File type. Please upload a csv.', 'warning')

    return render_template('index.html', messages=messages)


def process_mids_file(file):
    timestamp = arrow.utcnow().format('DDMMYY_hhmmssSSS')

    # MIDs columns default to float type which could cause issues e.g removing leading 0s
    datatype_conversion = {agent_class.mids_col_name: str for agent_class in PROVIDERS_MAP.values()}
    datatype_conversion.update({'Scheme ID': str})

    bytes_content = file.stream.read()
    file = BytesIO(bytes_content)
    original_df = pd.read_csv(file, dtype=datatype_conversion)

    headers = list(original_df.columns.values)
    is_valid_headers, invalid_headers, missing_headers = validate_headers(headers)

    messages = []
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
            invalid_message = ''
            missing_message = ''

            if invalid_headers:
                invalid_message = 'Invalid headers: {}'.format(invalid_headers)
            if missing_headers:
                missing_message = 'Missing headers: {}'.format(missing_headers)

            error_message = '<p style="margin-bottom: 0;">{}</p><p style="margin-bottom: 0;">{}</p>'

            raise ValueError(error_message.format(invalid_message, missing_message))

    return messages
