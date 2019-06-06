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

    return render_template('user/user_profile.html', user=user, posts=user_posts,is_following=is_following(username))

@bp.route('/follow/<username>')
@login_required
def follow(username):
    db = get_db()
    current_user = g.user

    follow_user = db.execute('SELECT * FROM user WHERE username = (?)',(username,)).fetchone()

    if follow_user is None:
        flash('User {} does not exist'.format(username))
        return redirect(url_for('blog.index'))
    elif follow_user['id']==session['user_id']:
        flash('You can Follow yourself')
        return redirect(url_for('blog.index'))
    elif is_following(username):
        flash('You are already following {}.format(username)')
        return redirect(url_for('user.user_profile',username=username))

    db.execute('INSERT INTO user_relations (follower_id, followed_id) VALUES (?,?)',
            (session['user_id'],follow_user['id']))

    db.commit()
    flash("You have succesfully followed {}".format(username))
    return redirect(url_for('user.user_profile',username=username))

@bp.route('/unfollow/<username>')
@login_required
def unfollow(username):
    db = get_db()
    error = None
    current_user = g.user

    unfollow_user = db.execute('SELECT * FROM user WHERE username = (?)',(username,)).fetchone()

    if unfollow_user is None:
        flash('User {} does not exist'.format(username))
        return redirect(url_for('blog.index'))

    db.execute('DELETE FROM user_relations WHERE follower_id=(?) and followed_id=(?)',
            (session['user_id'],unfollow_user['id']))

    db.commit()
    flash("You have succesfully unfollowed {}".format(username))
    return redirect(url_for('user.user_profile',username=username))

def is_following(username):
    db = get_db()
    follow_user = db.execute('SELECT * FROM user WHERE username = (?)',(username,)).fetchone()
    follow_row = db.execute('SELECT * FROM user_relations WHERE follower_id=(?) and followed_id=(?)',
            (session['user_id'],follow_user['id'])).fetchone()

    if follow_user is None:
        return False
    elif follow_row is not None:
        return True

    return False
