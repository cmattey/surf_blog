from flask import (
    Blueprint, url_for, render_template, g, flash, redirect, request, session
    )
from werkzeug.exceptions import abort

from surf_app.auth import login_required
from surf_app.db import get_db

bp = Blueprint('blog', __name__)

@bp.route('/')
def landing_page():
    if 'user_id' in session:
        return redirect(url_for('blog.index'))
    else:
        return render_template('blog/landing_page.html')


@bp.route('/home')
def index():
    db = get_db()

    posts = db.execute(
    'SELECT p.id, title, body, created, author_id, username'
    ' FROM posts p JOIN user u ON p.author_id = u.id'
    ' ORDER BY created DESC'
    ).fetchall()

    return render_template('blog/index.html', posts = posts)

@bp.route('/create', methods=('GET','POST'))
@login_required
def create():
    if request.method=='POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'
        elif not body:
            error = 'Body is required'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO posts (title, body, author_id)'
                'VALUES (?,?,?)',
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')

# The check_author argument is defined so that the function can be used to get
# a post without checking the author. This would be useful if you wrote a view
# to show an individual post on a page, where the user doesn’t matter because
# they’re not modifying the post.
def get_post(id, check_author = True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM posts p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id, )
    ).fetchone()

    if post is None:
        abort(404,"Post id {0} doesn't exist".format(id))
    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post


@bp.route('/<int:id>/update', methods=('GET','POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method=='POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if title is None:
            error = "Title is required"
        elif body is None:
            error = "Body is required"

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
            'UPDATE posts SET title=?, body=?'
            ' WHERE id=?',
            (title, body, id)
            )
        db.commit()
        return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post = post)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute(
    'DELETE FROM post WHERE id = ?',(id,)
    )
    db.commit()
    return redirect(url_for('blog.index'))
