from flask import Flask

from flask_cors import CORS
from flask_restful import Api
from flask_wtf.csrf import CSRFProtect

import logging
from config import config

csrf = CSRFProtect()
cors = CORS()
rapi = Api()

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    logging.getLogger('werkzeug').setLevel(app.config['LOG_LEVEL'])

    csrf.init_app(app)
    cors.init_app(app)
    rapi.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api/v1.0')

    return app
