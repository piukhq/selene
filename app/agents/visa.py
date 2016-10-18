import csv
import arrow
import os
import settings
import random

from openpyxl import Workbook

from app.source_format import SourceFormat

class VisaMerchantFile():

    def __init__(self):
        self.visa_lines = []

    def set_header(self, ws1):
        """
        set the header record for the file
        :param header: the header to use
        :return: None
        """
        ws1.title = "PVnnn_90523_Choice_20160101"

        visa_header = ['CUSTOMER_MERCHANT_ID', 'ACQUIRER_CAI', 'MERCHANT_NAME', 'MERCHANT_CITY', 'POST_CODE', 'ADDRESS',
                       'ALTERNATIVE_MERCHANT_NAME', 'STATUS', 'VISA_VALIDATION_COMMENTS', 'CUSTOMER_COMMENTS'
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


class Visa(SourceFormat):
    def __init__(self):
        pass

    def has_mid(self, row):
        """return True if there is a visa mid in the row"""
        if row['Visa MIDs'] != '':
            try:
                mid = int(row['Visa MIDs'])
                return True
            except:
                return False

        return False

    def write_transaction_matched_csv(self, merchants):
        try:
            a = arrow.utcnow()
            path = os.path.join(settings.APP_DIR, 'merchants/visa', 'cass_inp_visa_{}'.format(merchants[0]['Partner Name']) + '_{}'.format(a.timestamp) + '.csv')
            with open(path, 'w') as csv_file:
                csv_writer = csv.writer(csv_file, quoting=csv.QUOTE_NONE, escapechar='')
                for merchant in merchants:
                    merchant_partner_town_field = merchant['Partner Name'].strip('"') + \
                                          ' - ' + \
                                          merchant['Town/City'].strip('"')
                    csv_writer.writerow(['visa',
                                         merchant['Visa MIDs'],
                                         merchant['Scheme'].strip('"').lower(),
                                         merchant_partner_town_field,
                                         ])

        except IOError as err:
            status = 'error'
            raise Exception('Error writing file:' + path)

    @staticmethod
    def write_to_file(input_file, file_name):
        """
        writes the given input file to a file under a given name.
        :param visa_input_file: the file to write
        :param file_name: the file name under which to write the data
        :return: None
        """

        path = os.path.join(settings.APP_DIR, 'merchants/visa', file_name)

        wb = Workbook()
        ws1 = wb.active
        input_file.set_header(ws1)
        visa_lines = input_file.get_data()
        for line in visa_lines:
            ws1.append(line)

        wb.save(path)

    def export_merchants(self, merchants, validated, reason=[]):
        """
        uses a given set of merchants to generate a file in Visa input file format
        :param merchants: a list of merchants to send to Visa
        :return: None
        """
        detail_record_count = len(merchants)
        file_num = 1  # sequential_file_number() + 1

        file = VisaMerchantFile()

        reference_scheme_id = ''
        for count, merchant in enumerate(merchants):
            reference_scheme_id = merchant['Scheme ID']
            detail = [merchant['Scheme ID'], merchant['Visa MIDs'], merchant['Partner Name'], merchant['Town/City'],
                      merchant['Postcode'],
                      merchant['Address (Building Name/Number, Street)'], '', 'New', '',
                      ]
            if validated:
                detail.append('')
            else:
                detail.append(reason[count])

            file.add_detail(detail)

        file_name = self.create_file_name(validated, reference_scheme_id)
        try:
            self.write_to_file(file, file_name)
            status = 'written'
        except IOError as err:
            status = 'error'
            raise Exception('Error writing file:' + file_name)

        log = {
            'provider': 'bink',
            'receiver': 'visa',
            'file_name': file_name,
            'date': arrow.now(),
            'process_date': arrow.now(),
            'status': status,
            'file_type': 'out',
            'direction': 'out',
            'sequence_number': file_num,
            'comment': 'Merchant onboarding'
        }
        # insert_file_log(log)

    def create_file_name(self, validated, reference_scheme_id):
        # e.g. PVnnn_GLBMID_BINK_yyyymmdd.xlsx
        file_name = ''

        pv_num = 'nnn'
        cust_merch_id = reference_scheme_id
        mrch_name = 'MrchName'

        file_name = '{}{}{}{}{}{}'.format(
            'PV',
            pv_num + '_',
            cust_merch_id + '_',
            'BINK_',
            arrow.now().format('YYYYMMDD'),
            '.xlsx'
        )

        if not validated:
            file_name = 'INVALID_' + file_name

        return file_name