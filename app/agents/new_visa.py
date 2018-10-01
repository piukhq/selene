import os

import arrow
from openpyxl import Workbook
from openpyxl.writer.excel import save_virtual_workbook

import settings
from app.agents.base import BaseProvider
from app.utils import save_blob


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


class Visa(BaseProvider):
    name = 'Visa'
    col_name = 'Visa MIDs'

    action_translate = dict(
        A='On-Board',
        U='Update',
        D='Remove'
    )

    def export(self):
        file = VisaMerchantFile()
        partner_name = ''

        mids_dict = self.df.to_dict('records')

        for count, merchant in enumerate(mids_dict):
            if count == 0:
                partner_name = merchant['Partner Name']

            action = self.action_translate.get(merchant['Action'])

            detail = [merchant['Visa MIDs'], merchant['Partner Name'], merchant['Town/City'],
                      merchant['Postcode'], merchant['Address (Building Name/Number, Street)'],
                      '', action,
                      ]

            file.add_detail(detail)

        file_name = self.create_file_name(validated=True, merchant_name=partner_name)
        self.write_to_file(file, file_name, self.timestamp)

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

    def write_to_file(self, input_file, file_name, now):
        """
        writes the given input file to a file under a given name.
        :param input_file: the file to write
        :param file_name: the file name under which to write the data
        :param now: string datetime
        :return: None
        """
        path = os.path.join(settings.WRITE_FOLDER, 'merchants', self.name.replace(' ', '_').lower(), now)

        wb = Workbook()
        ws1 = wb.active
        input_file.set_header(ws1)
        visa_lines = input_file.get_data()
        for line in visa_lines:
            ws1.append(line)

        virtual_wb = save_virtual_workbook(wb)
        save_blob(virtual_wb, container='dev-media', filename=file_name, path=path, type='bytes')
