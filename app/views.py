import requests.compat

from datetime import datetime
from flask import render_template, g, redirect, url_for, request
from flask_login import login_required, login_user, logout_user, current_user

from app import app, lm
from .models import User

users = dict()
status_mappings = {'new': ['warning', 'n'], 'open': ['danger', 'o'], 'pending': ['info', 'p'],
                   'closed': ['light', 'c'], 'solved': ['secondary', 's'], 'hold': ['dark', 'h']}


@app.before_request
def before_request():
    g.user = current_user


@lm.user_loader
def load_user(userid):
    return users.get(int(userid))


# login and load user details
@app.route('/login', methods=['GET', 'POST'])
def login():
    if hasattr(g.user, 'id') and g.user.is_authenticated():
        return redirect(url_for('index'))

    if request.method == 'POST':
        domain = request.form.get('domain')
        if domain:
            user = User('https://' + request.form['domain'] + '.zendesk.com')
            status = user.login(request.form.get('email', ''), request.form.get('password', ''))

        else:
            status = 404

        if status == 200:
            login_user(user)
            users[user.id] = user
            return redirect(request.form.get('next') or url_for('index'))

        elif status == 401:
            return render_template('login.html', invalid="*Invalid Credentials",
                                   next=request.form.get('next')), status

        elif status == 404:
            return render_template('login.html', invalid="*Invalid Domain",
                                   next=request.form.get('next')), status

        elif status >= 500:
            return render_template('error.html', error='Sorry, the API is unavailable.'), status

    else:
        return render_template('login.html', next=request.args.get('next'))


# renders the home page
@app.route('/')
@login_required
def index():
    return render_template('index.html', user=g.user)


# fetches all tickets for the account and renders it in a HTML table
@app.route('/tickets')
@login_required
def get_tickets():
    tickets = list()
    url = requests.compat.urljoin(g.user.domain, '/api/v2/tickets.json?include=users')
    counter = 0
    page = list()

    while url:
        users_list = dict()
        r = g.user.session.get(url)

        if r.status_code >= 500:
            return render_template('error.html', user=g.user, error='Sorry, the API is unavailable.'), r.status_code

        data = r.json()

        for i in data['users']:
            users_list[i['id']] = i['name']

        for i in data['tickets']:
            page.append({'id': i['id'], 'subject': i['subject'], 'requester': users_list[i['requester_id']],
                         'created': datetime.strptime(i['created_at'], '%Y-%m-%dT%H:%M:%SZ').strftime(
                             '%d %b %Y %I:%M %p'), 'description': i['description'], 'status': i['status']})
            counter += 1

            if counter % 20 == 0:
                tickets.append(page)
                page = list()

        url = data['next_page'] + '&include=users' if data['next_page'] else data['next_page']

    if page:
        tickets.append(page)

    return render_template('tickets.html', user=g.user, tickets=tickets, status_mappings=status_mappings, search=False)


# fetches ticket by ID specified and renders it in a HTML table
@app.route('/search')
@login_required
def get_ticket():
    tickets = list([list()])
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

    tickets[0].append({'id': data['ticket']['id'], 'subject': data['ticket']['subject'],
                       'requester': users_list[data['ticket']['requester_id']],
                       'created': datetime.strptime(data['ticket']['created_at'], '%Y-%m-%dT%H:%M:%SZ').strftime(
                           '%d %b %Y %I:%M %p'), 'description': data['ticket']['description'],
                       'status': data['ticket']['status']})

    return render_template('tickets.html', user=g.user, tickets=tickets, status_mappings=status_mappings, search=True)


# logs out the user
@app.route('/logout')
@login_required
def logout():
    users.pop(g.user.id)
    logout_user()
    return redirect(url_for('login'))


# custom HTML for page not found error
@app.errorhandler(404)
def not_found(e):
    if hasattr(g.user, 'id') and g.user.is_authenticated():
        return render_template('error.html', user=g.user, error='This page does not exist.'), 404

    return render_template('error.html', error='This page does not exist.'), 404


# custom HTML for internal server error
@app.errorhandler(500)
def server_error(e):
    if hasattr(g.user, 'id') and g.user.is_authenticated():
        return render_template('error.html', user=g.user, error='Oops, something went wrong.'), 500

    return render_template('error.html', error='Oops, something went wrong.'), 500
