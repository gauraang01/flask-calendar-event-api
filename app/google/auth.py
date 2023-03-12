import pathlib
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


os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
GOOGLE_CLIENT_ID = Config.GOOGLE_CLIENT_ID
CLIENT_SECRET = Config.CLIENT_SECRET

CLIENT_CONFIG = json.loads(CLIENT_SECRET)

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
    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )

    return id_info

def get_flow():
    return flow