import os
from flask import Flask, request, jsonify, render_template
import strava
app = Flask(__name__)

@app.route("/")
def start():
    return {"message": "HelloWebhook is listening"}

@app.route("/health")
def health_check():
    return {"status": "healthy"}


VERIFY_TOKEN = "STRAVA"
python_script = "strava.py"

@app.route('/webhook', methods=['GET'])
def verify_webhook():
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')

    if mode and token:
        if mode == 'subscribe' and token == VERIFY_TOKEN:
            print("Webhook verified")
            return jsonify({"hub.challenge": challenge})
        else:
            return "Invalid verification token", 403

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    # data = request.get_json()
    latest_activity_id = request.args.get('object_id')
    print("Webhook event received with activity:", latest_activity_id)

    strava.get_latest_activities()
    # subprocess.run(["python", python_script], check=True, capture_output=True)
    # stdout = subprocess.check_output(["python", python_script])  # Capture output for logging
    # print("Python script output:", stdout.decode())

    return jsonify({"message": "EVENT_RECEIVED"}), 200