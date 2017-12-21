import csv
import arrow
import os
import settings
import pysftp

from app.models import Sequence
from app.utils import get_attachment


def get_next_file_number():
    sequence = Sequence.query.filter(Sequence.scheme_provider == 'amex').first()

    # just for the first time the database is created.
    if not sequence:
        from app.models import db
        sequence = Sequence(scheme_provider='amex', type='ENROL', next_seq_number=1)
        db.session.add(sequence)
        db.session.commit()

    return sequence.get_seq_number()


def upload_sftp(url, username, password, src_dir, dst_dir):
    """
    Upload all the files in the source directory to the sftp location url in the destination directory
    with appropriate user credentials
    """
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    with pysftp.Connection(url, username=username, password=password, cnopts=cnopts) as sftp:
        path = os.path.join(settings.WRITE_FOLDER, 'merchants', 'amex', src_dir)
        src_path = get_attachment(path, 'amex')

        filename = src_path.split('/')[-1]
        dst_path = os.path.join(dst_dir, filename)
        sftp.put(src_path, dst_path)


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


class AmexMerchantFile:

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

    def get_detail(self):
        """
        freeze the current file contents into a string
        :return: a string representing the current state of the file
        """
        file_contents = [self.header_string]
        for detail in self.details:
            file_contents.append(detail['detail'])
        file_contents.append(self.footer_string)
        return '\n'.join(file_contents)

    def add_detail(self, detail):
        """
        add a detail record to the file
        :param detail: the detail to add
        :return: None
        """
        self.details.append({
            'detail': self._serialize(AmexDetail, detail),
        })


class Amex:

    @staticmethod
    def format_datetime(datetime):
        """
        formats an <arrow> datetime into the format expected by Amex
        :param datetime: the <arrow> datetime to be formatted
        :return: a datetime string in the format 'YYYYMMDD_hhmmss'
        """
        return datetime.format('MM/DD/YYYY')

    @staticmethod
    def has_mid(row):
        """
        return True if there is a visa mid in the row
        """

        selected = row.get('American Express MIDs')
        if selected and str(selected) != "" and str(selected) != "N/A":
            return True

        return False

    @staticmethod
    def write_transaction_matched_csv(merchants):
        a = arrow.utcnow()
        filename = 'cass_inp_amex_{}'.format(merchants[0]['Partner Name']) + '_{}'.format(a.timestamp) + '.csv'
        path = os.path.join(settings.WRITE_FOLDER, 'merchants', 'amex', filename)
        try:
            with open(path, 'w') as csv_file:
                csv_writer = csv.writer(csv_file, quoting=csv.QUOTE_NONE, escapechar='')
                for merchant in merchants:
                    csv_writer.writerow([
                        'amex',
                        merchant['American Express MIDs'].strip(' '),
                        merchant['Scheme'].strip('" ').lower(),
                        merchant['Partner Name'].strip('" '),
                        merchant['Town/City'].strip('" '),
                        merchant['Postcode'].strip('" '),
                    ])

        except IOError:
            raise Exception('Error writing file:' + path)

    @staticmethod
    def write_to_file(amex_input_file, file_name):
        """
        writes the given input file to a file under a given name.
        :param amex_input_file: the file to write
        :param file_name: the file name under which to write the data
        :return: None
        """

        path = os.path.join(settings.WRITE_FOLDER, 'merchants/amex', file_name)

        with open(path, 'w+') as f:
            f.write(amex_input_file.get_detail())

    def export_merchants(self, merchants, validated, reason=None):
        """
        uses a given set of merchants to generate a file in Amex input file format
        :param merchants: a list of merchants to send to Amex
        :param validated:
        :param reason:
        :return: None
        """
        reason = reason or []

        detail_record_count = len(merchants)
        file_num = get_next_file_number()

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

        file = AmexMerchantFile()
        file.set_header(header)
        file.set_footer(footer)

        for count, merchant in enumerate(merchants):
            if validated:
                the_reason = ''

            else:
                the_reason = reason[count]

            file.add_detail(AmexDetail(
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
                filler=the_reason
            ))

        file_name = self.create_file_name(validated)
        try:
            self.write_to_file(file, file_name)

        except IOError:
            raise Exception('Error writing file:' + file_name)

    @staticmethod
    def create_file_name(validated):
        # e.g. <Prtr>_AXP_mer_reg_yymmdd_hhmmss.txt
        file_name = '{company}_AXP_MER_REG_{datetime}.txt'.format(
            company='CHINGS',
            datetime=arrow.now().format('YYYYMMDD_hhmmss')
        )

        if not validated:
            file_name = 'INVALID_' + file_name

        return file_name
