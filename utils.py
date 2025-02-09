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



