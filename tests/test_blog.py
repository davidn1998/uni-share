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

    auth.login()
    # current user cannot modify other user's post
    assert client.post('/2/update').status_code == 403
    assert client.post('/2/delete').status_code == 403
    # current user doesn't see edit link
    assert b'href"/1/update"' not in client.get('/').data

@pytest.mark.parametrize('path', (
    '/3/update',
    '/3/delete',
))
def test_exists_required(client, auth, path):
    auth.login()
    assert client.post(path).status_code

def test_create(client, auth, app):
    auth.login()
    assert client.get('/create').status_code == 200
    client.post('/create', data={'title':'created', 'body':''})

    with app.app_context():
        count = db.session.execute('SELECT COUNT (id) FROM posts').fetchone()[0]
        print(count)
        assert count == 3

def test_update(client, auth, app):
    auth.login()
    assert client.get('/1/update').status_code == 200
    client.post('/1/update', data={'title':'updated', 'body':''})

    with app.app_context():
        post = Post.query.filter_by(id=1).first()
        assert post.title == 'updated'

@pytest.mark.parametrize('path', (
    '/create',
    '/1/update',
))
def test_create_update_validate(client, auth, path):
    auth.login()
    response = client.post(path, data={'title':'', 'body':''})

def test_delete(client, auth, app):
    auth.login()
    response = client.post('/1/delete')
    assert response.headers['Location'] == 'http://localhost/'

    with app.app_context():
        post = Post.query.get(1)
        assert post is None