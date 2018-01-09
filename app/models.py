import arrow

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Sequence(db.Model):
    __tablename__ = 'sequence_numbers'
    id = db.Column(db.Integer(), primary_key=True)
    scheme_provider = db.Column(db.String())
    type = db.Column(db.String())
    next_seq_number = db.Column(db.Integer())
    sequence_date = db.Column(db.Date(), onupdate=arrow.utcnow().date())

    def to_dict(self):
        return {
            'scheme_provider': self.scheme_provider,
            'type': self.type,
            'next_seq_number': self.next_seq_number,
            'sequence_date': arrow.get(self.sequence_date).format("DD MMM YYYY")
        }

    def get_seq_number(self):
        return self.next_seq_number
