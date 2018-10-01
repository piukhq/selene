import os
import re
import csv
import json
import shutil
import importlib
from azure.storage.blob import BlockBlobService, ContentSettings

import settings

from app.active import AGENTS
from app.models import Sequence, db


bbs = BlockBlobService(
        account_name=settings.AZURE_ACCOUNT_NAME,
        account_key=settings.AZURE_ACCOUNT_KEY
    )


def resolve_agent(name):
    class_path = AGENTS[name]
    module_name, class_name = class_path.split(".")
    agent_module = importlib.import_module('app.agents.{}'.format(module_name))
    return getattr(agent_module, class_name)


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


def get_agent(partner_slug):
    agent_class = resolve_agent(partner_slug)
    return agent_class()


def csv_to_list_json(csv_file):
    data = list()
    with open(csv_file, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            data.append(row)

    return data


def list_json_to_dict_json(file):
    data = list()
    header = file[0]
    for row in file[1:]:
        if ''.join(row):
            data.append(dict(zip(header, row)))

    return data


def format_json_input(json_file):
    file = json.loads(json_file) if isinstance(json_file, str) else json_file
    if isinstance(file[0], list):
        return list_json_to_dict_json(file)

    return file


def update_amex_sequence_number():
    sequence = Sequence.query.filter_by(scheme_provider='amex').first()
    sequence.next_seq_number += 1
    db.session.commit()


def get_attachment(path, provider):
    pattern = settings.GET_ATTACHMENT[provider]
    attachment = None
    for entry in os.scandir(path):
        if pattern.match(entry.name):
            attachment = os.path.join(path, entry.name)

    return attachment


def prepare_cassandra_file(file, headers):
    """
    Remove trailing empty lines, and add headers.
    :param file: input json file as list of lists with no headers
    :param headers: cassandra table headers
    :return: list of dictionaries with no trailing empty lines.
    """

    if set(headers) == set(file[0]):
        file = file[1:]

    while not ''.join(file[-1]):
        file = file[:-1]

    data = list()
    for row in file:

        if len(headers) != len(row):
            raise ValueError("Columns of the input file do not match the expected value")

        data.append(dict(zip(headers, row)))

    return data


def save_blob(content, container, filename, type='text', path=''):
    """
    Saves a file to the Azure Blob Storage.

    :param content: string or bytes to store as blob.
    :param container: string. Name of the blob storage container to save in.
    :param filename: string. Name of file.
    :param type: string. Must be either 'text' or 'bytes' depending on the content type.
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

    if type == 'text':
        args.update(text=content)
        bbs.create_blob_from_text(**args)
    elif type == 'bytes':
        args.update(blob=content)
        bbs.create_blob_from_bytes(**args)
