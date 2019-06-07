from flask import (
    Blueprint, url_for, redirect, session, render_template, flash, g, request
)

from surf_app.auth import login_required
from surf_app.db import get_db
import requests

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

    # Making call to our API to access user information

    user_api_url = "http://localhost:5000/api/users/{}".format(user['id'])
    user_api_response = requests.get(user_api_url)
    try:
        user_api_response.raise_for_status()
    except Exception as exc:
        print("There was a problem with SURF API:",(exc))

    user_details = user_api_response.json()

    return render_template('user/user_profile.html', user=user_details, posts=user_posts,is_following=is_following(username))

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

class User():
    """
    Utility class for quick access to user meta information.
    """

    def __init__(self,id):
        self.user_id = id

    def get_username(self):
        db = get_db()

        username = db.execute('SELECT username FROM user WHERE id = (?)',(self.user_id,)).fetchone()
        return username['username']

    def get_followers(self):
        db = get_db()

        followers = db.execute('SELECT follower_id FROM user_relations WHERE followed_id=(?)',
            (self.user_id,)).fetchall()

        return followers

    def get_followed(self):
        db = get_db()

        followed = db.execute('SELECT followed_id FROM user_relations WHERE follower_id=(?)',
                (self.user_id,)).fetchall()

        return followed

    def get_posts(self):
        db = get_db()

        user_posts = db.execute('SELECT id FROM posts WHERE author_id=(?)',
                (self.user_id,)).fetchall()

        return user_posts

    def to_dict(self):

        data = {
            'id':self.user_id,
            'username' : self.get_username(),
            'post_count' : len(self.get_posts()),
            'follower_count' : len(self.get_followers()),
            'followed_count' : len(self.get_followed()),
            '_links' : {
                    'self' : url_for('api.get_user',id=self.user_id),
                    'followers' : url_for('api.get_followers',id=self.user_id),
                    'followed' : url_for('api.get_followed', id=self.user_id)
            }
        }

        return data
