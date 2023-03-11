import os
import pathlib
from datetime import datetime, time

import google.auth.transport.requests
import pytz
import requests
from config import Config
from flask import (
    Flask,
    abort,
    g,
    redirect,
    request,
    session,
)
from flask import Flask
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import psycopg2.pool
from pip._vendor import cachecontrol

app = Flask(__name__)
app.config.from_object(Config)

# Database configuration
# Create a connection pool
db_pool = psycopg2.pool.SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    host=app.config['DB_HOST'],
    port=app.config['DB_PORT'],
    dbname=app.config['DB_NAME'],
    user=app.config['DB_USER'],
    password=app.config['DB_PASSWORD']
)

@app.before_request
def before_request():
    # Get a connection from the pool and save it to the global `g` object
    g.db_conn = db_pool.getconn()

@app.after_request
def after_request(response):
    # Return the connection to the pool
    db_pool.putconn(g.db_conn)
    return response



# OAUTH CONFIGURATION FILES
app.secret_key = app.config['APP_SECRET_KEY'] # make sure this matches with that's in client_secret.json

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1" # to allow Http traffic for local dev

GOOGLE_CLIENT_ID = app.config['GOOGLE_CLIENT_ID']

client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid", "https://www.googleapis.com/auth/calendar"],
    redirect_uri="http://localhost:5000/callback"
)



def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return abort(401)  # Authorization required
        else:
            return function()

    return wrapper


def get_calendar_service():
    credentials = flow.credentials
    service = build("calendar", "v3", credentials=credentials)
    print(f"Access token for Calendar API: {credentials.token}")
    return service


@app.route("/login")
def login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)

@app.route("/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)

    if not session["state"] == request.args["state"]:
        abort(500)  # State does not match!

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )

    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")
    print(f"Google OAUTH token: {credentials._id_token}")
    return redirect("/protected_area")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")



@app.route("/")
def index():
    return "Hello World <a href='/login'><button>Login</button></a>"


@app.route("/protected_area", methods=["GET", "POST"])
@login_is_required
def protected_area():
    if request.method == "POST":
        start_date_str = request.form.get("start_date")
        end_date_str = request.form.get("end_date")

        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()

            if start_date > end_date:
                raise ValueError("Start date should be before end date.")
        except (ValueError, TypeError):
            return "Invalid date format. Please use YYYY-MM-DD format."

        service = get_calendar_service()
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
            f"Hello {session['name']}! <br/> <br/> Your upcoming events are between "
            f"{start_date} and {end_date}: <br/> {', '.join(event_list)} <br/> "
            f"<a href='/logout'><button>Logout</button></a>"
        )

    return """
        <html>
            <body>
                <form method="post">
                    Start date: <input type="date" name="start_date" required><br>
                    End date: <input type="date" name="end_date" required><br>
                    <input type="submit" value="Submit">
                </form>
            </body>
        </html>
    """

@app.route('/users')
def get_users():
    cur = g.db_conn.cursor()
    cur.execute('SELECT * FROM Users')
    users = cur.fetchall()
    cur.close()
    return str(users)


if __name__ == '__main__':
    app.run()
