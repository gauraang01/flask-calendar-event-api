from app.utils.validation import (
    validate_dates,
    user_id_is_required,
    fetchCredentials,
)
from pip._vendor import cachecontrol
from app.google.auth import (
    get_id_info,
    get_flow,
)
from flask import (
    Flask,
    abort,
    g,
    redirect,
    request,
    session,
    render_template,
)
from googleapiclient.discovery import build
from app.mongo.db import (
    db_add_user,
)

from app.google.calendar import get_calendar_events
from app.config import Config

app = Flask(__name__)
app.config.from_object(Config)

@app.route("/")
def index():
    return render_template('index.html')


@app.route("/login")
def login():
    authorization_url, state = get_flow().authorization_url()
    session["state"] = state
    return redirect(authorization_url)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/callback")
def callback():
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


@app.route("/events", methods=["GET"])
def get_events():
    return render_template("events.html")


@app.route("/events", methods=["POST"])
@user_id_is_required
@validate_dates
@fetchCredentials
def post_events(user_id, dates, credentials):
    if(dates == None):
        return "Invalid date format. Please use YYYY-MM-DD format, and ensure that you are passing both dates."
    else:
        start_date, end_date = dates

    event_list = get_calendar_events(start_date, end_date, credentials)

    return (
        f"Your upcoming events are between "
        f"{start_date} and {end_date}: <br/> {', '.join(event_list)} <br/> "
        f"<a href='/logout'><button>Logout</button></a>"
    )



if __name__ == '__main__':
    app.run()
