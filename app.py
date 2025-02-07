from datetime import datetime
import itertools
import os
import re
import secrets
from flask import Flask, make_response, redirect, request, session, url_for, jsonify, render_template,app
import requests
import ai
import strava
import json
import database
import logging
import strava_v2_testing

import workout_classifier_testing
from strava_v2_testing import format_prompt_for_llm
import markdown2
# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Adjust logging level as needed
app.config['PERMANENT_SESSION_LIFETIME'] = 180  # 30 minutes
session.permanent = True
app = Flask(__name__)
app.secret_key = os.urandom(24)  # Set a secure secret key
app.config.update(
    SESSION_COOKIE_SAMESITE='Lax',  # Allows cookies in same-site context
    SESSION_COOKIE_SECURE=False     # Set to True in production (HTTPS)
)
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
    logger.info("Inside connect strava api call")
    logger.info(f"{url_for('strava_callback', _external=True)}")
    session_token = request.cookies.get('session_token')
    
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
        
        # Refresh access token silently
        # access_token = requests.post(
        #     'https://www.strava.com/oauth/token',
        #     data={
        #         'client_id': STRAVA_CLIENT_ID,
        #         'client_secret': STRAVA_CLIENT_SECRET,
        #         'grant_type': 'refresh_token',
        #         'refresh_token': refresh_token
        #     }
        # ).json()

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
   
    next_week_plan = session.get('next_week_workout_plan')
    goal_summary = session.get('goal_summary')
    dates = session.get('dates')
    if next_week_plan is None or next_week_plan=="":
        logger.info("next week plan is not available")
        dates,next_week_plan, notes,goal_summary = database.get_athelte_training_details(athlete_id)
    # next_week_plan = test_plan_data.next_week_plan
    # goal_summary = test_plan_data.goal_summary
    # dates = test_plan_data.dates
    # athlete_id = test_plan_data.athlete_id
    # next_week_plan = join_dict_keys_values(next_week_plan)
    next_week_plan =  markdown2.markdown(next_week_plan)
    if goal_summary:
        goal_summary =  markdown2.markdown(goal_summary)
    return render_template('training_dashboard.html', athlete_name = "Omkar Jadhav",next_week_plan=next_week_plan, goal_summary=goal_summary, dates=dates, athlete_id=athlete_id)

def join_dict_keys_values(data):
    if isinstance(data, dict):  # Check if it's a dictionary
        return " ".join(f"{key} {value}" for key, value in data.items())
    
    try:
        # Check if it's a valid JSON string and convert it to a dictionary
        # data = json.loads(data)  
        if isinstance(data, dict):
            return " ".join(f"{key} {value}" for key, value in data.items())
    except (json.JSONDecodeError, TypeError):
        pass
    
    return data

@app.route('/process_user_input', methods=['POST'])
def process_user_input():
    chat_history = request.json.get('messages')
    current_plan =request.json.get('next_week_plan')
    goal_summary = request.json.get('goal_summary')
    athlete_id =request.json.get('athlete_id')
    dates = request.json.get('dates')

    athlete_message, chat_history = get_last_athlete_msg_and_chat(chat_history)
    # Step 1: Check relevance
    is_athlete_msg_relevant = is_user_input_relevant(athlete_message, current_plan, goal_summary,chat_history) 
    
    if is_athlete_msg_relevant == 'relevant':
        # Step 2: Call GPT for plan update
        gpt_response, is_plan_updated = work_on_user_query(athlete_message, current_plan, goal_summary)
        
        if is_plan_updated.lower()=='true':
            workout_json, _,notes = parse_workout_plan(gpt_response)
            if workout_json:
                database.save_workout_plan(athlete_id, workout_json, dates,notes=notes)
            
        gpt_response = markdown2.markdown(gpt_response)
        gpt_response = gpt_response.replace("\n","")
        # Step 3: Update the plan (optional: save to database)  
        # For now, we'll just return the GPT response
        return jsonify({
            "relevant": True,
            "gpt_response": gpt_response,
            "is_plan_updated":is_plan_updated
        })
        
    else:
        return jsonify({
            "relevant": False,
            "gpt_response": "Your input is not relevant to the plan."
        })

