from app.agents.base import BaseProvider


class MasterCard(BaseProvider):
    name = 'MasterCard'
    col_name = 'MasterCard MIDs'

    def export(self):
        pass
