from flask import Flask

from flask_cors import CORS
from flask_restful import Api
from flask_selfdoc import Autodoc
from flask_wtf.csrf import CSRFProtect

import logging
from config import config

csrf = CSRFProtect()
cors = CORS()
auto = Autodoc()
api = Api()

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    logging.getLogger('werkzeug').setLevel(app.config['LOG_LEVEL'])

    csrf.init_app(app)
    cors.init_app(app)
    auto.init_app(app)
    api.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
