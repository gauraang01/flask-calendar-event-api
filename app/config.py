import os
import secrets

class Config:
    SECRET_KEY = secrets.token_urlsafe(16)
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_AUTH_SCOPE=[
            "https://www.googleapis.com/auth/userinfo.profile", 
            "https://www.googleapis.com/auth/userinfo.email", 
            "openid", 
            "https://www.googleapis.com/auth/calendar"
            ]
    GOOGLE_AUTH_REDIRECT_URI="http://localhost:5000/callback"
