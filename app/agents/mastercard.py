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
    mids_col_name = 'MasterCard MIDs'
    write_path = os.path.join(settings.WRITE_FOLDER, 'merchants', 'mastercard')
    file = None

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
        mids_dicts = self.df.to_dict('records')

        file = MastercardMerchantFile()

        for count, merchant in enumerate(mids_dicts):

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
        self.file = io.StringIO()

        writer = csv.writer(self.file, delimiter=',', quotechar='"')

        input_file.set_header(writer)
        input_file.set_data(writer)
        input_file.set_trailer(writer)

        save_blob(self.file.getvalue(), container='dev-media', filename=file_name, path=path, content_type='text')

    def process_handback_file(self):
        self.write_path = os.path.join(self.write_path, 'handback')

        self.clean_handback_data()
        messages = [self.create_messages()]

        mids_dicts = self.df.to_dict('records')

        self.write_transaction_matched_csv(mids_dicts=mids_dicts, path=self.write_path)

        return messages

    def clean_handback_data(self):
        cols_to_index = {
            self.mids_col_name: 23,
            self.PARTNER_NAME: 7,
            self.TOWN_CITY: 13,
            self.SCHEME: 45,
            self.POSTCODE: 17
        }

        columns_to_clean = [cols_to_index[self.mids_col_name], cols_to_index[self.POSTCODE]]

        for column in columns_to_clean:
            self._remove_null_rows(column_name=column)

        self._remove_duplicate_mids(column=cols_to_index[self.mids_col_name])
        self._remove_invalid_postcode_rows(postcode_col=cols_to_index[self.POSTCODE], index_value=True)

        self.df = self.df[self.df.columns[[index for index in cols_to_index.values()]]]

        index_to_column_names = {index: col_name for col_name, index in cols_to_index.items()}
        self.df = self.df.rename(columns=index_to_column_names)
