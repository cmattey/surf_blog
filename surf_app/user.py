from flask import (
    Blueprint, url_for, redirect, session, render_template, flash, g, request
)

from surf_app.auth import login_required
from surf_app.db import get_db

bp = Blueprint('user', __name__, url_prefix='/user')

@bp.route('/<username>')
@login_required
def user_profile(username):
    db = get_db()

    user = db.execute('SELECT * FROM user WHERE username=?',(username,)).fetchone()
    user_posts = db.execute(
    'SELECT id, title, body, created, author_id'
    ' FROM posts WHERE author_id = (?)'
    ' ORDER BY created DESC',(user['id'],)
    ).fetchall()

    return render_template('user/user_profile.html', user=user, posts=user_posts)

@bp.route('/follow/<username>')
@login_required
def follow(username):
    db = get_db()
    error = None
    current_user = g.user

    follow_user = db.execute('SELECT * FROM user WHERE username = (?)',(username,)).fetchone()

    if follow_user is None:


    db.execute('')

    pass

@bp.route('/unfollow/<username>')
@login_required
def unfollow(username):
    pass
