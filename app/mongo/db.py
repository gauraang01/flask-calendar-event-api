import os
import json
import google.oauth2.credentials
from pymongo import MongoClient

# Set up MongoDB client and collection
mongo_client = MongoClient(os.environ.get('MONGO_URI'))
mongo_db = mongo_client[os.environ.get('MONGO_DB')]
mongo_collection = mongo_db[os.environ.get('MONGO_COLLECTION')]


# Define MongoDB schema
user_schema = {
    'user_id': str,
    'credentials_data': dict,
    'credentials': str
}

class MongoDBError(Exception):
    pass


def db_add_user(user_id, credentials):
    credentials_data = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes,
        'expiry': credentials.expiry.isoformat(),
    }
    
    try:
        mongo_collection.update_one(
            {'user_id': user_id},
            {'$set': {
                'credentials_data': credentials_data,
                'credentials': credentials.to_json()
            }},
            upsert=True
        )
    except Exception as e:
        raise MongoDBError(f"Error adding user to MongoDB: {e}")


def db_get_user_credentials(user_id):
    try:
        user_doc = mongo_collection.find_one({'user_id': user_id})
        if user_doc and 'credentials' in user_doc:
            credentials_info = json.loads(user_doc['credentials'])
            credentials = google.oauth2.credentials.Credentials.from_authorized_user_info(credentials_info)
            return credentials

        else:
            raise MongoDBError(f"User not found in the database")
    except Exception as e:
        raise MongoDBError(f"Error getting user credentials from MongoDB: {e}")
