import os
from flask import Flask, request, jsonify
import strava

app = Flask(__name__)
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(port=port)
    print("Webhook is listening on port", port)  # Log listening message

@app.get("/")
async def root():
    return {"message": "Hello, world!"}

@app.get("/health")
async def health_check():
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

if __name__ == "__main__":
    import uvicorn  # Or gunicorn for production
    # Note: You don't need a Procfile for Vercel deployment
    
    # Environment variables will be injected by Vercel during deployment
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
    print("webhook is listening")