from app.agents.base import BaseProvider


class Amex(BaseProvider):
    name = 'Amex'
    col_name = 'American Express MIDs'

    def export(self):
        pass