def parse_workout_plan(text):
    # Extracting dates
    date_start_idx = text.find("Dates:")
    if date_start_idx != -1:
        date_end_idx = text.find("\n", date_start_idx)
        date_range = text[date_start_idx + len("Dates:"):date_end_idx].strip()
        dates = date_range.split(" - ") if date_range else None
        if dates:
            dates = "-".join(dates)
    else:
        dates = None

    # Extracting the workout plan (between "Workout Plan:" and "Notes:")
    workout_plan_start_idx = text.find("Workout Plan:")
    if workout_plan_start_idx != -1:
        workout_plan_end_idx = text.find("Notes:", workout_plan_start_idx)
        if workout_plan_end_idx == -1:  # If "Notes" is not found, assume it's the end of the text
            workout_plan_end_idx = len(text)
        workout_plan = text[workout_plan_start_idx + len("Workout Plan:"):workout_plan_end_idx].strip()
    else:
        workout_plan = None

    # Extracting notes (everything after "Notes:")
    notes_start_idx = text.find("Notes:")
    if notes_start_idx != -1:
        notes = text[notes_start_idx + len("Notes:"):].strip()
    else:
        notes = None

    return workout_plan, dates, notes


def parse_workout_plan_(text):
    # Extracting Dates
    dates = re.search(r"\s*(\d{2}/\d{2}/\d{4})\s*-\s*(\d{2}/\d{2}/\d{4})", text)
    dates = dates.groups() if dates else None
    if dates:
        dates = "-".join(dates)

    # Extracting Workouts
    workouts = {}
    workout_pattern = r"#### (\w+)\s*-([^#]+)"
    workout_matches = re.findall(workout_pattern, text)  
    for day, details in workout_matches:
        workouts[day] = details.strip()

    # Extracting Notes
    notes = []
    notes_section = re.search(r"### Notes:\n([\s\S]+)", text)
    if notes_section:
        notes = [note.strip() for note in notes_section.group(1).split("\n*") if note]

    return workouts,dates , notes


def get_last_athlete_msg_and_chat(chat_history):
    if chat_history:
    # Get the last athlete input
        last_athlete_message = chat_history[-1]
        if last_athlete_message['sender'] == 'Athlete':
            last_athlete_input = last_athlete_message['message']
            # Combine all previous messages into a single string
            previous_messages = " ".join(
                f"{msg['sender']}: {msg['message']}" 
                for msg in chat_history[:-1]
            )
        else:
            # No Athlete message at the end
            previous_messages = " ".join(
                f"{msg['sender']}: {msg['message']}" 
                for msg in chat_history
        )
    else:
        # Empty chat history case
        previous_messages = "No previous chat history available."
        
    return last_athlete_input, previous_messages

def work_on_user_query(user_input, current_plan, goal_summary):
    prompt=f"""
    Act as a professional running coach. The user may have queries, suggestions, inputs, or changes regarding the training plan you previously provided. Today is {datetime.now().strftime("%B %d, %Y")}  and the day is {datetime.today().strftime('%A')}.

Your task is to respond to these queries, incorporating the athlete’s goals and needs. If there is a change in the plan, provide the updated version for the entire week, reflecting any modifications. For general questions about training, just respond directly. 

To update the workout plan, follow these instructions:

Generate a complete workout plan: Include the type of runs (e.g., intervals, tempo), distance, pace, and other relevant details for each day.
Consider a holistic approach: Address the athlete’s strengths, weaknesses, and specific requirements.
Ensure injury prevention: Strive to keep the athlete injury-free while improving fitness levels.
Incorporate strength and mobility workouts: Add these workouts as needed, based on the athlete’s requirements. Specify the type of exercises for strength and mobility sessions.
Include rest days: Ensure proper recovery is accounted for, including rest days.
Cover all days of the week: Make sure every day in the plan is detailed.

Output Format if the workout plan is NOT updated:
'Response: Direct response to the query/suggestions/inputs.
is_plan_updated: False (if the plan was updated).'

Output Format if the workout plan is updated:
'Response: 
Dates: Specify the date range (e.g., DD/MM/YYYY - DD/MM/YYYY) provided from current plan.
Workout Plan: Detailed plan for each day of the week
is_plan_updated: True'

Additional Notes:
Use #### to bold important text.
Ensure subitems are properly bullet-pointed.
Keep responses simple and focused on the athlete’s needs.
Ensure the dates are added from the current plan.
Here is the athlete's current plan:
{current_plan}
Athlete's goal is:
{goal_summary}
Athlete's input is:
{user_input}

Ensure that -
- the output is in the desired format
- is_plan_updated flag is at the end of the message.
- The output format is returned in the correct format.

Take a moment and understand the instructions again.
"""
    gpt_response = ai.get_response_from_groq(prompt)
    response, is_plan_updated = extract_response_and_plan_status(gpt_response)
    
    return response, is_plan_updated
    

