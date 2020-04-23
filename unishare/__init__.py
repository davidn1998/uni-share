from flask import Flask

def create_app(test_config=None):
    # Create the app
    app = Flask(__name__, instance_relative_config=True)
    
    # Load the default config file
    app.config.from_object('config')

    # Overide default configuration
    if test_config is None:
        # Load the instance config when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load tbe test config if passed in
        app.config.from_mapping(test_config)

    # test app
    @app.route('/')
    def test():
        return 'Welcome to Uni Share'

    return app