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

    # old API key: KLogDsJB7E2Oy-2WHME-tQ2451
    result = False
    if len(postcode):
        r = requests.get('https://api.getAddress.io/v2/uk/{}?api-key=1h-2FYKur0-3JmtmPmNlRQ7622'.format(postcode))

        if r.status_code == 200:
            try:
                result = bool(r.json()['Addresses'])
            except KeyError:
                print("EXCEPTION: KeyError 'Addresses' for post code {}".format(postcode))
        else:
            print('Got HTTP status code {} from third party post code validator for post code {}.'.format(r.status_code, postcode))

    if result:
        print('Post code {} is valid'.format(postcode))
    else:
        print('Post code {} is invalid'.format(postcode))

    return result
