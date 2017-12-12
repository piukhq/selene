import os
import json
from flask_testing import TestCase

from app import create_app
from app.utils import csv_to_json


class TestViews(TestCase):
    def create_app(self):
        return create_app(self, )

    def test_import_mids(self):
        file = csv_to_json(os.getcwd() + "/fixture/test_data.csv")

        response = self.client.post("/test", data=file, content_type="application/json")
        self.assertEqual(response.json.get('processed_file'), file)
