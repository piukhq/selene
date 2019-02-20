import csv
import io
import os

import settings
from app import utils
from app.utils import save_blob


class BaseProvider:
    PARTNER_NAME = 'Partner Name'
    TOWN_CITY = 'Town/City'
    ACTION = 'Action'
    POSTCODE = 'Postcode'
    SCHEME = 'Scheme'

    name = None
    mids_col_name = None

    def __init__(self, dataframe, timestamp, **kwargs):
        self.df = dataframe
        self.timestamp = timestamp
        self.input_headers = self.df.columns.values
        self.initial_row_count = len(self.df[self.mids_col_name].index)
        self.invalid_rows = []
        self.invalid_row_count = 0
        self.duplicates_count = 0

        self._clean_dataframe()

    def __str__(self):
        return '{} - Total rows - {}'.format(self.name, self.initial_row_count)

    @property
    def valid_rows_count(self):
        return self.initial_row_count - self.invalid_row_count - self.duplicates_count

    def _clean_dataframe(self):
        columns_to_clean = [self.mids_col_name, self.PARTNER_NAME, self.TOWN_CITY, self.ACTION, self.POSTCODE]

        for column in columns_to_clean:
            self._remove_null_rows(column_name=column)

        self._remove_duplicate_mids(column=self.mids_col_name)

        self._remove_invalid_postcode_rows(postcode_col=self.POSTCODE)

    def _remove_duplicate_mids(self, column):
        initial_row_size = self.df[column].size
        self.df = self.df.drop_duplicates(column)

        self.duplicates_count = initial_row_size - self.df[column].size

    def _remove_null_rows(self, column_name):
        total_null_rows = self.df[column_name].isnull().sum()

        if total_null_rows > 0:
            dropped_null_df = self.df.dropna(subset=[column_name])
            null_rows = self.df[~self.df.index.isin(dropped_null_df.index)]

            self.df = dropped_null_df
            self.invalid_row_count += len(null_rows.index)
            self.invalid_rows += list(null_rows.index.values)
            print("{} has null rows for {} - Total: {}".format(self.name, column_name, len(null_rows.index)))

    def _remove_invalid_postcode_rows(self, postcode_col, index_value=False):
        invalid_postcode_rows = []
        for row in self.df.itertuples(index=True, name='Postcodes'):
            if index_value:
                # +1 to postcode_col to make up for the added index column
                postcode = str(row[postcode_col + 1]).strip().upper()
            else:
                postcode = str(getattr(row, postcode_col)).strip().upper()

            if not utils.validate_uk_postcode(postcode):
                invalid_postcode_rows.append(row[0])

        if invalid_postcode_rows:
            self.invalid_row_count += len(invalid_postcode_rows)
            self.invalid_rows += invalid_postcode_rows
            self.df = self.df.drop(invalid_postcode_rows)
            print("Invalid postcodes - Total: {}".format(len(invalid_postcode_rows)))

    def write_transaction_matched_csv(self, mids_dicts=None, path=None):
        mids_dicts = mids_dicts or self.df.to_dict('records')
        if not mids_dicts:
            return

        partner_name = mids_dicts[0]['Partner Name'].replace(' ', '_').lower()
        provider_name = self.name.replace(' ', '_').lower()
        file_name = 'cass_inp_{}_{}_{}.csv'.format(provider_name, partner_name, self.timestamp)

        path = path or os.path.join(settings.WRITE_FOLDER, 'merchants', provider_name, self.timestamp)
        file = io.StringIO()

        csv_writer = csv.writer(file, quoting=csv.QUOTE_NONE, escapechar='"')
        for row in mids_dicts:
            try:
                csv_writer.writerow([
                    provider_name,
                    row[self.mids_col_name].strip(),
                    row['Scheme'].strip().lower(),
                    row['Partner Name'].strip(),
                    row['Town/City'].strip(),
                    row['Postcode'].strip(),
                    'A'
                ])
            except Exception as e:
                raise ValueError(f'Error writing to file. Row: {row}') from e

        save_blob(file.getvalue(), container='dev-media', filename=file_name, path=path, content_type='text')

    def create_messages(self):
        total_imported = "{}".format(self)
        invalid_mids = "Invalid MIDs: {} - Rows: {}".format(self.invalid_row_count,
                                                            self.invalid_rows)
        total_duplicates = "Total duplicates: {}".format(self.duplicates_count)
        total_exported = "{} MIDs exported: {}".format(self.name, self.valid_rows_count)

        return [total_imported, invalid_mids, total_duplicates, total_exported]

    def export(self):
        raise NotImplementedError('Export method has not been implemented for {}'.format(self.name))
