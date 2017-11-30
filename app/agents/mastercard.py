import csv
import arrow
import os
import settings


class MastercardMerchantFile:

    def __init__(self):
        self.mastercard_lines = []

    def set_header(self, ws1):
        """
        set the header record for the file
        :param ws1: the header to use
        :return: None
        """
        pass

    def get_data(self):
        """Retrieve a list of lines of mastercard data"""
        return self.mastercard_lines

    def add_detail(self, detail):
        """Add a detail record for a line in the mastercard output file
        :param detail: the detail to add
        :return: None
        """
        self.mastercard_lines.append(detail)


class MasterCard:
    def __init__(self):
        pass

    @staticmethod
    def has_mid(element):
        """return True if there is a mastercard mid in the row"""

        if len(str(element)):
            return True

        return False

    @staticmethod
    def write_transaction_matched_csv(merchants):
        a = arrow.utcnow()
        filename = 'cass_inp_mastercard_{}'.format(merchants[0]['Partner Name']) + '_{}'.format(a.timestamp) + '.csv'
        path = os.path.join(settings.APP_DIR, 'merchants/mastercard', filename)
        try:
            with open(path, 'w') as csv_file:
                csv_writer = csv.writer(csv_file, quoting=csv.QUOTE_NONE, escapechar='')
                for merchant in merchants:
                    csv_writer.writerow(['mastercard',
                                         merchant['MasterCard MIDs'].strip(' '),
                                         merchant['Scheme'].strip('" ').lower(),
                                         merchant['Partner Name'].strip('" '),
                                         merchant['Town/City'].strip('" '),
                                         merchant['Postcode'].strip('" '),
                                         ])

        except IOError:
            raise Exception('Error writing file:' + path)

    @staticmethod
    def write_duplicates_file(duplicates):
        a = arrow.utcnow()
        filename = 'duplicates_mastercard_{}.txt'.format(a.format('DD-MM-YYYY'))
        path = os.path.join(settings.APP_DIR, 'merchants/mastercard', filename)
        try:
            with open(path, 'w') as dup_file:
                dup_file.write('Date of file creation: {}\n'.format(a.format('DD-MM-YYYY')))
                for dup in duplicates:
                    dup_file.write(dup + '\n')

        except IOError:
            raise Exception('Error writing file:' + path)

    @staticmethod
    def create_file_name(validated):
        # e.g. ???

        file_name = ''

        if not validated:
            file_name = 'INVALID_' + file_name

        return file_name
