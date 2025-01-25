from datetime import datetime
import os
import secrets
from flask import Flask, make_response, redirect, request, session, url_for, jsonify, render_template
import requests
import strava
import json
import database
import logging
from test_strava_activity import athlete_id

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Adjust logging level as needed

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Set a secure secret key
# Constants
VERIFY_TOKEN = "STRAVA"
DATA_FILE = "refresh_tokens.json"
STRAVA_CLIENT_ID = os.environ.get('CLIENT_ID')
STRAVA_CLIENT_SECRET = os.environ.get('CLIENT_SECRET')
# Routes
@app.route("/")
def start():
   return render_template('index.html')

@app.route("/training")
def training():
    
    return render_template('training_landing_pg.html')

@app.route("/connectStrava")
def connect_strava():
    session_token = request.cookies.get('session_token')
    if not session_token:
        auth_url = (
        f"https://www.strava.com/oauth/authorize?"
        f"client_id={STRAVA_CLIENT_ID}&" 
        f"redirect_uri={url_for('strava_callback', _external=True)}&"
        f"response_type=code&"
        f"approval_prompt=auto&"
        f"scope=activity:read_all,activity:write"
    )
        return redirect(auth_url)
    else:
        client = database.initiate_mango_connection()
        athlete_id, expires_at, refresh_token, previous_workout_plan, athlete_name = database.check_session_token_in_data(client, session_token)
        session['athlete_id'] = athlete_id
        session['athlete_name'] = athlete_name
        
        if datetime.now() > expires_at:
            # Refresh access token silently
            new_token = requests.post(
                'https://www.strava.com/oauth/token',
                data={
                    'client_id': STRAVA_CLIENT_ID,
                    'client_secret': STRAVA_CLIENT_SECRET,
                    'grant_type': 'refresh_token',
                    'refresh_token': refresh_token
                }
            ).json()

            # Update tokens
            refresh_token = new_token['refresh_token']
            expires_at = datetime.fromtimestamp(new_token['expires_at'])
            database.update_tokens(client, session_token, expires_at, refresh_token)  

        database.close_client(client)
        if previous_workout_plan=='':
            return redirect('/training_qna')
        else:
            return redirect('/training_dashboard')
       
    
@app.route("/training_qna")
def training_qna():
    # Retrieve athlete_id from session
    athlete_id = session.get('athlete_id')
    athlete_name = session.get('athlete_name')
    if not athlete_id:
        return redirect('/connectStrava')  # Redirect if no session
    
    # Render the template with athlete_id
    return render_template('training_qna.html', athlete_id=athlete_id, athlete_name=athlete_name)


@app.route("/training_dashboard")
def training_dashboard():  
     # Retrieve athlete_id from session
    athlete_id = session.get('athlete_id')
    athlete_name = session.get('athlete_name')
    if not athlete_id:
        return redirect('/connectStrava')  # Redirect if no session
    
    # Render the template with athlete_id
    return render_template('training_dashboard.html', athlete_id=athlete_id, athlete_name=athlete_name)

@app.route('/strava-callback')
def strava_callback():
    error = request.args.get('error')
    if error:
        return f"Strava authorization failed: {error}"
    
    auth_code = request.args.get('code')
    
    
    if not auth_code:
        return "Authorization code missing", 400
    
    try:
        token_response = exchange_code_for_token(auth_code)
        athlete = token_response.get('athlete')
        athlete_id = athlete.get('id')  
        athlete_name = f"{athlete.get('firstname')} {athlete.get('lastname')}"
        refresh_token = token_response.get('refresh_token')
        session['athlete_id'] = athlete_id
        session['athlete_name'] = athlete_name
        
        if 'errors' in token_response:
            return f"Strava token exchange failed: {token_response['errors']}", 400
        
        try:
            session_token = secrets.token_urlsafe(64)
           
            data = {
                "athlete_id":athlete_id,
                "refresh_token": refresh_token,
                "athlete_name": athlete_name,
                "session_token": session_token,
                "expires_at": datetime.fromtimestamp(token_response['expires_at']),
                "previous_workout_plan": ''
            }
            
            response = make_response(redirect('/training_qna', athelete_id=athlete_id))
            response.set_cookie(
                'session_token',
                session_token,
                max_age=365*24*3600,
                httponly=True,
                secure=True
            )
            
            client = database.initiate_mango_connection()
            message = database.save_athlete_data(client, data)
            database.close_client(client)
            
            return response
        except IOError as e:
            return jsonify({"error": str(e)}), 500
    
    except Exception as e:
        return f"Error connecting to Strava: {str(e)}", 500

def exchange_code_for_token(code):
    data = {
        'client_id': STRAVA_CLIENT_ID,
        'client_secret': STRAVA_CLIENT_SECRET,
        'code': code,
        'grant_type': 'authorization_code'
    }
    STRAVA_TOKEN_URL = f"https://www.strava.com/oauth/token"
    response = requests.post(STRAVA_TOKEN_URL, data=data)
    return response.json()


@app.route("generatePlan", methods=['POST'])
def generate_plan():
    form_data = request.json
    month_1_activities, month_2_activities, month_3_activities = strava.get_activities_for_period(12, athlete_id, sport_type='Run')
    all_activities_3_mnths = month_1_activities + month_2_activities + month_3_activities
    top_3_long_runs = strava.get_top_three_longest_runs(all_activities_3_mnths)
    races=strava.get_races(all_activities_3_mnths)

    athlete_goal_prompt = generate_goal_prompt(form_data, top_3_long_runs, races)
    
def generate_goal_prompt(form_data, top_3_long_runs, races):
    goal_type = form_data.get('goalType', '') 
    goal = form_data.get('goal', '')
    target_date = form_data.get('targetDate', '')
    training_days = form_data.get('trainingDays', '')
    fitness_level = form_data.get('fitnessLevel', '')
    recent_performance = form_data.get('recentPerformance', '')
    strength_sessions = form_data.get('strengthSessions', '')
    time_commitment = form_data.get('timeCommitment', '')
    injuries = form_data.get('injuries', '')
    preferences = form_data.get('preferences', '')
    special_conditions = form_data.get('specialConditions', '')
    other_info = form_data.get('otherInfo', '')
    
    goal_prompt = f"""
    You are a professional running coach. You have been hired by a client to help them train for a running goals.
    Summarise clients goal in a actionable and measurable way. Clients goal wants to train for {goal} by {target_date}.
    The client is currently at a fitness level of {fitness_level} and  can commit {time_commitment} per week for training.
    In past 3 months, longest 3 runs of the client are {top_3_long_runs}.
    Athlete has recently performed {recent_performance}, and race performances from strava are {races}. 
    He/she can train for {training_days} days in a week and can do {strength_sessions} strength sessions per week.
    The client has {injuries} and {special_conditions} that you need to consider while creating the plan.
    The client prefers {preferences} and has {other_info} that you need to consider while creating the plan.
    """
    
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

if __name__ == "__main__":
    app.run(debug=True, port=int(os.getenv("PORT", 80)))
