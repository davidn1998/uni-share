# '''
# A module that holds blueprint and views for user pages

# ...

# Methods
# -------


# '''
# from flask import Blueprint, flash, g, redirect, render_template, request, url_for
# from werkzeug.exceptions import abort
# from unishare.auth import login_required
# from unishare.database import *

# # Create Blueprint for blog views
# bp = Blueprint('user', __name__)

# @bp.route('/<username>')
# def profile(username):
#     ''' View a the profile page of a user

#     Will return the profile page either of the logged in user or another user
#     '''
#     my_profile=False
#     exists=False
#     posts=[]

#     # Check if the profile page is for the logged in user then return their profile
#     if g.user is not None:
#         if g.user.username == username:
#             my_profile=True

#     # Verify that the user exists
#     user = User.query.filter_by(username=username).first()
#     exists = user is not None

#     if exists:
#         posts = user.posts
    
#     # Return profile pages
#     return render_template('user/profile.html', username=username, exists=exists, my_profile=my_profile, posts=posts)

# @bp.route('/messages')
# @login_required
# def messages():
#     ''' Get all messages for the logged in user.
#     '''
#     messages = Message.query.filter_by(recipient_id=g.user.id).join(User).with_entities(
#         Message.sender_id, 
#         Message.recipient, 
#         Message.subject, 
#         Message.body,
#         Message.date,
#         Message.id, 
#         Message.sender.username,
#         Message.recipient.username).order_by(Message.date.desc()).all()

#     print(messages)

#     return render_template('user/messages.html', messages=messages)
