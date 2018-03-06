import unittest

from app import app


class TestCase(unittest.TestCase):

    def setUp(self):
        app.testing = True
        self.app = app.test_client()

    def login(self, email, password, domain):
        return self.app.post('/login', data=dict(
            email=email,
            password=password,
            domain=domain
        ), follow_redirects=True)

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)

    def fetch_page(self, path):
        return self.app.get(path, follow_redirects=True)

    def test_login_logout(self):
        r = self.login('mmadhusu@usc.edu', 'megh64742', 'uscsupport')
        if r.status_code < 500:
            assert r.status_code == 200

        r = self.logout()
        assert b'id="user-dropdown"' not in r.data

        r = self.login('admin', 'default', 'uscsupport')
        if r.status_code < 500:
            assert r.status_code == 401

        r = self.login('mmadhusu@usc.edu', 'megh64742', 'uscupport')
        if r.status_code < 500:
            assert r.status_code == 404

    def test_api_availability(self):
        r = self.login('mmadhusu@usc.edu', 'megh64742', 'uscsupport')
        if r.status_code == 200:
            assert b'id="user-dropdown"' in r.data

        elif r.status_code >= 500:
            assert b'Sorry, the API is unavailable.' in r.data


if __name__ == '__main__':
    unittest.main()
