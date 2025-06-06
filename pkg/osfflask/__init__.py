"""
Copyright (c) 2024, Kevin Crouse. 

This file is part of the *URE Methods Plugin Repository*, located at 
https://github.com/kcphila/osf-ure-plugins

This file is distributed under the terms of the GNU General Public License 3.0
and can be used, shared, or modified provided you attribute the original work 
to the original author, Kevin Crouse.

See the README.md in the root of the project directory, or go to 
http://www.gnu.org/licenses/gpl-3.0.html for license details.
"""

import os
import flask
from . import auth,importer,osf,google, exporter, search

def create_app(test_config=None):
    # create and configure the app
    app = flask.Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'osfapp.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/')
    def index():
        return(flask.render_template('index.html'))

    @app.route('/collectionlist')
    def collectionlist():
        return(flask.render_template('collectionlist.html'))

    # register the blueprints
    app.register_blueprint(auth.bp)
    app.register_blueprint(importer.bp)
    app.register_blueprint(osf.bp)
    app.register_blueprint(google.bp)
    app.register_blueprint(exporter.bp)
    app.register_blueprint(search.bp)


    return app
