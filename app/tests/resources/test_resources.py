import json
from flask_testing import TestCase

from app import create_app
from app.utils import csv_to_list_json
from settings import APP_DIR


class TestViews(TestCase):
    def create_app(self):
        return create_app(self, )

    def test_import_mids(self):
        response = self.client.post("/mids/import_mids", data="test wrong content", content_type="application/json")
        self.assertEqual(response.status_code, 500)

        file = csv_to_list_json(APP_DIR + "/app/tests/fixture/test_import_mids.csv")
        response = self.client.post("/mids/import_mids", data=json.dumps(file), content_type="application/json")

        self.assertEqual(response.status_code, 200)

    def test_mastercard_handback(self):
        response = self.client.post("/mids/mastercard_handback", data="test wrong content",
                                    content_type="application/json")
        self.assertEqual(response.status_code, 500)

        file = csv_to_list_json(APP_DIR + "/app/tests/fixture/test_handback.csv")
        response = self.client.post("/mids/mastercard_handback", data=json.dumps(file), content_type="application/json")

        self.assertEqual(response.status_code, 200)

    def test_handback_duplicates(self):
        response = self.client.post("/mids/handback_duplicates", data="", content_type="application/json")
        self.assertEqual(response.status_code, 200)
