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
    
    with client:
        auth.login()
        response = client.get(path)
        assert button_text in response.data
    