from flask import jsonify, abort
import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth
from firebase_admin import firestore
from functools import wraps


# def _firebase_auth_required(f):
#     @wraps(f)
#     def wrapper(request):
#         authorization = request.headers.get('Authorization')
#         id_token = None
#         if authorization and authorization.startswith('Bearer '):
#             id_token = authorization.split('Bearer ')[1]
#         else:
#             _json_abort(401, message="Invalid authorization")
#
#         try:
#             decoded_token = auth.verify_id_token(id_token)
#         except Exception as e:
#             _json_abort(401, message="Invalid authorization")
#         return f(request, decoded_token)
#     return wrapper


cred = credentials.Certificate("firebase_admin.json")
firebase_admin.initialize_app(cred)
db = firestore.client()


def get_collection(collection_name):
    users_ref = db.collection(collection_name)
    return users_ref


# @_firebase_auth_required
def get_city(request):
    request_json = request.get_json(silent=True)
    if request_json is None or "data" not in request_json:
        _json_abort(400, 'Bad Request')

    if request.method == 'POST':
        docs = get_collection('city').stream()
        response_dict = {
            'city': []
        }
        for doc in docs:
            city_dict = {'doc_id': doc.id, 'name': doc.to_dict()['name']}
            response_dict['city'].append(city_dict)
        return _json(response_dict)
    else:
        _json_abort(405, 'Method Not Allowed')


def get_language(request):
    request_json = request.get_json(silent=True)
    if request_json is None or "data" not in request_json:
        _json_abort(400, 'Bad Request')

    if request.method == 'POST':
        docs = get_collection('language').stream()
        response_dict = {
            'language': []
        }
        for doc in docs:
            language_dict = {'doc_id': doc.id, 'name': doc.to_dict()['name']}
            response_dict['language'].append(language_dict)
        return _json(response_dict)
    else:
        _json_abort(405, 'Method Not Allowed')


def _json(data):
    data = {
        'data': data
    }
    response = jsonify(data)
    response.status_code = 200
    response.headers.add('Content-Type', 'charset=utf-8')
    return response


def _json_abort(status_code, message):
    data = {
        'error': {
            'code': status_code,
            'message': message
        }
    }
    response = jsonify(data)
    response.status_code = status_code
    response.headers.add('Content-Type', 'charset=utf-8')
    abort(response)
