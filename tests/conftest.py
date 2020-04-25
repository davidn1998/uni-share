import tempfile
import pytest
from unishare import create_app
from unishare.database import *
from werkzeug.security import check_password_hash, generate_password_hash


@pytest.fixture
def app():
    # Create app with test mappings
    app = create_app(testing=True)

    with app.app_context():
        db.drop_all()
        db.create_all()

        # Create users
        user1 = User(username='test1', password=generate_password_hash('password1'))
        user2 = User(username='test2', password=generate_password_hash('password2'))
        
        # Add users to database
        db.session.add(user1)
        db.session.add(user2)

        db.session.commit()

        # Create post
        user1.add_post(title='test title 1', body='test 1')
        user2.add_post(title='test title 2', body='test 2')

        db.session.commit()

    yield app

@pytest.fixture
def client(app):
    # Used to make requests without running the server
    return app.test_client()

@pytest.fixture
def runner(app):
    # Used to call the Click commands registered with the app
    return app.test_cli_runner()

class AuthActions(object):
    ''' Class that can login and logout a user on the client.

    The login() method will login user 'test1'

    The logout() method will logout user 'test1'
    '''
    def __init__(self, client):
        self._client = client

    def login(self, username='test1', password='password1'):
        return self._client.post(
            '/auth/login',
            data={'username': username, 'password': password}
        )

    def logout(self):
        return self._client.get('/auth/logout')

@pytest.fixture
def auth(client):
    # Fixture used to call login() or logout()
    return AuthActions(client)