def extract_response_and_plan_status(gpt_output):
    # Find the position of the "Response:" keyword
    response_start_idx = gpt_output.find("Response:")
    if response_start_idx == -1:
        return None, None  # Return None if "Response:" is not found
    
    # Find the position of the next line starting with "is_plan_updated:"
    is_plan_updated_start_idx = gpt_output.find("is_plan_updated:", response_start_idx)
    if is_plan_updated_start_idx == -1:
        # If "is_plan_updated:" is not found, assume it’s at the end of the string
        is_plan_updated_start_idx = len(gpt_output)
    
    # Extract the response text between "Response:" and the next part
    response = gpt_output[response_start_idx + len("Response: "):is_plan_updated_start_idx].strip()
    
    # Extract the value of is_plan_updated
    is_plan_updated_text = gpt_output[is_plan_updated_start_idx + len("is_plan_updated:"):].strip()

    # Ensure we only extract 'True' or 'False' cleanly
    is_plan_updated = None
    for word in is_plan_updated_text.split():
        if word in {"True", "False"}:
            is_plan_updated = word
            break  # Stop at the first valid boolean value

    return response, is_plan_updated

def is_user_input_relevant(user_input, next_week_plan, goal_summary, messages):
    prompt=f"""
    You are a chat reviewer. 
    The chat you have to review is in between an athlete and a coach. You have to predict if the athlete input is relevant with the discussion or not. You are provided with athlete goal summary, his next weeks plan coach has provided, previous chat discussion.
    The athlete may ask for queries/suggestions/changes/questions/details/strategies etc.
    If the user input is relevant with the discussion you have return only one word - "relevant". 
    If the user input is not relevatnt with discussion you have to return only following words - "not relevant" 
    The output should only "relevant" or "not relevant", and nothing else no explanation is required.
    
    Here's the chat history - {messages}
    Athlete goal is  -{goal_summary}
    Next weeks plan is -  {next_week_plan}
    The user input for this discussion is - {user_input}
    """
    
    is_relevant = ai.get_response_from_groq(prompt)
    return is_relevant

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

SESSION_KEYS = {
    'form_data': 'form_data',
    'activities': 'activities',
    'analysis': 'analysis',
    'goals': 'goals',
    'access_token': 'access_token',
    'past_3m_summ':'past_3m_summ',
}

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
        
        past_3m_runs_details = "\n".join([f"{i+1}. {run_type}" for i, run_type in enumerate(combined_dtls)])
        past_month_details = "\n".join([f"{i+1}. {run_type}" for i, run_type in enumerate(past_month_runs)])
        
        session[SESSION_KEYS['activities']] = {
            'baseline_stats': baseline_stats,
            'past_month_details': past_month_details,
            'long_runs': strava.get_top_three_longest_runs(combined_activities),
            'races': strava.get_race_details(combined_activities),
            'past_3m_details':past_3m_runs_details
        }
        
        return jsonify(success=True, next_step='/generatePlan/getGoalSummary'), 200
    
    except Exception as e:
        return jsonify(success=False, error=str(e)), 500
    
@app.route("/generatePlan/getGoalSummary", methods=['POST'])
def step3_analyze_goals():
    try:
        form_data = session.get(SESSION_KEYS['form_data'])
        activities = session.get(SESSION_KEYS['activities'])
        if not form_data or not activities:
            return jsonify(success=False, error="Session expired"), 400
        
        # Generate goal analysis
        goal_prompt = generate_goal_prompt(
            form_data, 
            activities['long_runs'], 
            activities['races']
        )
        
        past_3m_summarised = ai.analyse_past_3m_runs(activities['past_3m_details'], activities['baseline_stats'])
        goal_summary = ai.get_response_from_groq(goal_prompt)
        
        session[SESSION_KEYS['goals']] = goal_summary
        session[SESSION_KEYS['past_3m_summ']]= past_3m_summarised
        
        return jsonify(success=True, next_step='/generatePlan/getPlan'), 200
        
    except Exception as e:
        return jsonify(success=False, error=str(e)), 500
    
    
