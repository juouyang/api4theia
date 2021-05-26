from flask import Blueprint, make_response, jsonify

main = Blueprint('main', __name__)

@main.app_errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

from . import views
