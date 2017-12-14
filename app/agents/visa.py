import csv
import arrow
import os
import settings

from openpyxl import Workbook


class VisaMerchantFile:

    def __init__(self):
        self.visa_lines = []

    @staticmethod
    def set_header(ws1):
        """
        set the header record for the file
        :param ws1: the header to use
        :return: None
        """
        ws1.title = "visa_merchant_ID_file"

        visa_header = ['CAID', 'MERCHANT_NAME', 'MERCHANT_CITY', 'POST_CODE', 'ADDRESS',
                       'Merchant Also Known As', 'Action (On-Board/Remove/Update)'
                       ]
        ws1.append(visa_header)

    def get_data(self):
        """Retrieve a list of lines of visa data"""
        return self.visa_lines

    def add_detail(self, detail):
        """Add a detail record for a line in the visa output file
        :param detail: the detail to add
        :return: None
        """
        self.visa_lines.append(detail)


class Visa:
    def __init__(self):
        pass

    @staticmethod
    def has_mid(row):
        """
        return True if there is a visa mid in the row
        """
        if row['Visa MIDs'] and row['Visa MIDs'] is not "":
            return True

        return False

    @staticmethod
    def write_transaction_matched_csv(merchants):

        a = arrow.utcnow()
        filename = 'cass_inp_visa_{}'.format(merchants[0]['Partner Name']) + '_{}'.format(a.timestamp) + '.csv'
        path = os.path.join(settings.WRITE_FOLDER, 'merchants/visa', filename)
        try:
            with open(path, 'w') as csv_file:
                csv_writer = csv.writer(csv_file, quoting=csv.QUOTE_NONE, escapechar='')
                for merchant in merchants:
                    csv_writer.writerow(['visa',
                                         merchant['Visa MIDs'].strip(' '),
                                         merchant['Scheme'].strip('" ').lower(),
                                         merchant['Partner Name'].strip('" '),
                                         merchant['Town/City'].strip('" '),
                                         merchant['Postcode'].strip('" '),
                                         ])

        except IOError:
            raise Exception('Error writing file:' + path)

    @staticmethod
    def write_to_file(input_file, file_name):
        """
        writes the given input file to a file under a given name.
        :param input_file: the file to write
        :param file_name: the file name under which to write the data
        :return: None
        """

        path = os.path.join(settings.WRITE_FOLDER, 'merchants/visa', file_name)

        wb = Workbook()
        ws1 = wb.active
        input_file.set_header(ws1)
        visa_lines = input_file.get_data()
        for line in visa_lines:
            ws1.append(line)

        wb.save(path)

    def export_merchants(self, merchants, validated, reason=None):
        """
        uses a given set of merchants to generate a file in Visa input file format
        :param merchants: a list of merchants to send to Visa
        :param validated:
        :param reason:
        :return: None
        """
        reason = reason or []

        file = VisaMerchantFile()
        partner_name = ''

        for count, merchant in enumerate(merchants):
            if count == 0:
                partner_name = merchant['Partner Name']

            detail = [merchant['Visa MIDs'], merchant['Partner Name'], merchant['Town/City'],
                      merchant['Postcode'], merchant['Address (Building Name/Number, Street)'],
                      '', 'On-Board',
                      ]
            if validated:
                detail.append('')
            else:
                detail.append(reason[count])

            file.add_detail(detail)

        file_name = self.create_file_name(validated, partner_name)
        try:
            self.write_to_file(file, file_name)
        except IOError:
            raise Exception('Error writing file:' + file_name)

    @staticmethod
    def create_file_name(validated, merchant_name):
        # e.g. PVnnn_GLBMID_BINK_yyyymmdd.xlsx
        # e.g. CAID_<merchant_name>_LoyaltyAngels_<date YYYYMMDD>.xlsx

        file_merchant_name = merchant_name.replace(" ", "")

        file_name = 'CAID_{}_{}_{}{}'.format(
            file_merchant_name,
            'LoyaltyAngels',
            arrow.now().format('YYYYMMDD'),
            '.xlsx'
        )

        if not validated:
            file_name = 'INVALID_' + file_name

        return file_name
