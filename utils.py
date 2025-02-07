from datetime import datetime
import itertools
import os
import flask
import requests
from string import Template

import ai

def update_activity(activity_url, update_json, headers):
    update_response = requests.put(activity_url, headers=headers, json=update_json)
    if update_response.status_code == 200:
        message ="Activity description updated successfully."
    else:
        message=f"Error updating activity description: {update_response.status_code}, Error description : {update_response.text}"
    return message
            
            
def make_url_request(activity_url, headers):
    activity_response = requests.get(activity_url, headers=headers)
    if(activity_response.status_code == 200):
        return activity_response
    else:
            print(f"Error while getting activity: {activity_response.status_code}, Error description : {activity_response.text}")
            
def update_description(activity_data, summary):
    description = activity_data['description']
    if description == "" or description is None:
        updated_description = f"{summary}"
    else:    
        updated_description = f"{description} {summary}"
    update_json = {"description": updated_description}
    return update_json


def convert_seconds_in_hhmmss(seconds):
    hours = int(seconds//3600)
    minutes = int((seconds%3600)//60)
    seconds = int(seconds % 60)
    return str(hours).zfill(2) +':' + str(minutes).zfill(2) +':'+ str(seconds).zfill(2)

def convert_speed_to_pace(speed_m_per_s):
    if speed_m_per_s <= 0:
        return "Speed must be greater than 0"

    # Convert speed to pace in min/km
    pace_min_per_km = (1000 / speed_m_per_s) / 60
    minutes = int(pace_min_per_km)  # Whole minutes
    seconds = int((pace_min_per_km - minutes) * 60)  # Remaining seconds

    return f"{minutes}:{seconds:02d} min/km"

def pace_to_speed(pace_str):
    """
    Convert a pace string in the format 'mm:ss min/km' to speed in m/s.
    """
    # Split the string into minutes and seconds
    pace_str = pace_str.replace(" min/km", "")
    minutes, seconds = map(int, pace_str.split(":"))
    
    # Convert pace (min/km) to total seconds per kilometer
    total_seconds_per_km = minutes * 60 + seconds
    
    # Convert to speed in m/s (meters per second)
    speed_m_per_s = 1000 / total_seconds_per_km
    return speed_m_per_s

def calculate_speed(moving_time, distance):
    if distance == 0:
        return "00:00 min/Km"
    else:
        mov_speed_min, mov_speed_sec = map(int, divmod(moving_time / distance, 60))
        return f"{mov_speed_min:02d}:{mov_speed_sec:02d} min/Km"
    
def calculate_speed_in_kmph(moving_time, distance):
    if moving_time == 0:
        return "0.00 km/hr"
    else:
        speed_kph = (distance / 1000) / (moving_time / 3600)
        return f"{speed_kph:.2f} km/hr"
    
def calculate_pace_minKm(moving_time, distance):
    if distance == 0:
        return "00:00 min/Km"
    else:
        pace_seconds_per_km = moving_time / (distance / 1000)
        pace_minutes = int(pace_seconds_per_km // 60)
        pace_seconds = int(pace_seconds_per_km % 60)
        return f"{pace_minutes:02d}:{pace_seconds:02d} min/Km"

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



def load_prompt(template_name):
    file_path = os.path.join("prompts", f"{template_name}.txt")
    with open(file_path, "r") as file:
        return Template(file.read())
    
    
def is_user_input_relevant(user_input, next_week_plan, goal_summary, messages):
    
    prompt_template = load_prompt("is_user_input_relevant")
    prompt = prompt_template.substitute(
        messages=messages,
        goal_summary=goal_summary,
        next_week_plan=next_week_plan,
        user_input=user_input
    )
    
    is_relevant = ai.get_response_from_groq(prompt)
    return is_relevant

def format_next_week_prompt_for_llm(last_week_plan, goal_summary, past_week_activity_dtls):
    prompt_template = load_prompt("next_week_prompt")
    prompt = prompt_template(
        current_day = datetime.now().strftime("%B %d, %Y"),
        current_date = datetime.now().strftime("%A"),
        goal_summary = goal_summary,
        last_week_plan = last_week_plan,
        past_week_activity_dtls = past_week_activity_dtls
    )
    
    return prompt


def work_on_user_query(user_input, current_plan, goal_summary):
    prompt_template  = load_prompt("user_query_prompt")
    prompt = prompt_template.substitute(
                    current_date=datetime.now().strftime("%B %d, %Y"),
                    current_day=datetime.today().strftime('%A'),
                    current_plan=current_plan,
                    goal_summary=goal_summary,
                    user_input=user_input
                )

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
    
    goal_prompt_template = load_prompt("generate_goal_prompt") 
    goal_prompt = goal_prompt_template.substitute(
        goal = goal, target_date = target_date,
        day_str = day_str,date_str =date_str,
        fitness_level = fitness_level, time_commitment = time_commitment,
        top_3_long_runs = top_3_long_runs, recent_performance = recent_performance, 
        races = races, training_days = training_days,
        strength_sessions = strength_sessions, injuries= injuries,
        special_conditions = special_conditions, preferences = preferences,
        other_info=other_info
    )
    
    return goal_prompt