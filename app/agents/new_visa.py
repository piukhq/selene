from app.agents.base import BaseProvider


class Visa(BaseProvider):
    name = 'Visa'
    col_name = 'Visa MIDs'

    def export(self):
        pass
