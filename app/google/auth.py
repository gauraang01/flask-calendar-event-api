import pathlib
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
import google.auth.exceptions
import requests
from google.oauth2 import id_token
from app.config import Config

import os

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
GOOGLE_CLIENT_ID = Config.GOOGLE_CLIENT_ID

client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", 
            "https://www.googleapis.com/auth/userinfo.email", 
            "openid", 
            "https://www.googleapis.com/auth/calendar"],
    redirect_uri="http://localhost:5000/callback"
)



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