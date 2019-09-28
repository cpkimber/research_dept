"""
Making the vlog. There's blueprint stuff in here that is similar to the
use of blueprint in auth. Let's check it out. It all starts with import
statements
Cam Kimber Sept 27 2019
tutorial url
https://flask.palletsprojects.com/en/1.1.x/tutorial/blog/
"""

from flask import (
        Blueprint, flash, g, redirect, render_template, request, url_for
)

from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('blog',__name__)

################################################
# Function Name: index
# Function use: grabs blog posts and displays them
# Notes:
################################################

@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('blog/index.html', posts=posts)

################################################
# Function Name: create
# Function use: Click this button to make a post
# Notes: Have you be logged in
################################################

@bp.route('/create', methods=('GET','POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)

        else:
            db = get_db()
            db.execute(
                    'INSERT INTO post (title, body, author_id)'
                    ' VALUES (?, ?, ?)',
                    (title, body, g.user['id'])
                    )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')


################################################
# Function Name: get_post
# Function use: note sure
# Notes:
################################################

def get_post(id, check_author=True):
    post = get_db().execute(
            'SELECT p.id, title, body, created, author_id, username'
            ' FROM post p JOIN user u ON p.author_id = u.id'
            ' WHERE p.id = ?',
            (id,)
            ).fetchone()
    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post

################################################
# Function Name: Update
# Function use: Updates, edits, and deletes
# Notes:
################################################

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)


################################################
# Function Name: Delete
# Function use: Removes post from db
# Notes: troublesome
################################################
@bp.route('/<int:id>', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))
