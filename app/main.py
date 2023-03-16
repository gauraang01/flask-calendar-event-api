from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask import (
    Flask,
    abort,
    redirect,
    request,
    session,
    render_template,
)
from app.utils.decorators import (
    validate_dates,
    user_id_is_required,
    fetchCredentials,
)
from app.google_utility.auth import (
    get_id_info,
    get_flow,
)

from app.mongo.db import (
    db_add_user,
)

from app.google_utility.calendar import get_calendar_events
from app.config import Config

app = Flask(__name__)
app.config.from_object(Config)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)

@app.route("/")
def index():
    return render_template('index.html')


@app.route("/login")
def login():
    try:
        authorization_url, state = get_flow().authorization_url()
        session["state"] = state
        return redirect(authorization_url)
    except Exception as error:
        print(f"Error occured: {error}")
        return redirect("/")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/callback")
def callback():
    try:
        get_flow().fetch_token(authorization_response=request.url)

        if not session["state"] == request.args["state"]:
            abort(500)  # State does not match!

        credentials = get_flow().credentials
        id_info = get_id_info(credentials)
        
        session["user_id"] = id_info.get("sub")
        session["name"] = id_info.get("name")

        user_id = id_info.get("sub")
        db_add_user(user_id, credentials)
        return redirect("/events")
    except Exception as error:
        print(f"Error occured: {error}")
        return redirect("/")


@app.route("/events", methods=["GET"])
@limiter.limit("5 per minute")
def get_events():
    return render_template("events.html")


@app.route("/events", methods=["POST"])
@limiter.limit("5 per minute")
@user_id_is_required
@validate_dates
@fetchCredentials
def post_events(user_id, dates, credentials):
    start_date, end_date = dates

    try:
        event_list = get_calendar_events(start_date, end_date, credentials)
        return (
        f"Your upcoming events are between "
        f"{start_date} and {end_date}: <br/> {', '.join(event_list)} <br/> "
        f"<a href='/logout'><button>Logout</button></a>"
    )
    except Exception as error:
        print(f"Error occured: {error}")
        return redirect("/")
    



if __name__ == '__main__':
    app.run()
