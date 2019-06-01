import sqlite3

import click
from flask import current_app, g # current_app and g are special objects
from flask.cli import with_appcontext

def init_app(app):
    # app.teardown_appcontext() tells Flask to call that function when cleaning
    # up after returning the response.
    app.teardown_appcontext(close_db)

    # app.cli.add_command() adds a new command that can be called with the flask
    # command.
    app.cli.add_command(init_db_command)


def init_db():
    db = get_db()

    # open_resource() opens a file relative to the flaskr package
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf-8'))


# click.command() defines a command line command called init-db that calls
# the init_db function and shows a success message to the user.
@click.command('init-db')
@with_appcontext
def init_db_command():
    """ Clear the existing data and create new tables. """
    init_db()
    click.echo('Initialized the database.')


def get_db():
    """ Returns a databse connection. """
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        # sqlite3.Row tells the connection to return rows that behave like dicts
        # This allows accessing the columns by name.
        g.db.row_factory = sqlite3.Row

    return g.db

def close_db(e=None):
    db = g.pop('db',None)

    if db is not None:
        db.close()
