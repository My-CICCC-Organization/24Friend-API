import json
from google.cloud import firestore
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

def get_collection(collection_name):
    cred = credentials.Certificate("firebase_admin.json")
    firebase_admin.initialize_app(cred)

    db = firestore.client()
    users_ref = db.collection(collection_name)
    return users_ref


def get_city(request):
    docs = get_collection('city').stream()

    response_dict = {
        'city': []
    }

    for doc in docs:
        response_dict['city'].append(doc.to_dict()['name'])

    return response_dict


def get_language(request):
    docs = get_collection('language').stream()

    response_dict = {
        'language': []
    }

    for doc in docs:
        response_dict['language'].append(doc.to_dict()['name'])

    return response_dict


# request = ''
# print(get_city(request))
# print(get_language(request))
