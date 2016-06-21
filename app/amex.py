import arrow
import os
import settings
from app.csvfile import CSVReader


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


class Detail(Field):
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


class AmexMerchantFile(object):

    def __init__(self):
        self.header_string = ''
        self.details = []
        self.footer_string = ''

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

    def add_detail(self, detail):
        """
        add a detail record to the file
        :param detail: the detail to add
        :return: None
        """
        self.details.append({
            'detail': self._serialize(Detail, detail),
        })

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


class Amex(object):
    delimiter = ','
    column_names = ['Location Name', 'Partner Name', 'American Express', 'MasterCard', 'Visa', 'Currency',
                    'Building Name Number', 'Postcode', 'Street', 'Local Area Name', 'TownCity', 'CountyState',
                    'Country', 'Longitude', 'Latitude'
                    ]
    column_keep = {'Location Name', 'Partner Name', 'American Express', 'MasterCard', 'Visa', 'Currency',
                   'Building Name Number', 'Postcode', 'Street', 'Local Area Name', 'TownCity', 'CountyState',
                   'Country', 'Longitude', 'Latitude'
                   }

    @staticmethod
    def format_datetime(datetime):
        """
        formats an <arrow> datetime into the format expected by Amex
        :param datetime: the <arrow> datetime to be formatted
        :return: a datetime string in the format 'MM-DD-YYYY'
        """
        return datetime.format('YYYY-MM-DD')

    @staticmethod
    def write_to_file(amex_input_file, file_name):
        """
        writes the given input file to a file under a given name.
        :param amex_input_file: the file to write
        :param file_name: the file name under which to write the data
        :return: None
        """
        path = os.path.join(settings.APP_DIR, 'merchants/amex', file_name)

        with open(path, 'w+') as f:
            f.write(amex_input_file.freeze())

    def export_merchants(self, merchants):
        """
        uses a given set of merchants to generate a file in Amex input file format
        :param merchants: a list of merchants to send to Amex
        :return: None
        """
        detail_record_count = len(merchants)

        header = Header(
            date=self.format_datetime(arrow.now()),
            sequence_number='0000000001',
            from_to='P2A',
            file_type='10',
            file_description='Merchant Registration',
            partner_id='bink_pid',
            filler=''
        )

        footer = Footer(
            file_type='10',
            trailer_count=str(detail_record_count).rjust(12, '0'),
            filler=''
        )

        file = AmexMerchantFile()
        file.set_header(header)
        file.set_footer(footer)
        column_keep = {'Location Name', 'Partner Name', 'American Express', 'MasterCard', 'Visa', 'Currency',
                       'Building Name Number', 'Postcode', 'Street', 'Local Area Name', 'TownCity', 'CountyState',
                       'Country', 'Longitude', 'Latitude'
                       }

        for merchant in merchants:
            file.add_detail(
                Detail(
                    action_code='A',  # A=Add, U=Update, D=Delete
                    partner_id='AADP0050',
                    version_number='1.0',
                    seller_id='TBD',
                    tpa_se='TBD',
                    merchant_number=merchant['American Express'],
                    offer_id='900000000',
                    offer_name='',
                    offer_start_date=self.format_datetime(arrow.now()),
                    offer_end_date=self.format_datetime(arrow.now()),
                    source_system_id='GBP',
                    merchant_dba_name=merchant['Partner Name'],
                    merchant_legal_name=merchant['Partner Name'],
                    merchant_start_date=self.format_datetime(arrow.now()),
                    merchant_end_date='',
                    address_line_1='{0} {1}'.format(merchant['Building Name Number'], merchant['Street']),
                    address_line_2=merchant['Local Area Name'],
                    address_line_3='',
                    address_line_4='',
                    address_line_5='',
                    city=merchant['TownCity'],
                    state=merchant['CountyState'],
                    postal_code=merchant['Postcode'],
                    country=merchant['Country'],
                    geographical_code_latitude=merchant['Latitude'],
                    geographical_code_longitude=merchant['Longitude'],
                    custom_field_1='',
                    custom_field_2='',
                    filler=''
                ),
            )

        # e.g. <Prtr>_AXP_mer_reg_yymmdd_hhmmss.txt
        file_name = '{}{}{}'.format(
            'BINK',
            '_AXP_mer_reg_',
            self.format_datetime(arrow.now()),
        )

        self.write_to_file(file, file_name)

    def export(self, merchant):
        files = fetch_files(merchant, 'csv')
        start_line = 2
        reader = CSVReader(self.column_names, self.delimiter, self.column_keep)

        for txt_file in files:
            current_line = 0
            merchant_list = []

            for row in reader(txt_file):
                current_line += 1

                if current_line >= start_line:
                    merchant_list.append(row)

        self.export_merchants(merchant_list)


def fetch_files(merchant, file_extension):
    file_path = os.path.join(settings.APP_DIR + '/merchants',
                             merchant)
    merchant_files = file_list(file_path, file_extension)
    return merchant_files


def file_list(file_path, file_ext):
    if not os.path.isdir(file_path):
        return []
    return [os.path.join(file_path, fn) for fn in next(os.walk(file_path))[2] if fn.endswith(file_ext)]