@app.route("/generatePlan/getPlan", methods=['POST'])
def step4_generate_plan():
    try:
        form_data = session.get(SESSION_KEYS['form_data'])
        activities = session.get(SESSION_KEYS['activities'])
        past_3m_summ = session.get(SESSION_KEYS['past_3m_summ'])
        goals = session.get(SESSION_KEYS['goals'])
        athlete_id = form_data['athlete_id']
        athlete_name = form_data['athlete_name']
        if not all([form_data, activities, goals]):
            return jsonify(success=False, error="Session expired"), 400

        # Generate final plan
        prompt = strava_v2_testing.format_prompt_for_llm(
            goals, 
            activities['baseline_stats'],
            past_3m_summ,
            activities['past_month_details'],
        )
        plan = ai.get_response_from_groq(prompt)
        workout_json, dates, notes = parse_workout_plan(plan)
        
        # Save to database
        database.save_workout_plan(
            form_data['athlete_id'], 
            workout_json, 
            dates, 
            goals, notes=notes
        )
        
        # Cleanup session data
        for key in SESSION_KEYS.values():
            session.pop(key, None)
            
        session['next_week_workout_plan'] = plan
        session['goal_summary'] = goals
        session['athlete_id'] = athlete_id
        session['athlete_name'] =  athlete_name
        session['dates'] = dates
        session.modified = True  # Ensure session is saved
            
        return jsonify({
            "success": True,
            "redirect_url": url_for('training_dashboard', athlete_id=form_data['athlete_id'])
        }), 200
        
    except Exception as e:
        return jsonify(success=False, error=str(e)), 500


@app.route("/generatePlan/getNewPlanExisitingUser", methods=['POST'])
def get_new_plan_exisiting_user():
    form_data = session.get(SESSION_KEYS['form_data'])
    access_token = session.get(SESSION_KEYS['access_token'])
    athlete_id = form_data['athlete_id']
    athlete_name = form_data['athlete_name']
    
    dates_,last_week_plan, notes,goal_summary = database.get_athelte_training_details(athlete_id)
    past_week_activity_dtls_ = strava.get_activities_for_period(1, athlete_id, sport_type='Run', access_token=access_token)
    past_week_activity_dtls= "\n".join([f"{i+1}. {run_type}" for i, run_type in enumerate(past_week_activity_dtls_)])
    dates = dates_.split("-")
    next_week_avail, next_week_plan= generate_next_week_plan(dates,goal_summary,last_week_plan,past_week_activity_dtls, athlete_id)
    
    session['next_week_workout_plan'] = next_week_plan
    session['goal_summary'] = goal_summary
    session['athlete_id'] = athlete_id
    session['athlete_name'] =  athlete_name
    session['dates'] = dates
    session.modified = True  # Ensure session is saved
    
    if next_week_avail:
        workout_json, dates, notes = parse_workout_plan(next_week_plan)
        database.save_workout_plan(athlete_id, workout_json, dates, notes)
        
    return jsonify({
        "success": True,
        "redirect_url": url_for('training_dashboard', athlete_id=athlete_id)  # Redirect to the training dashboard 
    }), 200

# @app.route("/generatePlan", methods=['POST'])
# def generate_plan_for_new_user():
#     try:
#         form_data = request.json
#         athlete_id = form_data.get('athlete_id', '')
#         athlete_name = form_data.get('athlete_name','')
#         client = database.initiate_mango_connection()
#         athlete_present_in_training =database.check_athlete_in_training_data(client, athlete_id)
#         database.close_client(client)
        
#         if not athlete_present_in_training:
            
#             access_token = strava.get_access_token(athlete_id)
#             headers = {'Authorization': f'Bearer {access_token}'} 
            
#             all_activities_3_mnths = strava.get_activities_for_period(12, athlete_id, sport_type='Run')
#             all_activities_3_mnths_combined =  list(itertools.chain(*all_activities_3_mnths))

#             top_3_long_runs = strava.get_top_three_longest_runs(all_activities_3_mnths_combined)
#             races=strava.get_race_details(all_activities_3_mnths_combined)
            
#             past_month_activity_dtls, athlete_baseline_stats = workout_classifier_testing.get_run_type(all_activities_3_mnths[0], all_activities_3_mnths[0][0],headers)
            
#             m2_m3_dtls, _ = workout_classifier_testing.get_run_type(all_activities_3_mnths[1]+all_activities_3_mnths[1], all_activities_3_mnths[0][0], headers)
            
#             activities_3_mnths_dtls = past_month_activity_dtls+m2_m3_dtls
#             past_3m_runs_details = "\n".join([f"{i+1}. {run_type}" for i, run_type in enumerate(activities_3_mnths_dtls)])
#             past_month_runs_details = "\n".join([f"{i+1}. {run_type}" for i, run_type in enumerate(past_month_activity_dtls)])
            
