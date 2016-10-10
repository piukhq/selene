import csv
import arrow
import os
import settings

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

        visa_header = ['GLB_MID', 'ACQUIRER_MID', 'GLB_MERCHANT_NAME', 'MERCHANT_CITY', 'POST_CODE', 'ADDRESS',
                       'ALTERNATIVE_MERCHANT_NAME', 'STATUS', 'VISA_COMMENTS', 'MSG_COMMENTS'
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
            path = os.path.join(settings.APP_DIR, 'merchants/visa', 'cass_inp.csv')
            with open(path, 'w') as csv_file:
                csv_writer = csv.writer(csv_file, quoting=csv.QUOTE_NONE, escapechar='')
                for merchant in merchants:
                    csv_writer.writerow(['visa',
                                         merchant['Visa MIDs'],
                                         merchant['Scheme'].strip('"'),
                                         merchant['Partner Name'].strip('"')
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

    def export_merchants(self, merchants, validated):
        """
        uses a given set of merchants to generate a file in Visa input file format
        :param merchants: a list of merchants to send to Visa
        :return: None
        """
        detail_record_count = len(merchants)
        file_num = 1  # sequential_file_number() + 1

        file = VisaMerchantFile()

        for merchant in merchants:
            # TODO: 90523 might be partner ID or similar but is a BINK identifier; confirm
            detail = ['90523', merchant['Visa MIDs'], merchant['Partner Name'], merchant['Town/City'],
                      merchant['Postcode'],
                      merchant['Address (Building Name/Number, Street)'], '', 'New', '', '',
                      ]
            file.add_detail(detail)

        file_name = self.create_file_name(validated)
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

    def create_file_name(self, validated):
        # e.g. PVnnn_GLBMID_BINK_yyyymmdd.xlsx
        file_name = ''

        pv_num = 'nnn'
        glb_mid = '12345'
        mrch_name = 'MrchName'

        file_name = '{}{}{}{}{}{}'.format(
            'PV',
            pv_num + '_',
            glb_mid + '_',
            'BINK_',
            arrow.now().format('YYYYMMDD'),
            '.xlsx'
        )

        if not validated:
            file_name = 'INVALID_' + file_name

        return file_name
