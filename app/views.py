import arrow
from flask import Blueprint, render_template, request, flash, redirect
from flask_uploads import UploadSet
import pandas as pd

from app.agents.register import PROVIDERS_MAP

bp = Blueprint('selene', __name__)


files = UploadSet('files', extensions=('csv',))


@bp.route("/", methods=['GET', 'POST'])
def index():
    input_field_name = 'input_file'

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
            process_mids_file(input_file)

            flash('File uploaded')
        else:
            flash('Incorrect File type. Please upload a csv.')

    return render_template('index.html')


def process_mids_file(file):
    timestamp = arrow.utcnow().format('DDMMYY_hhmmssSSS')

    # MIDs columns default to float type which could cause issues e.g removing leading 0s
    datatype_conversion = {agent_class.col_name: str for agent_class in PROVIDERS_MAP.values()}
    datatype_conversion.update({'Scheme ID': str})

    original_df = pd.read_csv(file.stream, dtype=datatype_conversion)

    dataframes = {}
    for provider in PROVIDERS_MAP:
        columns_to_drop = [agent_class.col_name for name, agent_class in PROVIDERS_MAP.items() if name != provider]
        dataframes[provider] = original_df.drop(columns_to_drop, axis=1)

        try:
            agent_instance = PROVIDERS_MAP[provider](dataframes[provider])
            print("\n{}".format(agent_instance))
            print("Valid MIDs: {}".format(agent_instance.valid_rows_count))
            print("Total duplicates: {}\n".format(agent_instance.duplicates_count))

            agent_instance.export(timestamp)
            print('{} MIDs exported\n\n'.format(agent_instance.name))
        except Exception as e:
            print(e)
            continue
