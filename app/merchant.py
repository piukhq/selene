import arrow
import os
import settings

from bigdatalib.schema import Schema
from cassandralib.client import Client
from openpyxl import Workbook

from app.csvfile import CSVReader
from app.utils import validate_uk_postcode

class Field(object):
    def __init__(self, **kwargs):
        if 'record_identifier' in kwargs:
            raise TypeError('you may not specify record_identifier in kwargs')
        for k, v in kwargs.items():
            setattr(self, k, v)


class Header(Field):
    fields = [
        ('record_identifier', 1),
        ('date', 10),
        ('sequence_number', 10),
        ('from_to', 3),
        ('file_type', 2),
        ('file_description', 27),
        ('partner_id', 8),
        ('filler', 932)
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.record_identifier = 'H'


class AmexDetail(Field):
    fields = [
        ('record_identifier', 1),
        ('action_code', 1),
        ('partner_id', 8),
        ('version_number', 3),
        ('seller_id', 30),
        ('tpa_se', 15),
        ('merchant_number', 15),
        ('offer_id', 9),
        ('offer_name', 80),
        ('offer_start_date', 10),
        ('offer_end_date', 10),
        ('source_system_id', 3),
        ('merchant_dba_name', 38),
        ('merchant_legal_name', 38),
        ('merchant_start_date', 10),
        ('merchant_end_date', 10),
        ('address_line_1', 40),
        ('address_line_2', 40),
        ('address_line_3', 40),
        ('address_line_4', 40),
        ('address_line_5', 40),
        ('city', 35),
        ('state', 6),
        ('postal_code', 15),
        ('country', 3),
        ('geographical_code_latitude', 20),
        ('geographical_code_longitude', 20),
        ('custom_field_1', 20),
        ('custom_field_2', 20),
        ('filler', 351),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.record_identifier = 'D'


class Footer(Field):
    fields = [
        ('record_identifier', 1),
        ('file_type', 2),
        ('trailer_count', 12),
        ('filler', 982),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.record_identifier = 'T'


class MerchantFile(object):

    def __init__(self):
        self.header_string = ''
        self.details = []
        self.footer_string = ''
        self.visa_lines = []

    @staticmethod
    def _serialize(field_class, fields):
        """
        turns a given field into a string using field_class to choose the fields
        :param field_class: a class deriving from Field
        :param fields: an instance of field_class
        :return: the serialized string
        """
        data = []
        for field, length in field_class.fields:
            data.append(str(getattr(fields, field)).ljust(length))
        return '|'.join(data)

    def set_header(self, header):
        """
        set the header record for the file
        :param header: the header to use
        :return: None
        """
        self.header_string = self._serialize(Header, header)

    def set_footer(self, footer):
        """
        set the footer record for the file
        :param footer: the footer to use
        :return: None
        """
        self.footer_string = self._serialize(Footer, footer)

    def add_amex_detail(self, detail):
        """
        add a detail record to the file
        :param detail: the detail to add
        :return: None
        """
        self.details.append({
            'detail': self._serialize(AmexDetail, detail),
        })

    def add_visa_detail(self, detail):
        """Add a detail record for a line in the visa output file
        :param detail: the detail to add
        :return: None
        """
        self.visa_lines.append(detail)

    def freeze(self):
        """
        freeze the current file contents into a string
        :return: a string representing the current state of the file
        """
        file_contents = [self.header_string]
        for detail in self.details:
            file_contents.append(detail['detail'])
        file_contents.append(self.footer_string)
        return '\n'.join(file_contents)

    def get_visa_lines(self):
        """Retrieve a list of lines of visa data"""
        return self.visa_lines


class PaymentCard(object):
    delimiter = ','
    column_names = ['Partner Name', 'American Express MIDs', 'MasterCard MIDs', 'Visa MIDs',
                    'Address (Building Name/Number, Street)', 'Postcode', 'Town/City', 'County/State',
                    'Country', 'Action',
                    ]

    column_keep = {'Partner Name', 'American Express MIDs', 'MasterCard MIDs', 'Visa MIDs',
                   'Address (Building Name/Number, Street)', 'Postcode', 'Town/City', 'County/State',
                   'Country', 'Action',
                   }

    @staticmethod
    def format_datetime(datetime):
        """
        formats an <arrow> datetime into the format expected by Amex
        :param datetime: the <arrow> datetime to be formatted
        :return: a datetime string in the format 'YYYYMMDD_hhmmss'
        """
        return datetime.format('MM/DD/YYYY')

    @staticmethod
    def write_to_file(input_file, file_name, provider_type):
        """
        writes the given input file to a file under a given name.
        :param amex_input_file: the file to write
        :param file_name: the file name under which to write the data
        :return: None
        """

        path = os.path.join(settings.APP_DIR, 'merchants/{0}'.format(provider_type), file_name)

        if provider_type == 'amex':
            with open(path, 'w+') as f:
                f.write(input_file.freeze())
        elif provider_type == 'visa':
            wb = Workbook()
            ws1 = wb.active
            ws1.title = "PVnnn_90523_Choice_20160101"

            visa_header = ['GLB_MID', 'ACQUIRER_MID', 'GLB_MERCHANT_NAME', 'MERCHANT_CITY', 'POST_CODE', 'ADDRESS',
                           'ALTERNATIVE_MERCHANT_NAME', 'STATUS', 'VISA_COMMENTS', 'MSG_COMMENTS'
                           ]
            ws1.append(visa_header)
            visa_lines = input_file.get_visa_lines()
            for line in visa_lines:
                ws1.append(line)

            wb.save(path)

    def export_merchants(self, merchants, validated, provider_type):
        """
        uses a given set of merchants to generate a file in Amex input file format
        :param merchants: a list of merchants to send to Amex
        :return: None
        """
        detail_record_count = len(merchants)
        file_num = 1#sequential_file_number() + 1

        header = Header(
            date=self.format_datetime(arrow.now()),
            sequence_number=str(file_num).rjust(10, '0'),
            from_to='P2A',
            file_type='10',
            file_description='Merchant Registration',
            partner_id='AADP0050',
            filler=''
        )

        footer = Footer(
            file_type='10',
            trailer_count=str(detail_record_count).rjust(12, '0'),
            filler=''
        )

        file = MerchantFile()
        file.set_header(header)
        file.set_footer(footer)

        for merchant in merchants:
            if provider_type == 'amex':
                detail = AmexDetail(
                    action_code=merchant['Action'],  # A=Add, U=Update, D=Delete
                    partner_id='AADP0050',
                    version_number='1.0',
                    seller_id='',
                    tpa_se='',
                    merchant_number=merchant['American Express MIDs'],
                    offer_id='0',
                    offer_name='',
                    offer_start_date='',
                    offer_end_date='',
                    source_system_id='GEN',
                    merchant_dba_name=merchant['Partner Name'],
                    merchant_legal_name=merchant['Partner Name'],
                    merchant_start_date=self.format_datetime(arrow.now()),
                    merchant_end_date='',
                    address_line_1='{}'.format(merchant['Address (Building Name/Number, Street)']),
                    address_line_2='',
                    address_line_3='',
                    address_line_4='',
                    address_line_5='',
                    city=merchant['Town/City'],
                    state=merchant['County/State'],
                    postal_code=merchant['Postcode'],
                    country=merchant['Country'],
                    geographical_code_latitude='',
                    geographical_code_longitude='',
                    custom_field_1='',
                    custom_field_2='',
                    filler=''
                )

                file.add_amex_detail(detail)

            elif provider_type == 'visa':
                detail = ['90523', merchant['Visa MIDs'], merchant['Partner Name'], merchant['Town/City'], merchant['Postcode'],
                               merchant['Address (Building Name/Number, Street)'], '', 'New', '', '',
                               ]
                file.add_visa_detail(detail)

            elif provider_type == 'mastercard':
                mids = merchant['MasterCard MIDs']

        file_name = self.create_file_name(validated, provider_type)
        try:
            self.write_to_file(file, file_name, provider_type)
            status = 'written'
        except IOError as err:
            status = 'error'
            raise Exception('Error writing file:' + file_name)

        log = {
            'provider': 'bink',
            'receiver': provider_type,
            'file_name': file_name,
            'date': arrow.now(),
            'process_date': arrow.now(),
            'status': status,
            'file_type': 'out',
            'direction': 'out',
            'sequence_number': file_num,
            'comment': 'Merchant onboarding'
        }
        #insert_file_log(log)

    def export(self, provider_type):
        files = fetch_files(provider_type, 'csv')
        start_line = 2
        reader = CSVReader(self.column_names, self.delimiter, self.column_keep)

        merchant_list = []
        bad_merchant_list = []

        for txt_file in files:
            current_line = 0

            for row in reader(txt_file):
                current_line += 1

                if current_line >= start_line:
                    if validate_row_data(row, provider_type):
                        merchant_list.append(row)
                    else:
                        bad_merchant_list.append(row)

        self.export_merchants(merchant_list, True, provider_type)
        self.export_merchants(bad_merchant_list, False, provider_type)


    def create_file_name(self, validated, provider_type):
        # e.g. <Prtr>_AXP_mer_reg_yymmdd_hhmmss.txt
        file_name = ''

        if provider_type == 'amex':
            file_name = '{}{}{}{}'.format(
                'BINK',
                '_AXP_MER_REG_',
                arrow.now().format('YYYYMMDD_hhmmss'),
                '.txt'
            )
        elif provider_type == 'visa':
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
        elif provider_type == 'mastercard':
            pass

        if not validated:
            file_name = 'INVALID_' + file_name

        return file_name


def validate_row_data(row, merchant):
    """Validate data within a row from the csv file"""

    if row['Postcode'] != '':
        if not validate_uk_postcode(row['Postcode']):
            print("postcode fail", row['Postcode'])
            return False

    if row['Partner Name'] == '' or \
        row['Address (Building Name/Number, Street)'] == '' or \
        row['Town/City'] == '' or \
        row['Country'] == '' or \
        row['Action'] == '':
        return False

    if merchant == 'amex':
        if row['American Express MIDs'] == '':
            return False
    elif merchant == 'visa':
        if row['Visa MIDs'] == '':
            return False
    elif merchant == 'mastercard':
        if row['MasterCard MIDs'] == '':
            return False

    return True


def fetch_files(merchant, file_extension):
    file_path = os.path.join(settings.APP_DIR + '/merchants',
                             merchant)
    merchant_files = file_list(file_path, file_extension)
    return merchant_files


def file_list(file_path, file_ext):
    if not os.path.isdir(file_path):
        return []
    return [os.path.join(file_path, fn) for fn in next(os.walk(file_path))[2] if fn.endswith(file_ext)]


def sequential_file_number():
    db_client = Client(schema=Schema, hosts=settings.CASSANDRA_CLUSTER)
    # Get the currently logged files. This could be just the last file logged.
    # If returns nothing, then must be first file, so need to create the name.
    logged_files = db_client.select('file_logging', provider='amex', file_type='out')

    db_client.close()
    return len(logged_files.current_rows)


def insert_file_log(log):
    db_client = Client(schema=Schema, hosts=settings.CASSANDRA_CLUSTER)
    # Get the currently logged files. This could be just the last file logged.
    # If returns nothing, then must be first file, so need to create the name.
    db_client.insert('file_logging', [log])

    db_client.close()
