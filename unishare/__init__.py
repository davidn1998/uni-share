from flask import Flask
from unishare.database import db
import os

def create_app(testing=False):
    # Create the app
    app = Flask(__name__, instance_relative_config=True)
    
    # Load the default config file
    app.config.from_object('config')

    # Overide default configuration
    if testing == False:
        # Load the instance config when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test config if passed in
        app.config.update(
            SECRET_KEY = os.environ['SECRET_KEY'],
            SQLALCHEMY_DATABASE_URI = os.environ['POSTGRES_TEST_DB'],
            TESTING = True
        )

    # Load Database
    db.init_app(app)
    with app.app_context():
        db.create_all()

    # Import and register auth blueprint
    from unishare import auth
    app.register_blueprint(auth.bp)

    # Import and register blog blueprint
    from unishare import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')

    return app