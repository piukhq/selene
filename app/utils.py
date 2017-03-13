import re
import importlib

from app.active import AGENTS


def resolve_agent(name):
    class_path = AGENTS[name]
    module_name, class_name = class_path.split(".")
    module = importlib.import_module('app.agents.{}'.format(module_name))
    return getattr(module, class_name)

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
