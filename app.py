from datetime import datetime, timedelta
import itertools
import os
import re
import secrets
from string import Template
from flask import Flask, make_response, redirect, request, session, url_for, jsonify, render_template,app
import requests
import ai
import strava
import json
import database
import logging
import strava_v2_testing

import training_utils
import utils
import workout_classifier_testing
from training_utils import format_prompt_for_llm
import markdown2
# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Adjust logging level as needed
STRAVA_CLIENT_ID = os.environ.get('CLIENT_ID')
app = Flask(__name__)
# app.config['PERMANENT_SESSION_LIFETIME'] = 20  # 30 minutes
app.config["SESSION_PERMANENT"] = True
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=3)
app.secret_key = os.urandom(24)  # Set a secure secret key
app.config.update(
    SESSION_COOKIE_SAMESITE='Lax',  # Allows cookies in same-site context
    SESSION_COOKIE_SECURE=False     # Set to True in production (HTTPS)
)
@app.before_request
def make_session_permanent():
    session.permanent = True  # ✅ Move inside a request context

# Constants
VERIFY_TOKEN = "STRAVA"
DATA_FILE = "refresh_tokens.json"


SESSION_KEYS = {
    'form_data': 'form_data',
    'activities': 'activities',
    'analysis': 'analysis',
    'goals': 'goals',
    'access_token': 'access_token',
    'past_3m_summ':'past_3m_summ',
    'baseline_stats':'baseline_stats',
    'past_month_details':'past_month_details',
    'athlete_id':'athlete_id',
    'athlete_name':'athlete_name',
}

# Routes
@app.route("/")
def start():
   return render_template('index.html')

@app.route("/training")
def training():
    
    return render_template('training_landing_pg.html')

@app.route("/connectStrava")
def connect_strava():
    logger.info("Inside connect strava api call")
    logger.info(f"{url_for('strava_callback', _external=True)}")
    session_token = request.cookies.get('session_token')
    athlete_id = None
    
    if session_token:
        client = database.initiate_mango_connection()
        athlete_id, expires_at, refresh_token, previous_workout_plan, athlete_name = database.check_session_token_in_data(client, session_token)
    
    if not athlete_id:
        logger.info("Session token not found")
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
        logger.info("Session token found")
        
        session['athlete_id'] = athlete_id
        session['athlete_name'] = athlete_name  

        database.update_tokens(client, session_token, athlete_id)  

        database.close_client(client)
        if previous_workout_plan=='':
            logger.info("previous workout plan not found")
            return redirect('/training_qna')
        else:
            logger.info("Previous workout plan found")
            return redirect(url_for('training_dashboard', athlete_id=athlete_id))
       
    
@app.route("/training_qna")
def training_qna():
    # Retrieve athlete_id from session
    athlete_id = session.get('athlete_id')
    athlete_name = session.get('athlete_name')
    if not athlete_id:
        return redirect('/connectStrava')  # Redirect if no session
    
    # Render the template with athlete_id
    return render_template('training_qna.html', athlete_id=athlete_id, athlete_name=athlete_name)


@app.route("/training_dashboard/<athlete_id>")
def training_dashboard(athlete_id=None):  
     # Retrieve athlete_id from session
    athlete_id = athlete_id or session.get('athlete_id')
    athlete_name = session.get('athlete_name')
    if "overview" in session: 
        overview = session.get('overview')
    else:
        overview = ""
   
    next_week_plan = session.get('next_week_workout_plan')
    goal_summary = session.get('goal_summary')
    dates = session.get('dates')
    if next_week_plan is None or next_week_plan=="":
        logger.info("next week plan is not available")
        dates,next_week_plan, notes,goal_summary = database.get_athelte_training_details(athlete_id)
    
    next_week_plan =  training_utils.workout_days_plan_to_markdown(next_week_plan, dates, notes, overview)
    next_week_plan = markdown2.markdown(next_week_plan)
    if goal_summary:
        goal_summary =  markdown2.markdown(goal_summary)
    return render_template('training_dashboard.html', athlete_name = "Omkar Jadhav",next_week_plan=next_week_plan, goal_summary=goal_summary, dates=dates, athlete_id=athlete_id)


@app.route('/process_user_input', methods=['POST'])
def process_user_input():
    chat_history = request.json.get('messages')
    current_plan =request.json.get('next_week_plan')
    goal_summary = request.json.get('goal_summary')
    athlete_id =request.json.get('athlete_id')
    dates = request.json.get('dates')

    athlete_message, chat_history = utils.get_last_athlete_msg_and_chat(chat_history)
    # Step 1: Check relevance
    is_athlete_msg_relevant = utils.is_user_input_relevant(athlete_message, current_plan, goal_summary,chat_history) 
    
    if is_athlete_msg_relevant == 'relevant':
        # Step 2: Call GPT for plan update
        gpt_response, is_plan_updated = training_utils.work_on_user_query(athlete_message, current_plan, goal_summary)
        
        if is_plan_updated:
            _, workout_json,notes = utils.parse_json_workout_plan(gpt_response)
            if workout_json: 
                database.save_workout_plan(athlete_id, workout_json, dates,notes=notes)
            response = training_utils.workout_plan_to_markdown(gpt_response)
           
        response = markdown2.markdown(response)
        
        response = response.replace("\n","")
        # Step 3: Update the plan (optional: save to database)  
        # For now, we'll just return the GPT response
        return jsonify({
            "relevant": True,
            "gpt_response": response,
            "is_plan_updated":is_plan_updated
        })
        
    else:
        return jsonify({
            "relevant": False,
            "gpt_response": "Your input is not relevant to the plan."
        })


