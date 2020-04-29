import pytest
from unishare.database import *
from werkzeug.security import check_password_hash, generate_password_hash

@pytest.mark.parametrize(('path', 'message'),(
    ('/user/test1', b'test1'),
    ('/user/a', b'This account does not exist. Try searching for another.')
))
def test_profile_exists(client, auth, path, message):
    response = client.get(path)
    assert message in response.data

@pytest.mark.parametrize(('path', 'button_text'),(
    ('/user/test1', b'Messages'),
    ('/user/test2', b'Message')
))
def test_profile_message_edit(client, auth, path, button_text):
    auth.login()
    response = client.get(path)
    assert button_text in response.data

@pytest.mark.parametrize('path', (
    '/messages/inbox',
    '/messages/sent',
    '/messages/test1/compose',
))
def test_login_required(client, path):
    response = client.get(path)
    assert response.headers['Location'] == 'http://localhost/auth/login'

def test_inbox(client, auth):
    auth.login()
    assert client.get('/messages/inbox').status_code == 200

def test_sent(client, auth):
    auth.login()
    assert client.get('/messages/sent').status_code == 200

def test_compose(client, auth, app):
    auth.login()
    assert client.get('/messages/test3/compose').status_code == 404
    assert client.get('/messages/test2/compose').status_code == 200
    response = client.post(
        '/messages/test2/compose',
        data = {'subject': 'test subject', 'body' : 'test body'}
    )

    assert response.headers['Location'] == 'http://localhost/'

    with app.app_context():
        assert Message.query.filter_by(subject='test subject').first() is not None

        sender = User.query.filter_by(username='test1').first()
        assert sender.sent_messages.filter_by(subject='test subject').first() is not None

        receiver = User.query.filter_by(username='test2').first()
        assert receiver.received_messages.filter_by(subject='test subject').first() is not None

@pytest.mark.parametrize(('subject', 'body', 'error'), (
    ('', 'a', b'Subject is required.'),
    ('a', '', b'Body is required.')
))
def test_compose_validate_input(client, auth, subject, body, error):
    auth.login()
    response = client.post(
        '/messages/test2/compose',
        data = {'subject': subject, 'body' : body}
        )
    
    assert error in response.data