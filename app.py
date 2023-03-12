import pytz
from database import Database
from datetime import datetime, time
from config import Config
from utils import (
    validate_dates,
    user_id_is_required,
    fetchCredentials,
)
from pip._vendor import cachecontrol
from auth import (
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
from mongo import (
    db_add_user,
)

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

    service = build("calendar", "v3", credentials=credentials)
    start = datetime.combine(start_date, time.min).isoformat() + "Z"  # 'Z' indicates UTC time
    end = datetime.combine(end_date, time.max).isoformat() + "Z"  # 'Z' indicates UTC time

    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=start,
            timeMax=end,
            maxResults=10,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )

    events = events_result.get("items", [])
    event_list = []

    if not events:
        event_list.append("No upcoming events found.")
    else:
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            event_time = (
                datetime.fromisoformat(start)
                .astimezone(pytz.timezone("Asia/Kolkata"))
                .strftime("%Y-%m-%d %H:%M:%S")
            )
            event_list.append(f"{event_time} - {event['summary']}")

    return (
        f"Your upcoming events are between "
        f"{start_date} and {end_date}: <br/> {', '.join(event_list)} <br/> "
        f"<a href='/logout'><button>Logout</button></a>"
    )



if __name__ == '__main__':
    app.run()
