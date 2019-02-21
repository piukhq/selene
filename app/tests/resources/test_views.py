from io import BytesIO

from flask import url_for
from flask_testing import TestCase
from unittest import mock

from app import create_app


class TestViews(TestCase):
    TESTING = True
    UPLOADED_FILES_DEST = 'test'

    def create_app(self):
        return create_app()

    def assert_flashes(self, expected_message, expected_category='message'):
        with self.client.session_transaction() as session:
            try:
                category, message = session['_flashes'][0]
            except KeyError:
                try:
                    message, category = self.flashed_messages[0]
                except KeyError:
                    raise AssertionError('nothing flashed')
            assert expected_message in message
            assert expected_category == category

    def test_index_get(self):
        response = self.client.get(url_for('selene.index'))

        self.assertEqual(response.status_code, 200)
        self.assert_template_used('index.html')
        self.assert_context("messages", None)

    def test_index_post(self):
        response = self.client.post(url_for('selene.index'))

        self.assertEqual(response.status_code, 302)
        self.assert_flashes('No file part', 'warning')

    def test_index_incorrect_file_type(self):
        filename = "some.jpeg"
        data = dict(
            input_file=(BytesIO(b'my file contents'), filename),
        )

        response = self.client.post(url_for('selene.index'), content_type='multipart/form-data', data=data)

        self.assertEqual(response.status_code, 200)
        self.assert_flashes('Incorrect File type. Please upload a csv.', 'warning')

    @mock.patch('app.views.process_mids_file')
    def test_file_upload_success(self, mock_process_mids_file):
        filename = "some.csv"
        data = dict(
            input_file=(BytesIO(b'my file contents'), filename),
        )

        response = self.client.post(url_for('selene.index'), content_type='multipart/form-data', data=data)

        self.assertTrue(mock_process_mids_file.called)
        self.assertEqual(response.status_code, 200)
        self.assert_flashes('File uploaded', 'success')

    @mock.patch('app.views.process_mids_file')
    def test_failed_mids_processing(self, mock_process_mids_file):
        mock_process_mids_file.side_effect = ValueError('Invalid headers or something')

        filename = "some.csv"
        data = dict(
            input_file=(BytesIO(b'my file contents'), filename),
        )

        response = self.client.post(url_for('selene.index'), content_type='multipart/form-data', data=data)

        self.assertTrue(mock_process_mids_file.called)
        self.assertEqual(response.status_code, 200)
        self.assert_flashes('Invalid headers or something', 'danger')

    def test_healthz(self):
        response = self.client.get(url_for('selene.healthz'))
        self.assertEqual(response.status_code, 200)
