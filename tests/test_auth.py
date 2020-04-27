import pytest
from flask import g, session
from unishare.database import *
from werkzeug.security import check_password_hash, generate_password_hash

def test_register(client, app):
    assert client.get('/auth/register').status_code == 200
    response = client.post(
        'auth/register',
        data = {'username': 'a', 'password': 'abcd1234'}
    )
    assert response.headers['Location'] == 'http://localhost/'
    
    with app.app_context():
        assert User.query.filter_by(username='a').first() is not None

@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('', '', b'Username is required.'),
    ('a', '', b'Password is required.'),
    ('b b', 'a', b'Username cannot contain spaces.'),
    ('a', 'b b', b'Password cannot contain spaces'),
    ('/b', 'a', b'Username can only contain alphanumeric characters (letters A-Z, numbers 0-9) and underscores.'),
    ('aaaaaaaaaaaaaaaa', 'b', b'Username cannot be longer than 15 characters.'),
    ('a', 'b', b'Password must be atleast 8 characters long.'),
    ('test1', 'test1234', b'test1 is already registered.')
))
def test_register_validate_input(client, username, password, message):
    response = client.post(
        '/auth/register',
        data = {'username': username, 'password': password}
    )
    assert message in response.data

def test_login(client, auth, app):
    response = auth.login()
    assert response.headers['Location'] == 'http://localhost/'

    with client:
        client.get('/')
        assert session['user_id'] == 1
        assert g.user.username == 'test1'

@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('a', 'password1', b'The username and password that you entered did not match our records.\
                Please double-check and try again.'),
    ('test1', 'a', b'The username and password that you entered did not match our records.\
                Please double-check and try again.'),
))   
def test_login_validate_input(auth, username, password, message):
    response = auth.login(username, password)
    assert message in response.data

def test_logout(client, auth):
    auth.login()

    with client:
        auth.logout()
        assert 'user_id' not in session

@pytest.mark.parametrize(('path'), (
    '/auth/login',
    '/auth/register'
))
def test_already_logged_in(client, auth, path):
    auth.login()

    with client:
        response = client.get(path)
        assert response.headers['Location'] == 'http://localhost/'


