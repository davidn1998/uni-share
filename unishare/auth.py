'''
A module that holds blueprint and views for authorization pages

...

Methods
-------


'''

import functools
from flask import Blueprint, redirect, render_template, request, session, flash, url_for, g
from werkzeug.security import check_password_hash, generate_password_hash
from unishare.database import *

# Create Blueprint for authorization views
bp = Blueprint('auth', __name__, url_prefix='/auth')

bp.route('/register', methods=['GET','POST'])
def register():
    '''View at /auth/register 

    With GET -> returns HTML with a form to fill out.

    With POST -> When the form is submitted, it will validate their input and either 
    show the form again with an error message or
    create a new user and go to the login page
    '''
    # If method is post get username and password from form
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Validate that username and password are not empty
        # and that the username does not already exist
        if username is None:
            error = 'Username is required.'
        elif password is None:
            error = 'Password is required.'
        elif User.query.filter_by(username=username).first() is not None:
            error = f'User {username} is already registered.'

        # If there are no errors, create new user and commit to database
        # Then redirect to login page
        if error is None:
            user = User(username=username, password=generate_password_hash(password))
            db.session.add(user)
            print(f'{username} has successfully registered.')
            db.session.commit()
            return redirect(url_for('auth.login'))
        
        # Flash store error message so the template can use it
        flash(error)
    
    # If method is GET or there were errors in POST then show register.html
    return render_template('auth/register.html')

bp.route('/login', methods=['GET', 'POST'])
def login():
    '''View at /auth/login 

    With GET -> returns HTML with a form to fill out.

    With POST -> When the form is submitted, it will validate their input and either 
    show the form again with an error message or
    login the user and redirect to index page
    '''  
    # If method is post get username and password from form
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Find User with username
        user = User.query.filter_by(username=username).first()

        # Validate that user exists and that password is correct
        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user.password, password):
            error = 'Incorrect password'

        # If there are no errors, clear session and create session with user_id
        # Then redirect to index page
        if error is None:
            session.clear()
            session['user_id'] = user.id
            return redirect(url_for('index'))

        
        # Flash store error message so the template can use it
        flash(error)
    
    # If method is GET or there were errors in POST then show login.html
    return render_template('auth/login.html')

@bp.before_app_request()
def load_logged_in_user():
    '''Load data of logged in user

    At the beginning of each request, if a user is logged in
    their information should be loaded and made available to other views

    Check if a user_id is stored in the session and get that user's data from the database,
    storing it on g.user, which lasts the length of the request.

    If there is no user_id, or if the id doesn't exist, set g.user to None
    '''  
    # Get user_id of session
    user_id = session.get('user_id')

    # Store logged in user (if any) in g.user
    if user_id is None:
        g.user = None
    else:
        g.user = User.query.filter_by(id=user_id).first()

@bp.route('/logout')
def logout():
    '''Logout User

    Remove the user_id from the session so load_logged_in_user won't load a user on subsequent requests.
    '''  
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    '''Check that the user is logged in for a view

    This decorator returns a new view function that wraps the original view it's applied to.
    The new function checks if a user is loaded and redirects to the login page otherwise.
    If a user is loaded, the original view is called and continues normally.
    '''
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view

