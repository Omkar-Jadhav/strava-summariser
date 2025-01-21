import os
from flask import Flask, request, url_for, jsonify, render_template
import strava
import json
import database
import logging

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Adjust logging level as needed

app = Flask(__name__)

# Constants
VERIFY_TOKEN = "STRAVA"
DATA_FILE = "refresh_tokens.json"

# Routes
@app.route("/")
def start():
    return render_template('index.html')

@app.route("/health")
def health_check():
    return jsonify({"status": "healthy"})

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        return verify_webhook()
    elif request.method == 'POST':
        return handle_webhook()

@app.route('/getCode')
def get_code():
    return render_template('code.html')

@app.route('/saveRefreshToken', methods=['POST'])
def save_refresh_token():
    data = request.get_json()
    refresh_token = data.get('refresh_token')
    athlete = data.get('athlete')

    if not (refresh_token and athlete):
        return jsonify({"error": "Invalid data format"}), 400

    athlete_id = athlete.get('id')
    athlete_name = f"{athlete.get('firstname')} {athlete.get('lastname')}"

    try:
        client = database.initiate_mango_connection()
        token = database.check_athlete_in_data(client, athlete_id)
        database.close_client(client)
        
        if token is not None:
            redirect_url = url_for('already_authorized', _external=True)
        else:
            data = {
                "athlete_id":athlete_id,
                "refresh_token": refresh_token,
                "athlete_name": athlete_name
            }
            message = database.save_athlete_data(client, data)
            redirect_url = url_for('auth_success_page', _external=True)

        return jsonify({'redirect_url': redirect_url}), 200

    except IOError as e:
        return jsonify({"error": str(e)}), 500

@app.route('/authSuccessPage')
def auth_success_page():
    return render_template('authSuccessPage.html')    

@app.route('/alreadyAuthorized')
def already_authorized():
    return render_template('alreadyAuthorized.html')    

# Helper Functions
def verify_webhook():
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')

    if mode == 'subscribe' and token == VERIFY_TOKEN:
        return jsonify({"hub.challenge": challenge}), 200
    else:
        return "Invalid verification token", 403

def handle_webhook():
    latest_activity_id = request.json.get('object_id')
    athlete_id = request.json.get('owner_id')
    logger.info(f"request inputs are {request.args}")
    print(f"Webhook event received with activity:{latest_activity_id} for athlete ID: {athlete_id}")
    inputs={
        "activity_id":latest_activity_id,
        "athlete_id":athlete_id
    }
    
    logger.info(f"Inputs were{inputs}")
    strava.get_latest_activities(inputs)
    return jsonify({"message": "EVENT_RECEIVED"}), 200

# if __name__ == "__main__":
#     app.run(debug=True, port=int(os.getenv("PORT", 80)))
