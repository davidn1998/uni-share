'''
A module that holds blueprint and views for authorization pages

...

Methods
-------


'''

import functools
from flask import Blueprint, redirect, render_template, request, session, flash, url_for, g
from werkzeug.security import check_password_hash, generate_password_hash
import requests
import re
from unishare.database import *

# Create Blueprint for authorization views
bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=['GET','POST'])
def register():
    '''View at /auth/register 

    With GET -> 
        redirects to index if user is logged in
        returns HTML with a form to fill out if no user is logged in

    With POST -> When the form is submitted, it will validate their input and either 
    show the form again with an error message or
    create a new user and go to the login page
    '''
    # If method is post get username and password from form
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        error = None

        # Create a regex of special characters to validate against
        regex = re.compile('[@!#$%^&*()<>?/\|}{~:]') 
        
        # Validate that username and password are not empty
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif ' ' in username:
            error = 'Username cannot contain spaces.'
        elif ' ' in password:
            error = 'Password cannot contain spaces.'
        # Validate that username does not contain special characters
        elif regex.search(username) != None:
            error = 'Username can only contain alphanumeric characters (letters A-Z, numbers 0-9) and underscores.'
        # Validate the length of the username and password
        elif len(username) > 15:
            error = 'Username cannot be longer than 15 characters.'
        elif len(password) < 8:
            error = 'Password must be atleast 8 characters long.'
        # Validate that the user does not already exist
        elif User.query.filter_by(username=username).first() is not None:
            error = f'{username} is already registered.'

        if error is None:
            # If there are no errors, create new user and commit to database
            user = User(username=username, password=generate_password_hash(password))
            db.session.add(user)
            print(f'{username} has successfully registered.')
            db.session.commit()
            
            # Send a welcome message to the user
            creator = User.query.get(1)
            creator.send_message(recipient_id=user.id,
            subject='Welcome To UniShare',
            body='''This is a blogging website for users to share information related to university. 
                    Whether it's about uni life, courses, jobs or more, you can post here, share your thoughts and discuss with others in the community.

                    David - Creator of UniShare''')

            # Automatically login the user and go to index page
            return load_user_into_session(user)
        
        # Flash store error message so the template can use it
        flash(error)
    
    if g.user is None:
        # Show register page with registration
        return render_template('auth/register.html')
    else:
        # Redirect to index page
        return redirect(url_for('index'))

@bp.route('/login', methods=['GET', 'POST'])
def login():
    '''View at /auth/login 

    With GET -> 
        redirects to index if user is logged in
        returns HTML with a form to fill out if no user is logged in

    With POST -> When the form is submitted, it will validate their input and either 
    show the form again with an error message or
    login the user and redirect to index page
    '''  
    # If method is post get username and password from form
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error=None
        no_user = 'The username and password that you entered did not match our records.\
                Please double-check and try again.'
        
        # Find User with username
        user = User.query.filter_by(username=username).first()

        # Validate that user exists and that password is correct
        if user is None:
            error = no_user
        elif not check_password_hash(user.password, password):
            error = no_user

        # If there are no errors, clear session and create session with user_id
        # Then redirect to index page
        if error is None:
            return load_user_into_session(user)
        
        # Flash store error message so the template can use it
        flash(error)
    
    if g.user is None:
        # Show login page with login form
        return render_template('auth/login.html')
    else:
        # Redirect to index page
        return redirect(url_for('index'))

def load_user_into_session(user):
        '''Load a user into the session (login a user)

        Clear the session and add the users id to the session.
        Then redirect to the index page
        '''
        session.clear()
        session['user_id'] = user.id
        return redirect(url_for('index'))

@bp.before_app_request
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
        g.user = User.query.get(user_id)
        g.unread_messages_count = g.user.received_messages.filter_by(read=False).count()
        print(g.unread_messages_count)

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

