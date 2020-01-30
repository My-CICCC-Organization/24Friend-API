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
    request_json = request.get_json(silent=True)
    collection = get_collection('user')
    user = collection.document(request_json['user_doc_id']).get()
    if user.exists:
        return '{}'.format((request_json['user_doc_id']))

    else:
        data = {
        }
        new_user = collection.add(data)
        return '{}'.format((new_user[1].id))


def set_user_survey(request):
    request_json = request.get_json(silent=True)
    collection = get_collection('user')
    user = collection.document(request_json['user_doc_id'])
    if not user:
        return str(http.HTTPStatus.INTERNAL_SERVER_ERROR.value)

    survey = {
        u'nickname': request_json['nickname'],
        u'city_doc_id': request_json['city_doc_id'],
        u'languages': request_json['languages'],
        u'registration_token': request_json['registration_token']
    }
    user.set(survey)

    return str(http.HTTPStatus.OK.value)


def match_room(request):
    # request_json = request.get_json(silent=True)
    request_json = request
    collection = get_collection('room')
    room = collection \
        .where(u'city_doc_id', u'==', request_json['city_doc_id']) \
        .where(u'languages', u'array_contains_any', request_json['languages']) \
        .where(u'last_user_doc_id', u'==', None).get()

    match_room = None
    for r in room:
        match_room = collection.document(r.id)
        break

    if match_room:
        data = {
            u'last_user_doc_id': request_json['user_doc_id'],
            u'started_at': datetime.datetime.now()
        }
        set_room = match_room.update(data)
        return set_room


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
        user = collection.document(new_room[1].id).get()
        return user.to_dict()


def post_chat(request):
    request_json = request.get_json(silent=True)
    collection = get_collection(u'chat')
    chat = {
        u'message': request_json['message'],
        u'room_doc_id': request_json['room_doc_id'],
        u'user_doc_id': request_json['user_doc_id'],
        u'created_at': datetime.datetime.now()
    }

    collection.document().set(chat)

    return str(http.HTTPStatus.OK.value)


def exit_room(request):
    request_json = request.get_json(silent=True)
    collection = get_collection('room')
    room = collection.document(request_json['room_doc_id'])
    if not room:
        return str(http.HTTPStatus.INTERNAL_SERVER_ERROR.value)
    else:
        data = {
            u'ended_at': datetime.datetime.now()
        }
        room.update(data)

        return str(http.HTTPStatus.OK.value)


def delete_room():
    room_collection = get_collection('room')
    rooms = room_collection.where(u'created_at', u'>', datetime.datetime.now() + datetime.timedelta(days=-1)).stream()

    for room in rooms:
        room.set({u'ended_at': datetime.datetime.now()})


# if __name__ == '__main__':
    # delete_room()
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
