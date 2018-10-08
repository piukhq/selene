from flask import Blueprint, render_template, request, flash, redirect
from flask_uploads import UploadSet

from app.utils import process_mids_file

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
                flash('File uploaded', 'success')
            except Exception as e:
                flash('Error: {}'.format(e), 'danger')
        else:
            flash('Incorrect File type. Please upload a csv.', 'warning')

    return render_template('index.html', messages=messages)
