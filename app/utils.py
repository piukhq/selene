import re

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
