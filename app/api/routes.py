from app.api import bp
from flask import jsonify, request


@bp.route('/', methods=['GET'])
def get_no_title():
    return jsonify({
        'Status': 'NoTitle',
        'StatusCode': 200,
        'ErrorMessage': 'No title was set',
    })


@bp.route('/<title>/<int:page>', methods=['GET'])
def get_paginated(title, page):
    from . import omdbapi

    if page is None:
        page = 1
    return jsonify(omdbapi.get_omdb_movies(title, page))


@bp.route('/<title>', methods=['GET'])
def get(title):
    from . import omdbapi

    page = request.args.get('page')
    if page is None:
        page = 1
    return jsonify(omdbapi.get_omdb_movies(title, page))
