import csv
import arrow
import os
import settings


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
        row[2] = "A"
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


class MasterCard:
    def __init__(self):
        pass

    @staticmethod
    def has_mid(element):
        """return True if there is a mastercard mid in the row"""
        selected = element.get("MasterCard MIDs")
        if str(selected).isdigit():
            return True

        return False

    @staticmethod
    def write_transaction_matched_csv(merchants):
        a = arrow.utcnow()
        filename = 'cass_inp_mastercard_{}'.format(merchants[0]['Partner Name']) + '_{}'.format(a.timestamp) + '.csv'
        path = os.path.join(settings.APP_DIR, 'merchants/mastercard', filename)
        try:
            with open(path, 'w') as csv_file:
                csv_writer = csv.writer(csv_file, quoting=csv.QUOTE_NONE, escapechar='')
                for merchant in merchants:
                    csv_writer.writerow(['mastercard',
                                         merchant['MasterCard MIDs'].strip(' '),
                                         merchant['Scheme'].strip('" ').lower(),
                                         merchant['Partner Name'].strip('" '),
                                         merchant['Town/City'].strip('" '),
                                         merchant['Postcode'].strip('" '),
                                         ])

        except IOError:
            raise Exception('Error writing file:' + path)

    @staticmethod
    def write_duplicates_file(duplicates):
        a = arrow.utcnow()
        filename = 'duplicates_mastercard_{}.txt'.format(a.format('DD-MM-YYYY'))
        path = os.path.join(settings.APP_DIR, 'merchants/mastercard', filename)
        try:
            with open(path, 'w') as dup_file:
                dup_file.write('Date of file creation: {}\n'.format(a.format('DD-MM-YYYY')))
                for dup in duplicates:
                    dup_file.write(dup + '\n')

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

        path = os.path.join(settings.APP_DIR, 'merchants/mastercard', file_name)

        with open(path, 'w') as file:
            writer = csv.writer(file, delimiter=',', quotechar='"')

            input_file.set_header(writer)
            input_file.set_data(writer)
            input_file.set_trailer(writer)

    def export_merchants(self, merchants, validated, reason=None):
        """
        uses a given set of merchants to generate a file in Mastercard input file format
        :param merchants: a list of merchants to send to Mastercard
        :param validated:
        :param reason:
        :return: None
        """
        reason = reason or []

        file = MastercardMerchantFile()

        for count, merchant in enumerate(merchants):

            detail = [merchant['MasterCard MIDs'], merchant['Partner Name'], merchant['Town/City'],
                      merchant['Postcode'], merchant['Address (Building Name/Number, Street)'],
                      '', 'On-Board',
                      ]
            if validated:
                detail.append('')
            else:
                detail.append(reason[count])

            file.add_detail(detail)

        file_name = self.create_file_name(validated)
        try:
            self.write_to_file(file, file_name)
        except IOError:
            raise Exception('Error writing file:' + file_name)

    @staticmethod
    def create_file_name(validated):

        file_name = 'MAS_INPUT_BINK.csv'

        if not validated:
            file_name = 'INVALID_' + file_name

        return file_name
