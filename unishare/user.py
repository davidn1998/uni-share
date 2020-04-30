'''
A module that holds blueprint and views for user pages

...

Methods
-------


'''
from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort
from unishare.auth import login_required
from unishare.database import *

# Create Blueprint for blog views
bp = Blueprint('user', __name__)

@bp.route('/user/<username>')
def profile(username):
    ''' View a the profile page of a user

    Will return the profile page either of the logged in user or another user
    '''
    my_profile=False
    exists=False
    posts=[]

    # Check if the profile page is for the logged in user then return their profile
    if g.user is not None:
        my_profile = g.user.username == username

    # Verify that the user exists
    user = User.query.filter_by(username=username).first()
    exists = user is not None

    if exists:
        posts = user.posts.order_by(Post.created.desc()).all()
    
    # Return profile pages
    return render_template('user/profile.html', username=username, exists=exists, my_profile=my_profile, posts=posts)

@bp.route('/messages/inbox')
@login_required
def inbox():
    ''' Display the message inbox for the logged in user.
    '''
    
    # Get all messages in descending date order
    messages = g.user.received_messages.order_by(Message.date.desc()).all()

    # Get all unread messages
    unread_messages = g.user.received_messages.filter_by(read=False).all()
    # Change all unread messages to read
    for message in unread_messages:
        message.read = True
        db.session.commit()

    return render_template('user/inbox.html', messages=messages)

@bp.route('/messages/sent')
@login_required
def sent():
    ''' Display messages sent by the logged in user
    
    '''
    user = User.query.get(g.user.id)
    messages = user.sent_messages.order_by(Message.date.desc()).all()

    return render_template('user/sent.html', messages=messages)

@bp.route('/messages/compose', methods=['GET', 'POST'])
@login_required
def compose():
    '''View at /message/compose

    With GET -> returns HTML with a form to compose a message

    With POST -> When the form is submitted, it will validate their input and either 
    show the form again with an error message or
    compose a message and send it

    Use the login_required decorator so the user must be logged in to visit these views,
    otherwise they are redirected to the login page
    '''

    # Get url to return to, if provided
    return_url = request.args.get('returnto')

    if request.method == 'POST':
        # Get the form values
        to = request.form['recipient'].strip()
        subject = request.form['subject'].strip()
        body = request.form['body'].strip()
        error = None

        # Get recipient id
        recipient = User.query.filter_by(username=to).first()

        # Validate subject and body
        if not to:
            error = 'Recipient is required.'
        elif not subject:
            error = 'Subject is required.'
        elif not body:
            error = 'Body is required.'
        elif not recipient:
            error = f'User: {to} does not exist.'

        if error is not None:
            # Show error
            flash(error)
        else:
            # Create a new message and add to database
            g.user.send_message(recipient_id=recipient.id, subject=subject, body=body)
            if return_url is not None:
                return redirect(return_url)

    if request.args.get('recipient_name') is not None:
        recipient_name = request.args.get('recipient_name')
        # Validate that recipient_name exists
        if User.query.filter_by(username=recipient_name).first() is None:
            abort(404, f'User: {recipient_name} does not exist')
    else:
        recipient_name = ""
        
    return render_template('user/compose.html', recipient_name=recipient_name)