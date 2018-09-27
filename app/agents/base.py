from app import utils

PARTNER_NAME = 'Partner Name'
TOWN_CITY = 'Town/City'
ACTION = 'Action'
POSTCODE = 'Postcode'


class BaseProvider:
    name = None
    col_name = None

    invalid_row_count = 0
    duplicates_count = 0

    def __init__(self, dataframe):
        self.df = dataframe
        self.input_headers = self.df.columns.values
        self.initial_row_count = len(self.df[self.col_name].index)

        self._clean_dataframe()

    def __str__(self):
        return '{} - Total rows - {}'.format(self.name, self.initial_row_count)

    @property
    def valid_mids(self):
        return self.initial_row_count - self.invalid_row_count - self.duplicates_count

    def _clean_dataframe(self):
        self._remove_duplicate_mids()

        columns_to_clean = [self.col_name, PARTNER_NAME, TOWN_CITY, ACTION, POSTCODE]

        for column in columns_to_clean:
            self._remove_null_rows(column_name=column)

        self._remove_invalid_postcode_rows(postcode_col=POSTCODE)

    def _remove_duplicate_mids(self):
        initial_row_size = self.df[self.col_name].size
        self.df.drop_duplicates(self.col_name, inplace=True)

        self.duplicates_count = initial_row_size - self.df[self.col_name].size

    def _remove_null_rows(self, column_name):
        total_null_rows = self.df[column_name].isnull().sum()

        if total_null_rows > 0:
            dropped_null_df = self.df.dropna(subset=[column_name])
            null_rows = self.df[~self.df.index.isin(dropped_null_df.index)]

            self.df = dropped_null_df
            self.invalid_row_count += len(null_rows.index)
            print("{} has null rows for {} - Total: {}".format(self.name, column_name, len(null_rows.index)))

    def _remove_invalid_postcode_rows(self, postcode_col):
        invalid_rows = []
        for row in self.df.itertuples(index=True, name='Postcodes'):
            postcode = str(getattr(row, postcode_col)).strip()

            if not utils.validate_uk_postcode(postcode):
                invalid_rows.append(row[0])

        if invalid_rows:
            self.invalid_row_count += len(invalid_rows)
            self.df = self.df.drop(invalid_rows)
            print("Invalid postcodes - Total: {}".format(len(invalid_rows)))

    def export(self):
        raise NotImplementedError('Export method has not been implemented for {}'.format(self.name))
