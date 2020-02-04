from flask import jsonify, abort
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import datetime
import http


cred = credentials.Certificate("firebase_admin.json")
firebase_admin.initialize_app(cred)
db = firestore.client()


def get_collection(collection_name):
    return db.collection(collection_name)


def get_user(request):
    _print_access_log(request)

    request_json = request.get_json(silent=True)
    if request_json is None or "data" not in request_json:
        _json_abort(400, 'Bad Request')

    if request.method == 'POST':

        collection = get_collection('user')

        # TODO
        if request_json['data']['user_doc_id'] == "":
            data = {
            }
            new_user = collection.add(data)
            response_dict = {'user_doc_id': new_user[1].id}
            return _json(response_dict)

        user = collection.document(request_json['data']['user_doc_id']).get()
        if user.exists:
            response_dict = {'user_doc_id': request_json['data']['user_doc_id']}
            return _json(response_dict)
        else:
            data = {
            }
            new_user = collection.add(data)
            response_dict = {'user_doc_id': new_user[1].id}
            return _json(response_dict)
    else:
        _json_abort(405, 'Method Not Allowed')


def set_user_survey(request):
    _print_access_log(request)

    request_json = request.get_json(silent=True)
    if request_json is None or "data" not in request_json:
        _json_abort(400, 'Bad Request')

    collection = get_collection('user')
    user_ref = collection.document(request_json['data']['user_doc_id'])
    if not user_ref.get().exists:
        _json_abort(404, 'Not found')

    if request.method == 'POST':
        survey = {
            u'nickname': request_json['data']['nickname'],
            u'city_doc_id': request_json['data']['city_doc_id'],
            u'languages': request_json['data']['languages'],
            u'registration_token': request_json['data']['registration_token']
        }
        user_ref.set(survey)
        response_dict = {'code': str(http.HTTPStatus.OK.value)}
        return _json(response_dict)
    else:
        _json_abort(405, 'Method Not Allowed')


def match_room(request):
    _print_access_log(request)

    request_json = request.get_json(silent=True)
    if request_json is None or "data" not in request_json:
        _json_abort(400, 'Bad Request')

    collection = get_collection('room')
    if request.method == 'POST':
        room_refs = collection \
            .where(u'city_doc_id', u'==', request_json['data']['city_doc_id']) \
            .where(u'languages', u'array_contains_any', request_json['data']['languages']) \
            .where(u'last_user_doc_id', u'==', None).stream()

        match_room = None
        for r in room_refs:
            match_room = collection.document(r.id)
            break

        if match_room:
            data = {
                u'last_user_doc_id': request_json['user_doc_id'],
                u'started_at': str(datetime.datetime.now())
            }
            match_room.update(data)
            set_room = collection.document(match_room.id).get()

            return _json(set_room.to_dict())
        else:
            data = {
                u'first_user_doc_id': request_json['user_doc_id'],
                u'last_user_doc_id': None,
                u'city_doc_id': request_json['city_doc_id'],
                u'languages': request_json['languages'],
                u'started_at': None,
                u'ended_at': None
            }
            new_room = collection.add(data)

            collection = get_collection('room')
            room_refs = collection.document(new_room[1].id).get()
            return _json(room_refs.to_dict())
    else:
        _json_abort(405, 'Method Not Allowed')


def post_chat(request):
    _print_access_log(request)

    request_json = request.get_json(silent=True)
    if request_json is None or "data" not in request_json:
        _json_abort(400, 'Bad Request')

    if request.method == 'POST':
        collection = get_collection(u'chat')
        chat = {
            u'message': request_json['data']['message'],
            u'room_doc_id': request_json['data']['room_doc_id'],
            u'user_doc_id': request_json['data']['user_doc_id'],
            u'created_at': str(datetime.datetime.now())
        }
        collection.document().create(chat)
        response_dict = {'code': str(http.HTTPStatus.OK.value)}
        return _json(response_dict)
    else:
        _json_abort(405, 'Method Not Allowed')


def exit_room(request):
    _print_access_log(request)

    request_json = request.get_json(silent=True)
    if request_json is None or "data" not in request_json:
        _json_abort(400, 'Bad Request')

    collection = get_collection('room')
    room_ref = collection.document(request_json['data']['room_doc_id'])
    if not room_ref.get().exists:
        _json_abort(404, 'Not found')
    else:
        data = {
            u'ended_at': str(datetime.datetime.now())
        }
        room_ref.update(data)
        response_dict = {'code': str(http.HTTPStatus.OK.value)}
        return _json(response_dict)


def delete_room():
    room_collection = get_collection('room')
    rooms = room_collection.where(u'created_at', u'>', str(datetime.datetime.now()) + datetime.timedelta(days=-1)).stream()

    for room in rooms:
        room.set({u'ended_at': str(datetime.datetime.now())})


def _json(data):
    # TODO remove later
    print("Response body: ", data)

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


def _print_access_log(request):
    request_json = request.get_json(silent=True)
    print('[ACCESS LOG] START')
    print("Method: ", request.method)
    print("Request body: ", request_json)
    print('[ACCESS LOG] END')

# if __name__ == '__main__':
    # data = {
    #     "user_doc_id": "o4c2Uca0q1D3Dz90U1ta",
    #     "city_doc_id": "AzsfgA3tgjjolk9F9",
    #     "languages": [
    #         "8hl4GHNAamfqH3Hvu",
    #         "9Fs8Jjkfa4Ag3nkx"],
    # }
    # data = {
    #     "message": "Donald Trump",
    #     "room_doc_id": "AzsfgA3tgjjolk9F9",
    #     "user_doc_id": "o4c2Uca0q1D3Dz90U1ta",
    #     "created_at": "2020/01/01 11:11:11"
    # }
    # data = {
    #     "nickname": "Donald Trump",
    #     "city_doc_id": "AzsfgA3tgjjolk9F9",
    #     "user_doc_id": "o4c2Uca0q1D3Dz90U1ta",
    #     "languages": [
    #         "8hl4GHNAamfqH3Hvu",
    #         "9Fs8Jjkfa4Ag3nkx"]
    # }
    # print(match_room(data))
    # print(set_user_survey('CFNg85TFAUvOGk1WdYg0'))
    # collection = get_collection('chat')
    # collection = get_collection('room')
    # docs = collection.document('OSiaocwKncMhcYkykYzk').get()
    # docs = collection.where(u'name', u'==', u'太郎').stream()
    # docs = collection.where(u'languages', u'array_contains_any', ['8hl4GHNAamfqH3Hvu']).stream()
    #
    # print(docs.to_dict())

    # for doc in docs:
    #     print('{}'.format(doc.to_dict()))
