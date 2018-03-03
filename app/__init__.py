from flask import Flask
from flask_login import LoginManager

app = Flask(__name__)
app.config.from_pyfile('config.py')
lm = LoginManager(app)
lm.login_view = 'login'

from . import views, models