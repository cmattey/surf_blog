import os

from flask import Flask
from . import db

def create_app(test_config=None):
    # Create and configure the application
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'surf_app.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        # silent= True, doesn't raise issue if config.py doesn't exist
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config is passed in
        app.config.from_mapping(test_config)

    # ensure instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # register close_db and init_db_command commands with the application instance
    db.init_app(app)

    # Simple landing page

    @app.route('/hello')
    def hello():
        return 'Hello World!'

    return app
