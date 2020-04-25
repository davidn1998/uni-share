'''
A module that holds blueprint and views for blog pages

...

Methods
-------


'''
from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort
from unishare.auth import login_required
from unishare.database import *

# Create Blueprint for blog views
bp = Blueprint('blog', __name__)

@bp.route('/')
def index():
    '''Index page

    Show all posts
    '''
    # Get all post data
    posts = Post.query.join(User).with_entities(Post.author_id, Post.title, Post.body, Post.created, Post.id, User.username).order_by(Post.created.desc()).all()

    return render_template('blog/index.html', posts=posts)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    '''View at /create

    With GET -> returns HTML with a form to fill out.

    With POST -> When the form is submitted, it will validate their input and either 
    show the form again with an error message or
    create a post and add it to the database

    Use the login_required decorator so the user must be logged in to visit these views,
    otherwise they are redirected to the login page
    '''
    # If POST then get title and body of post
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        user = User.query.get(g.user.id)
        
        # Otherwise add post to database and redirect to index page
        user.add_post(title=title, body=body)
        return redirect(url_for('blog.index'))
    
    return render_template('blog/create.html')

def get_post(id, check_author=True):
    ''' Returns the post with the id

    check_author is defined so that the function can be used to get a post with or without verifying 
    that the person accessing the post is the author
    '''
    # Get post with id
    post = Post.query.get(id)

    # Validate post exists
    if post is None:
        abort(404, f'Post id {id} does not exist')
    
    # Validate author
    if check_author and post.author_id != g.user.id:
        abort(403)
    
    return post

@bp.route('/<int:id>/update', methods=['GET', 'POST'])
@login_required
def update(id):
    ''' Update the post title or body

    Takes in the argument id corresponding to the <int:id> in the route
    '''

    # Get post
    post = get_post(id)

    # If method is POST then get title and body from form
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None
        
        
        # Update title and/or body for post in database
        # Then redirect back to index page
        post.title = title
        post.body = body
        db.session.commit()
        return redirect(url_for('blog.index'))
    
    # If method is GET then show update.html (form)
    return render_template('blog/update.html', post=post)

@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    ''' Delete the post

    Takes in the argument id corresponding to the <int:id> in the route
    '''

    # Get post
    post = get_post(id)

    # Delete post from database
    db.session.delete(post)
    db.session.commit()

    # Redirect to index page
    return redirect(url_for('blog.index'))






