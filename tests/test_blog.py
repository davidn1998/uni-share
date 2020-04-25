import pytest
from unishare.database import *
from werkzeug.security import check_password_hash, generate_password_hash

def test_index(client, auth):
    response = client.get('/')
    assert b'Log In' in response.data
    assert b'Register' in response.data

    auth.login()
    response = client.get('/')
    assert b'Log Out' in response.data
    assert b'test title 1' in response.data
    assert b'test 1' in response.data
    assert b'href="/1/update"' in response.data

@pytest.mark.parametrize('path', (
    '/create',
    '/1/update',
    '/1/delete',
))
def test_login_required(client, path):
    response = client.post(path)
    assert response.headers['Location'] == 'http://localhost/auth/login'

def test_author_required(app, client, auth):
    # Change the post author to another user
    with app.app_context():
        post = Post.query.filter_by(author_id=1).first()
        post.author_id = 2
        db.session.commit()

    auth.login()
    # current user cannot modify other user's post
    assert client.post('/1/update').status_code == 403
    assert client.post('/1/delete').status_code == 403
    # current user doesn't see edit link
    assert b'href"/1/update"' not in client.get('/').data