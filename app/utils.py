import requests
import importlib

from app.active import AGENTS


def resolve_agent(name):
    class_path = AGENTS[name]
    module_name, class_name = class_path.split(".")
    module = importlib.import_module('app.agents.{}'.format(module_name))
    return getattr(module, class_name)


def validate_uk_postcode(postcode):
    """Validate a UK post code"""

    result = False
    if len(postcode):
        r = requests.get('http://api.postcodes.io/postcodes/{}/validate'.format(postcode))

        if r.status_code == 200:
            try:
                result = r.json()['result']
            except KeyError:
                print("EXCEPTION: KeyError 'result' for post code {}".format(postcode))
        else:
            print('Got HTTP status code {} from third party post code validator for post code {}.'.format(r.status_code, postcode))

    if result:
        print('Post code {} is valid'.format(postcode))
    else:
        print('Post code {} is invalid'.format(postcode))

    return result
