import csv
import arrow
import os
import settings


from app.source_format import SourceFormat

class MastercardMerchantFile():

    def __init__(self):
        self.mastercard_lines = []

    def set_header(self, ws1):
        """
        set the header record for the file
        :param header: the header to use
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


class MasterCard():
    def __init__(self):
        pass

    def has_mid(self, element):
        """return True if there is a mastercard mid in the row"""

        if len(str(element)):
            return True

        return False

    def write_transaction_matched_csv(self, merchants):
        try:
            a = arrow.utcnow()
            filename = 'cass_inp_mastercard_{}'.format(merchants[0]['Partner Name']) + '_{}'.format(a.timestamp) + '.csv'
            path = os.path.join(settings.APP_DIR, 'merchants/mastercard', filename)

            with open(path, 'w') as csv_file:
                csv_writer = csv.writer(csv_file, quoting=csv.QUOTE_NONE, escapechar='')
                for merchant in merchants:
                    csv_writer.writerow(['mastercard',
                                         merchant['MasterCard MIDs'],
                                         merchant['Scheme'].strip('"').lower(),
                                         merchant['Partner Name'].strip('"'),
                                         merchant['Town/City'].strip('"'),
                                         ])

        except IOError as err:
            status = 'error'
            raise Exception('Error writing file:' + path)


    def write_duplicates_csv(self, duplicates):
        try:
            a = arrow.utcnow()
            filename = 'dups_mastercard.txt'
            path = os.path.join(settings.APP_DIR, 'merchants/mastercard', filename)

            with open(path, 'w') as dup_file:
                dup_file.write('Date of file creation: {}\n'.format(a.format('DD-MM-YYYY')))
                for dup in duplicates:
                    dup_file.write(dup + '\n')

        except IOError as err:
            status = 'error'
            raise Exception('Error writing file:' + path)


    @staticmethod
    def write_to_file(input_file, file_name):
        """
        writes the given input file to a file under a given name.
        :param mastercard_input_file: the file to write
        :param file_name: the file name under which to write the data
        :return: None
        """

        pass

    def export_merchants(self, merchants, validated, reason=[]):
        """
        uses a given set of merchants to generate a file in Visa input file format
        :param merchants: a list of merchants to send to Visa
        :return: None
        """

        #log = {
        #    'provider': 'bink',
        #    'receiver': 'mastercard',
        #    'file_name': file_name,
        #    'date': arrow.now(),
        #    'process_date': arrow.now(),
        #    'status': status,
        #    'file_type': 'out',
        #    'direction': 'out',
        #    'sequence_number': file_num,
        #    'comment': 'Merchant onboarding'
        #}
        # insert_file_log(log)
        pass

    def create_file_name(self, validated):
        # e.g. ???

        file_name = ''

        if not validated:
            file_name = 'INVALID_' + file_name

        return file_name