from azure.storage.blob import BlockBlobService, ContentSettings
from flask import Blueprint, render_template, request, flash, redirect
from flask_uploads import UploadSet

import settings

bp = Blueprint('selene', __name__)


files = UploadSet('files', extensions=('csv',))
bbs = BlockBlobService(
        account_name=settings.AZURE_ACCOUNT_NAME,
        account_key=settings.AZURE_ACCOUNT_KEY
    )


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

        base_name = files.get_basename(input_file.filename)
        if files.file_allowed(input_file, base_name):
            input_file_content = input_file.read().decode('utf-8')

            flash('File uploaded')
        else:
            flash('Incorrect File type. Please upload a csv.')

    return render_template('index.html')


def save_file(file, container, path=''):
    """
    Saves a file to the Azure Blob Storage.

    :param file: FileStorage instance.
    :param container: string. Name of the blob storage container to save in.
    :param path: string. Folder path to store the file within the container.
    :return: None
    """
    if path[0] == '/':
        path = path[1:]
    if path[-1] != '/':
        path = path + '/'

    bbs.create_blob_from_stream(container_name=container,
                                blob_name='{}{}'.format(path, file.filename),
                                content_settings=ContentSettings(content_type='text/csv'),
                                stream=file.stream)