@app.route('/strava-callback')
def strava_callback():
    error = request.args.get('error')
    if error:
        return f"Strava authorization failed: {error}"
    
    auth_code = request.args.get('code')
    
    
    if not auth_code:
        return "Authorization code missing", 400
    
    try:
        token_response = strava.exchange_code_for_token(auth_code)
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
                "expires_at": datetime.fromtimestamp(token_response['expires_at'])
            }
            
            last_training_plan = database.get_athelte_training_details(athlete_id)
            if last_training_plan:
                response = make_response(redirect(url_for('training_dashboard', athlete_id=athlete_id)))            
            else:
                response = make_response(redirect('/training_qna'))
            
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



@app.route("/generatePlan/checkAthleteStatus", methods=['POST'])
def step1_check_athlete():
    try:
        form_data = request.json
        athlete_id = form_data['athlete_id']
        athlete_name = form_data['athlete_name']
        
        # Check athlete existence
        client = database.initiate_mango_connection()
        exists = database.check_athlete_in_training_data(client, athlete_id)
        database.close_client(client)
        
        access_token = strava.get_access_token(athlete_id)
        # Store initial data in session
        session[SESSION_KEYS['form_data']] = form_data
        session[SESSION_KEYS['access_token']] = access_token
        session[SESSION_KEYS['athlete_id']] = athlete_id
        session[SESSION_KEYS['athlete_name']] = athlete_name
        if exists:
           return jsonify(success=True, next_step='/generatePlan/getNewPlanExisitingUser'), 200
        else:
            return jsonify(success=True, next_step='/generatePlan/getAthleteActivities'), 200
    
    except Exception as e:
        return jsonify(success=False, error=str(e)), 500

@app.route("/generatePlan/getAthleteActivities", methods=['POST'])
def step2_fetch_activities():
    try:
        form_data = session.get(SESSION_KEYS['form_data'])
        access_token = session.get(SESSION_KEYS['access_token'])
        if not form_data:
            return jsonify(success=False, error="Session expired"), 400
            
        athlete_id = form_data['athlete_id']
        
        # Fetch and process Strava data
        # Activity fetching and processing
        headers = {'Authorization': f'Bearer {access_token}'}
        activities = strava.get_activities_for_period(12, athlete_id, 'Run',access_token)
        combined_activities = list(itertools.chain(*activities))
        
        # Activity analysis
        recent_runs = activities[0]
        past_month_runs, baseline_stats = workout_classifier_testing.get_run_type(recent_runs, recent_runs[0], headers)
        
        m2_m3_dtls, _ = workout_classifier_testing.get_run_type(activities[1]+activities[2], activities[0][0], headers)
        # m2_m3_dtls =[]
        combined_dtls =  past_month_runs+m2_m3_dtls
        
        combined_dtls = utils.sort_by_day(combined_dtls)
        past_month_runs = utils.sort_by_day(past_month_runs)
        
        past_3m_runs_details = "\n".join([f"{i+1}. {run_type}" for i, run_type in enumerate(combined_dtls)])
        past_month_details = "\n".join([f"{i+1}. {run_type}" for i, run_type in enumerate(past_month_runs)])
        
        session[SESSION_KEYS['activities']] = {
            'long_runs': strava.get_top_three_longest_runs(combined_activities),
            'races': strava.get_race_details(combined_activities),
            'past_3m_details':past_3m_runs_details
        }
        
        session[SESSION_KEYS['baseline_stats']]=baseline_stats
        session[SESSION_KEYS['past_month_details']]=past_month_details
        
        return jsonify(success=True, next_step='/generatePlan/getGoalSummary'), 200
    
    except Exception as e:
        return jsonify(success=False, error=str(e)), 500
    
@app.route("/generatePlan/getGoalSummary", methods=['POST'])
def step3_analyze_goals():
    try:
        form_data = session.get(SESSION_KEYS['form_data'])
        activities = session.get(SESSION_KEYS['activities'])
        baseline_stats = session.get(SESSION_KEYS['baseline_stats'])
        past_3m_details = activities['past_3m_details']
        
        
        session.pop('activities', None)
        session.pop('form_data', None)
        
        if not form_data or not activities:
            return jsonify(success=False, error="Session expired"), 400
        
        # Generate goal analysis
        goal_prompt = training_utils.generate_goal_prompt(
            form_data, 
            activities['long_runs'], 
            activities['races']
        )
        
        prompt_template = utils.load_prompt('analyse_3m_runs')
        past_3m_prompt = prompt_template.substitute(
            activities=activities['past_3m_details'],
        )
        past_3m_summ_json = ai.get_json_response_from_groq(past_3m_prompt)
        goal_summary_json = ai.get_json_response_from_groq(goal_prompt)
        
        session[SESSION_KEYS['goals']] = goal_summary_json['goal_summary']
        session[SESSION_KEYS['past_3m_summ']]= past_3m_summ_json['past_3m_summary']
        
        return jsonify(success=True, next_step='/generatePlan/getPlan'), 200
        
    except Exception as e:
        return jsonify(success=False, error=str(e)), 500
    
    
