import json
from flask_testing import TestCase

from app import create_app
from app.utils import csv_to_weird_json, list_json_to_dict_json
from settings import APP_DIR


class TestViews(TestCase):
    def create_app(self):
        return create_app(self, )

    def test_import_mids(self):
        file = csv_to_weird_json(APP_DIR + "/app/tests/unit/fixture/test_data.csv")

        response = self.client.post("/import_mids", data=json.dumps(file), content_type="application/json")
        file = list_json_to_dict_json(file)
        self.assertEqual(response.json.get('processed_file'), file)
