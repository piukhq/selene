import re
import importlib

from app.active import AGENTS


def resolve_agent(name):
    class_path = AGENTS[name]
    module_name, class_name = class_path.split(".")
    module = importlib.import_module('app.agents.{}'.format(module_name))
    return getattr(module, class_name)


def validate_uk_postcode(postcode):
    """Validate a UK post code"""

    # validate post code using regex
    pattern = re.compile('^(([gG][iI][rR] {0,}0[aA]{2})|((([a-pr-uwyzA-PR-UWYZ]'
                         '[a-hk-yA-HK-Y]?[0-9][0-9]?)|(([a-pr-uwyzA-PR-UWYZ][0-9]'
                         '[a-hjkstuwA-HJKSTUW])|([a-pr-uwyzA-PR-UWYZ][a-hk-yA-HK-Y]'
                         '[0-9][abehmnprv-yABEHMNPRV-Y]))) {0,}[0-9][abd-hjlnp-uw-z'
                         'ABD-HJLNP-UW-Z]{2}))$')

    if not re.match(pattern, postcode):
        return False

    return True
