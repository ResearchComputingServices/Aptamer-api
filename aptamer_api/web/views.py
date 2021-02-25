from flask import request, jsonify, url_for, Blueprint
from flask import json, jsonify, Response, blueprints
from aptamer_api.web.common_view import flask_seed_bp
from aptamer_api.decorators.crossorigin import crossdomain
from aptamer_api.decorators.authentication import authentication
import aptamer_api.web.role_view
import aptamer_api.web.user_view
import aptamer_api.web.image_view
import aptamer_api.web.user_field_type_view
import aptamer_api.web.user_field_category_view
import aptamer_api.web.enumeration_view
import aptamer_api.web.user_keycloak
import aptamer_api.web.authorization_view

@flask_seed_bp.route("/", methods=['GET'])
@crossdomain(origin='*')
@authentication
def hello():
    return "Hello Language2Test!"

