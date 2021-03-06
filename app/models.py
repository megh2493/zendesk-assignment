import requests
import requests.compat


# creates a zendesk session for the user
def get_zendesk_session(email, password):
    session = requests.Session()
    session.auth = (email, password)
    return session


# model to store user details
class User:
    def __init__(self, domain):
        self.domain = domain
        self.displayname = None
        self.id = None
        self.session = None
        self.img = None

    def __del__(self):
        self.session.close()

    # verify login credentials and update user details
    def login(self, email, password):
        self.session = get_zendesk_session(email, password)
        r = self.session.get(requests.compat.urljoin(self.domain, '/api/v2/users/me.json'))
        if r.status_code == 200:
            data = r.json()
            if data['user']['id']:
                self.id = data['user']['id']
                self.displayname = data['user']['name']
                if data['user']['photo']:
                    self.img = data['user']['photo']['thumbnails']['content_url']

            else:
                return 401

        return r.status_code

    @staticmethod
    def is_authenticated():
        return True

    @staticmethod
    def is_active():
        return True

    @staticmethod
    def is_anonymous():
        return False

    def get_id(self):
        return self.id

    def __repr__(self):
        return '<User %r>' % self.id



