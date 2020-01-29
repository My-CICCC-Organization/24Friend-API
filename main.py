import json
from google.cloud import firestore

import firebase_admin
import http
import time
from firebase_admin import credentials
from firebase_admin import firestore

from flask import escape

def get_collection(collection_name):
    cred = credentials.Certificate("firebase_admin.json")
    firebase_admin.initialize_app(cred)

    db = firestore.client()
    users_ref = db.collection(collection_name)
    return users_ref


def get_user(request):
    request_json = request.get_json(silent=True)
    collection = get_collection('user')
    user = collection.document(request_json['user_doc_id']).get()
    if user.exists:
        return '{}'.format(escape(request_json['user_doc_id']))

    else:
        data = {
        }
        new_user = collection.add(data)
        return '{}'.format(escape(new_user[1].id))


def set_user_survey(request):
    request_json = request.get_json(silent=True)
    collection = get_collection(u'user')
    user = collection.document(request_json['user_id']).get()
    if not user:
        return http.HTTPStatus.INTERNAL_SERVER_ERROR

    survey = {
        u'nickname': request_json['nickname'],
        u'city_doc_id': request_json['city_doc_id'],
        u'languages': request_json['languages'],
    }
    user.update(survey)

    return http.HTTPStatus.OK


def match_room(request):
    request_json = request.get_json(silent=True)
    user_collection = get_collection('user')
    user = user_collection.document(request_json['user_id'])
    room_collection = get_collection('room')
    room = room_collection.where(u'laungages', u'array_contains_any', user['language']).stream()

    if not room:
        data = {
            u'first_user_doc_id': request_json['user_id'],
            u'last_user_doc_id': None
        }
        new_room = room_collection.add(data)
        return new_room
    else:
        room = {
            u'last_user_doc_id': request_json['user_id'],
            u'created_at': time.time()
        }
        exist_room = room.set(room)
        return exist_room


def post_chat(request):
    request_json = request.get_json(silent=True)
    collection = get_collection(u'chat')
    chat = {
        u'message': request_json['message'],
        u'room_doc_id': request_json['room_doc_id'],
        u'user_doc_id': request_json['user_doc_id'],
        u'created_at': request_json['created_at'],
    }

    collection.document().set(chat)

    return http.HTTPStatus.OK


def delete_room():
    room_collection = get_collection('room')
    rooms = room_collection.where(u'created_at', u'>', time.time()).stream()

    for room in rooms:
        room.set({u'created_at': time.time()})


# if __name__ == '__main__':
#     print(set_user_survey('CFNg85TFAUvOGk1WdYg0'))
#     # collection = get_collection('chat')
#     # collection = get_collection('room')
#     # docs = collection.document('OSiaocwKncMhcYkykYzk').get()
#     # docs = collection.where(u'name', u'==', u'太郎').stream()
#     # docs = collection.where(u'laungage', u'array_contains_any', ['Japanese']).stream()
#
#     # print(docs.to_dict())
#
#     # for doc in docs:
#     #     print('{}'.format(doc.to_dict()))