#             past_3m_summarised = ai.analyse_past_3m_runs(past_3m_runs_details, athlete_baseline_stats)
            
#             athlete_goals = generate_goal_prompt(form_data, top_3_long_runs, races)
#             goal_summary_prompt = get_goal_summary_prompt(athlete_goals)
#             goal_summary = ai.get_response_from_groq(goal_summary_prompt)
            
#             # # athlete_goals = test_plan_data.athlete_goals
#             # # athlete_baseline_stats= test_plan_data.athlete_baseline_stats
#             # # past_3m_summarised = test_plan_data.past_3m_summarised
#             # # past_month_runs_details = test_plan_data.past_month_run_details
#             # goal_summary = test_plan_data.goal_summary
            
#             prompt_for_plan = strava_v2_testing.format_prompt_for_llm(athlete_goals,athlete_baseline_stats,  past_3m_summarised, past_month_runs_details)
            
#             # next_week_workout_plan, reason= ai.get_response_from_deepseek(prompt_for_plan)
#             next_week_plan_ = ai.get_response_from_groq(prompt_for_plan)
#             # next_week_plan_ = test_plan_data.new_plan_3
#             workout_json, dates, notes = parse_workout_plan(next_week_plan_)

#             next_week_plan =  markdown2.markdown(next_week_plan_)
#             next_week_plan =next_week_plan.replace('\n','')
            
#             # Store the generated plan and details in the session
#             session['next_week_workout_plan'] = next_week_plan
#             session['goal_summary'] = goal_summary
#             session['athlete_id'] = athlete_id
#             session['athlete_name'] =  athlete_name
#             session['dates'] = dates
#             session.modified = True  # Ensure session is saved
#             database.save_workout_plan(athlete_id, workout_json, dates, goal_summary)
#             return jsonify({
#                 "success": True,
#                 "redirect_url": url_for('training_dashboard', athlete_id=athlete_id)  # Redirect to the training dashboard 
#             }), 200
#         else:
#             dates,last_week_plan, notes,goal_summary = database.get_athelte_training_details(athlete_id)
#             past_week_activity_dtls_ = strava.get_activities_for_period(1, athlete_id, sport_type='Run')
#             past_week_activity_dtls= "\n".join([f"{i+1}. {run_type}" for i, run_type in enumerate(past_week_activity_dtls_)])
            
#             next_week_avail, next_week_plan= generate_next_week_plan(dates,goal_summary,last_week_plan,past_week_activity_dtls, athlete_id)
            
#             session['next_week_workout_plan'] = next_week_plan
#             session['goal_summary'] = goal_summary
#             session['athlete_id'] = athlete_id
#             session['athlete_name'] =  athlete_name
#             session['dates'] = dates
#             session.modified = True  # Ensure session is saved
            
#             if next_week_avail:
#                 database.save_workout_plan(athlete_id, workout_json, dates, notes)
#             return jsonify({
#                 "success": True,
#                 "redirect_url": url_for('training_dashboard', athlete_id=athlete_id)  # Redirect to the training dashboard 
#             }), 200
#     except Exception as ex:
#         logger.error("Eror while generating plan", exc_info=True)
#         raise


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
    today = datetime.today()
    date_str = today.strftime("%Y-%m-%d")  # Format: YYYY-MM-DD
    day_str = today.strftime("%A")  # Full day name
    
    goal_prompt = f"""
    Summarise this athlete goals shortly.
    Athlete goal is to train for {goal} by {target_date}, today is {date_str}, {day_str}.
    The Athlete is currently at a fitness level of {fitness_level} and  can commit {time_commitment} per day for training on weekdays.
    In past 3 months, longest 3 runs of the Athlete are {top_3_long_runs}.
    Athlete has recently performed {recent_performance}, and race performances from strava are {races}. 
    He/she can train for {training_days} days in a week and can do {strength_sessions} strength sessions per week.
    The Athlete has {injuries} and {special_conditions} that you need to consider while creating the plan.
    The Athlete prefers {preferences} and has {other_info} that you need to consider while creating the plan.
    """
    
    return goal_prompt
    
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

