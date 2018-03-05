import requests.compat

from datetime import datetime
from flask import render_template, g, redirect, url_for, request
from flask_login import login_required, login_user, logout_user, current_user

from app import app, lm
from .models import User

users = dict()


@app.before_request
def before_request():
    g.user = current_user


@lm.user_loader
def load_user(userid):
    return users.get(int(userid))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if hasattr(g.user, 'id') and g.user.is_authenticated():
        return redirect(url_for('index'))

    if request.method == 'POST':
        user = User('https://' + request.form['domain'] + '.zendesk.com')
        success = user.login(request.form['email'], request.form['password'])

        if success:
            login_user(user)
            users[user.id] = user
            return redirect(request.form.get('next') or url_for('index'))

        else:
            return render_template('login.html', invalid="*Invalid Credentials/Domain",
                                   next=request.form.get('next'))

    else:
        return render_template('login.html', next=request.args.get('next'))


@app.route('/')
@login_required
def index():
    return render_template('index.html', user=g.user)


@app.route('/tickets')
@login_required
def get_tickets():
    tickets = list()
    url = requests.compat.urljoin(g.user.domain, '/api/v2/tickets.json?include=users')

    while url:
        users_list = dict()
        r = g.user.session.get(url)

        if r.status_code >= 500:
            return render_template('error.html', user=g.user, error='Sorry, the API is unavailable.'), r.status_code

        data = r.json()

        for i in data['users']:
            users_list[i['id']] = i['name']

        for i in data['tickets']:
            tickets.append({'id': i['id'], 'subject': i['subject'], 'requester': users_list[i['requester_id']],
                            'created': datetime.strptime(i['created_at'], '%Y-%m-%dT%H:%M:%SZ').strftime(
                                '%d %b %Y %I:%M %p'), 'description': i['description']})

        url = data['next_page'] + '&include=users' if data['next_page'] else data['next_page']

    return render_template('tickets.html', user=g.user, tickets=tickets)


@app.route('/search')
@login_required
def get_ticket():
    tickets = list()
    url = requests.compat.urljoin(g.user.domain, '/api/v2/tickets/%s.json?include=users' % request.args['id'])

    users_list = dict()
    r = g.user.session.get(url)
    if r.status_code == 404:
        return render_template('error.html', user=g.user, error='The Ticket ID specified was not found.'), 404

    elif r.status_code >= 500:
        return render_template('error.html', user=g.user, error='Sorry, the API is unavailable.'), r.status_code

    data = r.json()

    for i in data['users']:
        users_list[i['id']] = i['name']

    tickets.append({'id': data['ticket']['id'], 'subject': data['ticket']['subject'],
                    'requester': users_list[data['ticket']['requester_id']],
                    'created': datetime.strptime(data['ticket']['created_at'], '%Y-%m-%dT%H:%M:%SZ').strftime(
                        '%d %b %Y %I:%M %p'), 'description': data['ticket']['description']})

    return render_template('tickets.html', user=g.user, tickets=tickets)


@app.route('/logout')
@login_required
def logout():
    del users[g.user.id]
    logout_user()
    return redirect(url_for('login'))
