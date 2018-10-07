import os
import io

import csv
import arrow
from io import StringIO
import pandas as pd

import settings
from app.agents.base import BaseProvider
from app.utils import save_blob, validate_uk_postcode


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
    mids_col_name = 'MasterCard MIDs'
    write_path = os.path.join(settings.WRITE_FOLDER, 'merchants', 'mastercard')

    def __init__(self, dataframe, timestamp, handback=False):
        if not handback:
            super(MasterCard, self).__init__(dataframe, timestamp)
        else:
            self.df = dataframe
            self.timestamp = timestamp
            self.input_headers = self.df.columns.values
            self.initial_row_count = len(self.df.index)
            self.invalid_rows = []
            self.invalid_row_count = 0
            self.duplicates_count = 0

    def export(self):
        mids_dict = self.df.to_dict('records')

        file = MastercardMerchantFile()

        for count, merchant in enumerate(mids_dict):

            detail = [merchant['MasterCard MIDs'], merchant['Partner Name'], merchant['Town/City'],
                      merchant['Postcode'], merchant['Address (Building Name/Number, Street)'],
                      '', merchant['Action'],
                      ]

            file.add_detail(detail)

        file_name = 'MAS_INPUT_BINK.csv'
        self.write_to_file(file, file_name)

    def write_to_file(self, input_file, file_name):
        """
        writes the given input file to a file under a given name.
        :param input_file: the file to write
        :param file_name: the file name under which to write the data
        :return: None
        """
        path = os.path.join(self.write_path, self.timestamp)
        file = io.StringIO()

        writer = csv.writer(file, delimiter=',', quotechar='"')

        input_file.set_header(writer)
        input_file.set_data(writer)
        input_file.set_trailer(writer)

        save_blob(file.getvalue(), container='dev-media', filename=file_name, path=path, type='text')

    def process_handback_file(self):
        self.write_path = os.path.join(self.write_path, 'handback')

        self.clean_handback_data()
        messages = [self.create_messages()]

        mids_dict = self.df.to_dict('records')
        self.write_transaction_matched_csv(mids_dict=mids_dict)

        return messages

    def clean_handback_data(self):
        self.SCHEME = 'Scheme'
        cols = {
            self.mids_col_name: 23,
            self.PARTNER_NAME: 7,
            self.TOWN_CITY: 13,
            self.SCHEME: 45,
            self.POSTCODE: 17
        }

        columns_to_clean = [cols[self.mids_col_name], cols[self.POSTCODE]]

        for column in columns_to_clean:
            self._remove_null_rows(column_name=column)

        self._remove_duplicate_mids(column=cols[self.mids_col_name])
        self._remove_invalid_postcode_rows(postcode_col=cols[self.POSTCODE], index_values=True)

        self.df = self.df[self.df.columns[[val for val in cols.values()]]]

        new_cols = {val: col for col, val in cols.items()}
        self.df = self.df.rename(columns=new_cols)