@app.route("/generatePlan/getPlan", methods=['POST'])
def step4_generate_plan():
    try:
        past_3m_summ = session.get(SESSION_KEYS['past_3m_summ'])
        goals = session.get(SESSION_KEYS['goals'])
        athlete_id = session.get(SESSION_KEYS['athlete_id'])
        athlete_name = session.get(SESSION_KEYS['athlete_name'])
        baseline_stats = session.get(SESSION_KEYS['baseline_stats'])
        past_month_details = session.get(SESSION_KEYS['past_month_details'])
        
        if not all([past_3m_summ, goals, goals]):
            return jsonify(success=False, error="Session expired"), 400

        # Generate final plan
        prompt = training_utils.format_prompt_for_llm(
            goals, 
            baseline_stats,
            past_3m_summ,
            past_month_details,
        )
        
        session.pop('goals',None)
        session.pop('baseline_stats',None)
        session.pop('past_3m_summ',None)
        session.pop('past_month_details',None)
        
        plan = ai.get_json_response_from_groq(prompt)
        dates,birdseye_view, workout_plan, notes = utils.parse_json_workout_plan(plan)
        
        # Save to database
        database.save_workout_plan(
            athlete_id, 
            workout_plan, 
            dates, 
            goals, notes=notes, overview=birdseye_view
        )
        
        # Cleanup session data
        for key in SESSION_KEYS.values():
            session.pop(key, None)
            
        session['next_week_workout_plan'] = workout_plan
        session['overview'] = birdseye_view
        session['goal_summary'] = goals
        session['athlete_id'] = athlete_id
        session['athlete_name'] =  athlete_name
        session['dates'] = dates
        session.modified = True  # Ensure session is saved
            
        return jsonify({
            "success": True,
            "redirect_url": url_for('training_dashboard', athlete_id=athlete_id)
        }), 200
        
    except Exception as e:
        return jsonify(success=False, error=str(e)), 500


@app.route("/generatePlan/getNewPlanExisitingUser", methods=['POST'])
def get_new_plan_exisiting_user():
    form_data = session.get(SESSION_KEYS['form_data'])
    access_token = session.get(SESSION_KEYS['access_token'])
    athlete_id = form_data['athlete_id']
    athlete_name = form_data['athlete_name']
    
    last_dates,last_week_plan, notes,goal_summary = database.get_athelte_training_details(athlete_id)
    # last_dates = dates_.split("-")
    dates, next_week_plan= training_utils.generate_next_week_plan(last_dates,goal_summary,last_week_plan, athlete_id)
    
    goal_summary = markdown2.markdown(goal_summary)
    next_week_plan = markdown2.markdown(next_week_plan)
    next_week_plan = next_week_plan.replace("\n","")    
        
    session['next_week_workout_plan'] = next_week_plan
    session['goal_summary'] = goal_summary
    session['athlete_id'] = athlete_id
    session['athlete_name'] =  athlete_name
    session['dates'] = dates
    session.modified = True  # Ensure session is saved
    
    # if next_week_avail:
    #     workout_json, dates, notes = utils.parse_workout_plan(next_week_plan)
    #     database.save_workout_plan(athlete_id, workout_json, dates, notes)
        
    return jsonify({
        "success": True,
        "redirect_url": url_for('training_dashboard', athlete_id=athlete_id)  # Redirect to the training dashboard 
    }), 200

    
@app.route("/health")
def health_check():
    return jsonify({"status": "healthy"})

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        return strava.verify_webhook()
    elif request.method == 'POST':
        return strava.handle_webhook()

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

        
@app.route('/getNextWeekPlan', methods=['POST'])
def get_next_week_plan():
    athlete_id = request.json.get('athlete_id')
    last_week_plan =request.json.get('last_week_plan')
    goal_summary = request.json.get('goal_summary') or ''
    last_dates = request.json.get('dates')
    # last_dates = 
    
    next_week_avail = training_utils.check_next_week_avail(last_dates.split("-"))
    if next_week_avail:
        dates, next_week_plan = training_utils.generate_next_week_plan(last_dates, last_week_plan, goal_summary, athlete_id)
        next_week_plan = markdown2.markdown(next_week_plan)
        next_week_plan = next_week_plan.replace("\n","")  
        
    if next_week_avail:
        return  jsonify({
            "next_week_avail": next_week_avail,
            "next_week_plan":next_week_plan,
            "dates":dates,
        })

    else:
        return  jsonify({
            "next_week_avail": next_week_avail,
            "next_week_plan":"Plan will be available next week"
        })



if __name__ == "__main__":
    app.run(debug=True, port=int(os.getenv("PORT", 80)))
