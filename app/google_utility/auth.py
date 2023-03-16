import json
import os
from google.oauth2.credentials import Credentials
import google_auth_oauthlib.flow
from google_auth_oauthlib.flow import Flow
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
import google.auth.exceptions
import requests
from google.oauth2 import id_token
from app.config import Config
from app.mongo.db import db_add_user
from datetime import datetime, timedelta


os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
GOOGLE_CLIENT_ID = Config.GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET = Config.GOOGLE_CLIENT_SECRET
GOOGLE_CLIENT_JSON = Config.GOOGLE_CLIENT_JSON
CLIENT_CONFIG = json.loads(GOOGLE_CLIENT_JSON)

SCOPES=["https://www.googleapis.com/auth/userinfo.profile", 
            "https://www.googleapis.com/auth/userinfo.email", 
            "openid", 
            "https://www.googleapis.com/auth/calendar"]


flow = google_auth_oauthlib.flow.Flow.from_client_config(
        client_config=CLIENT_CONFIG,
        scopes=SCOPES)

flow.redirect_uri = 'http://localhost:5000/callback'


def get_id_info(credentials):
    token_request = google.auth.transport.requests.Request(session=requests.session())
    try:
        id_info = id_token.verify_oauth2_token(
            id_token=credentials._id_token,
            request=token_request,
            audience=GOOGLE_CLIENT_ID
        )
        return id_info
    except Exception as error:
        raise Exception(f"Error occured: {error}")



def refresh_token(credentials):
    print(credentials.refresh_token)
    print(type(credentials.refresh_token))

    params = {
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "refresh_token": credentials.refresh_token,
        "grant_type": "refresh_token"
    }

    try:
        response = requests.post("https://oauth2.googleapis.com/token", data=params)
        response.raise_for_status()
        # Calculate the new expiry date based on the current time and the expires_in value in the response
        new_expiry = datetime.now() + timedelta(seconds=response.json()['expires_in'])

        # Create the new Credentials object with the updated access token and expiry date
        new_credentials = Credentials(
            token=response.json()['access_token'],
            refresh_token=credentials.refresh_token,
            token_uri=credentials.token_uri,
            client_id=GOOGLE_CLIENT_ID,
            client_secret=GOOGLE_CLIENT_SECRET,
            scopes=SCOPES,
            expiry=new_expiry
        )
        return new_credentials
    except requests.exceptions.HTTPError as error:
        # Handle HTTP errors
        raise Exception(f"HTTP error occurred: {error}")
    
    except Exception as error:
        raise Exception(f"Error occured: {error}")


def get_flow():
    return flow