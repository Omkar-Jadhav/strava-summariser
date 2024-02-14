import os
from flask import Flask, request, jsonify
import strava

app = Flask(__name__)

@app.get("/")
async def root():
    return {"message": "Hello, world!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}


VERIFY_TOKEN = "STRAVA"
python_script = "strava.py"

# @app.route('/webhook', methods=['GET'])
# def verify_webhook():
#     mode = request.args.get('hub.mode')
#     token = request.args.get('hub.verify_token')
#     challenge = request.args.get('hub.challenge')

#     if mode and token:
#         if mode == 'subscribe' and token == VERIFY_TOKEN:
#             print("Webhook verified")
#             return jsonify({"hub.challenge": challenge})
#         else:
#             return "Invalid verification token", 403

