import os
import re
import importlib
import json
import csv
import shutil

from settings import WRITE_FOLDER
from app.active import AGENTS
from app.models import Sequence, db


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
    try:
        agent_class = resolve_agent(partner_slug)
        return agent_class()

    except Exception as ex:
        raise ex


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
        data.append(dict(zip(header, row)))

    return data


def format_json_input(json_file):
    try:
        file = json.loads(json_file) if isinstance(json_file, str) else json_file
        if isinstance(file[0], list):
            return list_json_to_dict_json(file)

        return file

    except Exception as e:
        return "wrong file format, exception: {}".format(e)


def empty_folder(path):
    for the_file in os.listdir(path):
        file_path = os.path.join(path, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)

            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)

        except Exception as e:
            raise e


def wipe_output_folders():
    for folder in ['visa', 'amex', 'mastercard']:
        path = os.path.join(WRITE_FOLDER, 'merchants', folder)
        empty_folder(path)


def update_amex_sequence_number():
    sequence = Sequence.query.filter_by(scheme_provider='amex').first()
    sequence.next_seq_number += 1
    db.session.commit()
