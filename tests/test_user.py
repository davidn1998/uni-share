import pytest
from unishare.database import *
from werkzeug.security import check_password_hash, generate_password_hash
from flask import request

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
    '/messages/compose',
))
def test_login_required(client, path):
    response = client.get(path)
    assert response.headers['Location'] == 'http://localhost/auth/login'

def test_inbox(client, auth, app):
    auth.login()
    assert client.get('/messages/inbox').status_code == 200

def test_sent(client, auth):
    auth.login()
    assert client.get('/messages/sent').status_code == 200

def test_compose(client, auth, app):
    auth.login()
    assert client.get('/messages/compose?recipient_name=test3&returnto=%2Fmessages%2Finbox').status_code == 404
    assert client.get('/messages/compose').status_code == 200
    assert client.get('/messages/compose?recipient_name=test2&returnto=%2Fmessages%2Finbox').status_code == 200
    response = client.post(
        '/messages/compose?recipient_name=test2&returnto=%2Fmessages%2Finbox',
        data = {'recipient':'test2', 'subject': 'test subject', 'body' : 'test body'},
    )

    assert response.headers['Location'] == 'http://localhost/messages/inbox'

    with app.app_context():
        assert Message.query.filter_by(subject='test subject').first() is not None

        sender = User.query.filter_by(username='test1').first()
        assert sender.sent_messages.filter_by(subject='test subject').first() is not None

        receiver = User.query.filter_by(username='test2').first()
        assert receiver.received_messages.filter_by(subject='test subject').first() is not None

@pytest.mark.parametrize(('recipient', 'subject', 'body', 'error'), (
    ('', 'a', 'b', b'Recipient is required.'),
    ('test2','', 'b', b'Subject is required.'),
    ('test2', 'b', '',  b'Body is required.'),
    ('a', 'b', 'c',  b'User: a does not exist.')
))
def test_compose_validate_input(client, auth, recipient, subject, body, error):
    auth.login()
    response = client.post(
        '/messages/compose?recipient_name=test2&returnto=%2Fmessages%2Finbox',
        data = {'recipient': recipient,'subject': subject, 'body' : body}
        )
    
    assert error in response.data

def test_read_message(client, auth, app):
    auth.login()

    with client:
        with app.app_context():
            User.query.get(2).send_message(recipient_id=1, subject='test', body='test')

            assert Message.query.get(1).read == False

            client.get('/messages/inbox')
            
            assert Message.query.get(1).read == True

        
