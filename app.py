from flask import Flask, redirect, request, session, jsonify
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import os

app = Flask(__name__)
app.secret_key = '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'  # Replace with a secure secret key

# Path to your credentials.json file downloaded from Google Cloud Console
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # Allow HTTP for local testing
CLIENT_SECRETS_FILE = "credentials.json"
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
REDIRECT_URI = "https://cal-2.onrender.com/oauth2callback"

# Root route
@app.route('/')
def home():
    return "Welcome to the Google Calendar Integration App!"

# Step 1: Start OAuth Flow
@app.route('/connect-calendar')
def connect_calendar():
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    session['state'] = state
    return redirect(authorization_url)

# Step 2: Handle OAuth Callback
@app.route('/oauth2callback')
def oauth2callback():
    state = session['state']
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        state=state,
        redirect_uri=REDIRECT_URI
    )
    flow.fetch_token(authorization_response=request.url)

    credentials = flow.credentials
    session['credentials'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }
    return redirect('/fetch-events')

# Step 3: Fetch Calendar Events
@app.route('/fetch-events')
def fetch_events():
    if 'credentials' not in session:
        return redirect('/connect-calendar')

    creds_data = session['credentials']
    creds = google.oauth2.credentials.Credentials(**creds_data)
    service = build('calendar', 'v3', credentials=creds)

    events_result = service.events().list(
        calendarId='primary',
        timeMin='2025-03-01T00:00:00Z',
        timeMax='2025-03-31T23:59:59Z',
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])
    return jsonify(events)

if __name__ == '__main__':
    app.run(port=5000, debug=True)
