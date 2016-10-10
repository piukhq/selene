class SourceFormat(object):
    delimiter = ','
    column_names = ['Partner Name', 'American Express MIDs', 'MasterCard MIDs', 'Visa MIDs',
                    'Address (Building Name/Number, Street)', 'Postcode', 'Town/City', 'County/State',
                    'Country', 'Action', 'Scheme',
                    ]

    column_keep = {'Partner Name', 'American Express MIDs', 'MasterCard MIDs', 'Visa MIDs',
                   'Address (Building Name/Number, Street)', 'Postcode', 'Town/City', 'County/State',
                   'Country', 'Action', 'Scheme',
                   }
