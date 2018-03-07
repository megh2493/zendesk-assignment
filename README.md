# zendesk-assignment

## Requirements
* Python 3.5
* flask
* flask-login
* requests

## Installation
* <code> pip install -r requirements.txt </code>

## To run
* Edit the <code>config.py</code> file as required. By default the server runs on '127.0.0.1:5000'.
* <code> python run.py </code>
* This opens the link to the webpage in a tab on the default web browser.

## To run unit tests
* <code> python tests.py </code>

## How to use
* Provide credentials and appropriate domain name in the login page.
* Enter ticket id in the text box and hit the 'Search by ID' button to retrieve a particular ticket.
* Hit the 'View All' button to retrieve all the tickets in the account.
* Click on the desired ticket row to view description.
* You can click the back button on the page or 'Zendesk Ticket Viewer' on the top left corner of the page to navigate back to the home page.
* You can click the profile picture on the top right corner and select logout to logout.