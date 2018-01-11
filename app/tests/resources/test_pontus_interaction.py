from flask_testing import TestCase

from app import create_app
from app.models import Sequence, db
from app.utils import update_amex_sequence_number
from app.agents.amex import get_next_file_number


class TestPontus(TestCase):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    def create_app(self):
        return create_app(self, )

    def setUp(self):
        db.create_all()
        new = Sequence(scheme_provider='amex', type='TEST', next_seq_number=1)
        db.session.add(new)
        db.session.commit()

    def test_get_next_file_number(self):
        self.assertEqual(get_next_file_number(), 1)

    def test_update_amex_sequence_number(self):
        sequence = Sequence.query.first()
        self.assertEqual(sequence.to_dict()['next_seq_number'], 1)

        update_amex_sequence_number()
        db.session.refresh(sequence)
        self.assertEqual(sequence.to_dict()['next_seq_number'], 2)
