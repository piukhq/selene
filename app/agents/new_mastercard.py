import os
import io

import csv
import arrow

import settings
from app.agents.base import BaseProvider
from app.utils import save_blob


class MastercardMerchantFile:

    def __init__(self):
        self.mastercard_lines = []
        self.project_id = "BINK"

    def set_header(self, writer):
        """
        write headers of csv file for mastercard
        :param writer: csv writer
        :return:
        """

        row = [
            10,
            self.project_id,
            arrow.utcnow().format("YYYYMMDDHHmmss")
        ]
        writer.writerow(row)

    def set_data(self, writer):
        writer.writerows(self.mastercard_lines)

    def get_data(self):
        """Retrieve a list of lines of mastercard data"""
        return self.mastercard_lines

    def add_detail(self, detail):
        """Add a detail record for a line in the mastercard output file
        :param detail: the detail to add
        :return: None
        """
        row = [""] * 38
        today = arrow.utcnow().format("MM/DD/YYYY")

        row[0] = 20
        row[2] = detail[6]  # Action
        row[7] = detail[1]  # Merchant Name
        row[10] = detail[4]  # Merchant Address
        row[12] = detail[2]  # Merchant City
        row[14] = detail[5]  # Merchant State/Province
        row[16] = detail[3]  # Merchant Postcode
        row[18] = "UK"
        row[37] = row[28] = today

        self.mastercard_lines.append(row)

    def set_trailer(self, writer):
        row = [
            30,
            self.project_id,
            len(self.mastercard_lines)
        ]

        writer.writerow(row)


class MasterCard(BaseProvider):
    name = 'MasterCard'
    col_name = 'MasterCard MIDs'

    def export(self):
        mids_dict = self.df.to_dict('records')

        file = MastercardMerchantFile()

        for count, merchant in enumerate(mids_dict):

            detail = [merchant['MasterCard MIDs'], merchant['Partner Name'], merchant['Town/City'],
                      merchant['Postcode'], merchant['Address (Building Name/Number, Street)'],
                      '', merchant['Action'],
                      ]

            file.add_detail(detail)

        file_name = self.create_file_name(validated=True)
        self.write_to_file(file, file_name, self.timestamp)

    @staticmethod
    def create_file_name(validated):

        file_name = 'MAS_INPUT_BINK.csv'

        if not validated:
            file_name = 'INVALID_' + file_name

        return file_name

    @staticmethod
    def write_to_file(input_file, file_name, timestamp):
        """
        writes the given input file to a file under a given name.
        :param input_file: the file to write
        :param file_name: the file name under which to write the data
        :param timestamp: string datetime
        :return: None
        """
        path = os.path.join(settings.WRITE_FOLDER, 'merchants', 'mastercard', timestamp)
        file = io.StringIO()

        writer = csv.writer(file, delimiter=',', quotechar='"')

        input_file.set_header(writer)
        input_file.set_data(writer)
        input_file.set_trailer(writer)

        save_blob(file.getvalue(), container='dev-media', filename=file_name, path=path, type='text')
