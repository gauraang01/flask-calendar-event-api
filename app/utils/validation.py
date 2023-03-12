from google.auth.exceptions import RefreshError
from datetime import datetime
from flask import (
    redirect,
    request,
    session,
    url_for,
    Request,
)
from app.mongo.db import (
    db_get_user_credentials,
    db_add_user,
)

def user_id_is_required(function):
    def wrapper(*args, **kwargs):
        user_id =  request.form.get('user_id')
        
        if user_id == None:
            if "user_id" in session:
                user_id = session["user_id"]
            else:
                return redirect(url_for("login"))
        return function(user_id=user_id, *args, **kwargs)

    return wrapper

def validate_dates(function):
    def wrapper(*args, **kwargs):
        start_date_str = request.form.get("start_date")
        end_date_str = request.form.get("end_date")

        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()

            if start_date > end_date:
                raise ValueError("Start date should be before end date.")
            dates = (start_date, end_date)
        except (ValueError, TypeError):
            dates = None
        
        return function(dates=dates, *args, **kwargs)
    return wrapper

def fetchCredentials(function):
    def wrapper(*args, **kwargs):
        user_id = kwargs["user_id"]
        try: 
            credentials = db_get_user_credentials(user_id)
        except:
            return redirect(url_for("login"))

        if not credentials.valid:
            try:
                credentials.refresh(Request())
                db_add_user(user_id, credentials)
            except RefreshError:
                return redirect(url_for("login"))

        return function(credentials=credentials, *args, **kwargs)
    return wrapper