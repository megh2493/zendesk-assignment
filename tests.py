import unittest

from unittest.mock import patch

from app import app


# unit tests with api end points mocked to simulate situations
class TestCase(unittest.TestCase):
    def setUp(self):
        app.testing = True
        self.app = app.test_client()

    def post(self, path, data=None):
        return self.app.post(path, data=data, follow_redirects=True)

    def get(self, path, data=None):
        return self.app.get(path, query_string=data, follow_redirects=True)

    # tests successful login and logout
    @patch('app.models.requests.Session.get')
    def test_login_logout(self, mock_get):
        json_data = {'user': {'id': 10, 'name': 'Alice', 'photo': {
            'thumbnails': {'content_url': 'https://dummyurl.com/dummycontent.png'}}}}
        mock_get.return_value.json = lambda: json_data
        mock_get.return_value.status_code = 200
        r = self.post('/login', dict(email='alice@abc.com', password='password', domain='abc'))

        self.assertEqual(r.status_code, 200)

        r = self.get('/logout')

        self.assertNotIn(b'id="user-dropdown"', r.data)

    # tests login with invalid credentials
    @patch('app.models.requests.Session.get')
    def test_invalid_credentials(self, mock_get):
        json_data = {'user': {'id': None}}
        mock_get.return_value.json = lambda: json_data
        mock_get.return_value.status_code = 200
        r = self.post('/login', dict(email='alice@abc.com', password='password', domain='abc'))

        self.assertEqual(r.status_code, 401)
        self.assertIn(b'*Invalid Credentials', r.data)

    # test login with invalid zendesk domain
    @patch('app.models.requests.Session.get')
    def test_invalid_domain(self, mock_get):
        mock_get.return_value.status_code = 404
        r = self.post('/login', dict(email='alice@abc.com', password='password', domain='abc'))

        self.assertEqual(r.status_code, 404)
        self.assertIn(b'*Invalid Domain', r.data)

    # tests for api being unavailable
    @patch('app.models.requests.Session.get')
    def test_api_unavailable(self, mock_get):
        mock_get.return_value.status_code = 503
        r = self.post('/login', dict(email='alice@abc.com', password='password', domain='abc'))

        self.assertGreaterEqual(r.status_code, 500)
        self.assertIn(b'Sorry, the API is unavailable.', r.data)

    # tests for successful search of ticket by ID
    @patch('app.models.requests.Session.get')
    def test_search_ticket(self, mock_get):
        json_data = {'user': {'id': 10, 'name': 'Alice', 'photo': {
            'thumbnails': {'content_url': 'https://dummyurl.com/dummycontent.png'}}}}
        mock_get.return_value.json = lambda: json_data
        mock_get.return_value.status_code = 200
        self.post('/login', dict(email='alice@abc.com', password='password', domain='abc'))
        json_data = {'users': [{'id': 10, 'name': 'Alice'}],
                     'ticket': {'id': 1, 'subject': 'Dummy Ticket', 'requester_id': 10,
                                'created_at': '1990-01-01T00:00:00Z', 'description': 'Dummy description',
                                'status': 'open'}}
        mock_get.return_value.json = lambda: json_data
        mock_get.return_value.status_code = 200
        r = self.get('/search', dict(id=1))

        self.assertEqual(r.status_code, 200)
        self.assertIn(b'Dummy Ticket', r.data)

    # tests for search of ticket for invalid ticket ID
    @patch('app.models.requests.Session.get')
    def test_search_ticket_not_exists(self, mock_get):
        json_data = {'user': {'id': 10, 'name': 'Alice', 'photo': {
            'thumbnails': {'content_url': 'https://dummyurl.com/dummycontent.png'}}}}
        mock_get.return_value.json = lambda: json_data
        mock_get.return_value.status_code = 200
        self.post('/login', dict(email='alice@abc.com', password='password', domain='abc'))
        mock_get.return_value.status_code = 404
        r = self.get('/search', dict(id=100))

        self.assertEqual(r.status_code, 404)
        self.assertIn(b'The Ticket ID specified was not found.', r.data)

    # tests for successful retrieval of all tickets in the account
    @patch('app.models.requests.Session.get')
    def test_all_tickets(self, mock_get):
        json_data = {'user': {'id': 10, 'name': 'Alice', 'photo': {
            'thumbnails': {'content_url': 'https://dummyurl.com/dummycontent.png'}}}}
        mock_get.return_value.json = lambda: json_data
        mock_get.return_value.status_code = 200
        self.post('/login', dict(email='alice@abc.com', password='password', domain='abc'))
        json_data = {'users': [{'id': 10, 'name': 'Alice'}],
                     'tickets': [{'id': 1, 'subject': 'Dummy Ticket 1', 'requester_id': 10,
                                  'created_at': '1990-01-01T00:00:00Z', 'description': 'Dummy description',
                                  'status': 'open'},
                                 {'id': 2, 'subject': 'Dummy Ticket 2', 'requester_id': 10,
                                  'created_at': '1990-01-01T00:00:01Z', 'description': 'Dummy Description',
                                  'status': 'pending'}],
                     'next_page': None}
        mock_get.return_value.json = lambda: json_data
        mock_get.return_value.status_code = 200
        r = self.get('/tickets')

        self.assertEqual(r.status_code, 200)
        self.assertIn(b'Dummy Ticket 1', r.data)
        self.assertIn(b'Dummy Ticket 2', r.data)


if __name__ == '__main__':
    unittest.main()
