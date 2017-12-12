import re
import importlib
import json
import csv

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


def wipe_output_folders():
    # todo fill wipe folders function
    pass