def generate_next_week_plan(dates, last_week_plan, goal_summary, past_week_activity_dtls, athlete_id):
    today = datetime.today()
    prev_start_date = datetime.strptime(dates[0].strip(), '%d/%m/%Y')
    prev_end_date = datetime.strptime(dates[1].strip(), '%d/%m/%Y')
    next_week_avail = False
    next_week_plan = last_week_plan
    if prev_start_date< today and today >= prev_end_date:
        next_week_avail = True
        last_week_acitivity = strava.get_activities_for_period(1, athlete_id, sport_type='Run')
        last_week_acitivity =list(itertools.chain(*last_week_acitivity))
        access_token = strava.get_access_token(athlete_id)
        headers = {'Authorization': f'Bearer {access_token}'} 

        past_week_activity_dtls, athlete_baseline_stats_last_week = workout_classifier_testing.get_run_type(last_week_acitivity, last_week_acitivity[0],headers)   
        past_week_activity_dtls = "\n".join([f"{i+1}. {run_type}" for i, run_type in enumerate(past_week_activity_dtls)])

        # past_week_activity_dtls = test_plan_data.past_week_activity_dtls
        
        prompt_for_next_week = format_next_week_prompt_for_llm(last_week_plan, goal_summary, past_week_activity_dtls)
        
        next_week_plan_ = ai.get_response_from_groq(prompt_for_next_week)
        
        # next_week_plan = ai.get_response_from_deepseek(prompt_for_next_week)
        workout_json, dates, notes = parse_workout_plan(next_week_plan_)
        
        
        next_week_plan =  markdown2.markdown(next_week_plan_)
        next_week_plan =next_week_plan.replace('\n','')
        goal_summary =  markdown2.markdown(goal_summary)
       
        database.save_workout_plan(athlete_id, workout_json, dates, notes)
        
        return next_week_avail, next_week_plan
    else:
        return next_week_avail, last_week_plan
        
@app.route('/getNextWeekPlan', methods=['POST'])
def get_next_week_plan():
    athlete_id = request.json.get('athlete_id')
    last_week_plan =request.json.get('last_week_plan')
    goal_summary = request.json.get('goal_summary') or ''
    last_dates = request.json.get('dates')
    dates = last_dates.split("-")
    next_week_avail = False
    
    past_week_activity_dtls_ = strava.get_activities_for_period(1, athlete_id, sport_type='Run')
    past_week_activity_dtls= "\n".join([f"{i+1}. {run_type}" for i, run_type in enumerate(past_week_activity_dtls_)])
    
    next_week_avail, next_week_plan = generate_next_week_plan(dates, last_week_plan, goal_summary, past_week_activity_dtls, athlete_id)

    if next_week_avail:
        return  jsonify({
            "next_week_avail": next_week_avail,
            "next_week_plan":next_week_plan,
            "dates":dates
        })

    else:
        return  jsonify({
            "next_week_avail": next_week_avail,
            "next_week_plan":"Plan will be available next week"
        })

def format_next_week_prompt_for_llm(last_week_plan, goal_summary, past_week_activity_dtls):
    prompt= f"""
    You are a professional running coach. You are a helpful, friendly but strict coach.
    As a strict coach keep your athletes on their toes and make them accountable for their missed run activities or workouts. However, you also help them to plan for their running goals in a friendly manner.
    Today is {datetime.now().strftime("%B %d, %Y")} and the day is {datetime.today().strftime('%A')}. The athlete's goal is - {goal_summary}.
    For the past week the workout plan was - {last_week_plan}.
    And the athletes past_week_run_details were - {past_week_activity_dtls}.
    
    First applaud the athlete for the workouts he has followed in last week if he has done any. However, be strict and keep the athlete accountable for any missed workouts from the provided plan.
    Next generate the next weeks complete workout plan. Include the type of runs, distance, pace, and any other relevant details. provide a detailed workout plan.
    Keep a holistic nature while developing the plan considering strenghts, weaknesses and specific requirements of the athlete. 
    It is essential to keep him injury free while simultaneously increasing the fitness level of athlete.
    Add strength, mobility workouts whenever necessary and as per requirement of athlete. Mention type of workouts to be done in strength training and mobility workouts. Include rest days for proper recovery.
    Consider any inputs from the athlete and adjust the plan accordingly.
    Give plan only till Sunday.
    When generating workout plans, Generate the workout plan in an markdown format:
    Dates: DD/MM/YYYY(start dt) - DD/MM/YYYY(End dt) (first line)
    Overview of the previous workouts: Overview
    Workout Plan:
    [Day] - workouts
    
    Notes:
Ensure -
- Provide markdown formatting for components, items and subitems
- Keep dates in first line
- Days always start with capitalized names
- Put all notes after workout plan section
- Nested items use proper bullet hierarchy in markdown
- Verify date format is DD/MM/YYYY - DD/MM/YYYY

Take a moment and review all the instructions.

Next week plan is-
  
    """
    
    return prompt
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
