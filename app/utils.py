import os
import re
import importlib
import json
import csv
from settings import APP_DIR

from app.active import AGENTS


def resolve_agent(name):
    class_path = AGENTS[name]
    module_name, class_name = class_path.split(".")
    agent_module = importlib.import_module('app.agents.{}'.format(module_name))
    return getattr(agent_module, class_name)


def validate_uk_postcode(postcode):
    # validate post code using regex
    pattern = re.compile('^[A-Z]{2}[0-9][A-Z] *?[0-9][A-Z]{2}$'
                         '|^[A-Z][0-9][A-Z] *?[0-9][A-Z]{2}$'
                         '|^[A-Z][0-9] *?[0-9][A-Z]{2}$'
                         '|^[A-Z][0-9]{2} *?[0-9][A-Z]{2}$'
                         '|^[A-Z]{2}[0-9] *?[0-9][A-Z]{2}$'
                         '|^[A-Z]{2}[0-9]{2} *?[0-9][A-Z]{2}$')

    if not re.match(pattern, postcode):
        return False

    return True


def csv_to_json(csv_file):
    data = []
    with open(csv_file, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)

    return json.dumps(data)


def csv_to_weird_json(csv_file):
    data = []
    with open(csv_file, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            data.append(row)
    return data


def list_json_to_dict_json(file):
    data = list()
    for i in range(1, len(file)):
        data.append(dict(zip(file[0], file[i])))
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
    folder = APP_DIR + path
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(e)


def wipe_output_folders():
    empty_folder('/merchants/visa')
    empty_folder('/merchants/amex')
    empty_folder('/merchants/mastercard')
