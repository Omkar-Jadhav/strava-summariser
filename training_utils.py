from datetime import datetime
import itertools
import ai
import database
import strava
import utils
import workout_classifier_testing
import markdown2

def generate_next_week_plan(dates, last_week_plan, goal_summary, athlete_id):
    last_week_acitivity = strava.get_activities_for_period(1, athlete_id, sport_type='Run')
    last_week_acitivity =list(itertools.chain(*last_week_acitivity))[::-1]
    access_token = strava.get_access_token(athlete_id)
    headers = {'Authorization': f'Bearer {access_token}'} 

    past_week_activity_dtls, athlete_baseline_stats_last_week = workout_classifier_testing.get_run_type(last_week_acitivity, last_week_acitivity[0],headers)   
    past_week_activity_dtls = "\n".join([f"{i+1}. {run_type}" for i, run_type in enumerate(past_week_activity_dtls)])

    # past_week_activity_dtls = test_plan_data.past_week_activity_dtls
    
    prompt_for_next_week = utils.format_next_week_prompt_for_llm(last_week_plan, goal_summary, past_week_activity_dtls)
    
    next_week_plan_ = ai.get_json_response_from_groq(prompt_for_next_week)
    
    # next_week_plan = ai.get_response_from_deepseek(prompt_for_next_week)
    dates, workout_json, notes, overview = utils.parse_json_workout_plan(next_week_plan_)
    next_week_plan = workout_json
    
    next_week_plan_markdown = workout_days_plan_to_markdown(workout_json, dates, notes, overview)
    database.save_workout_plan(athlete_id, workout_json, dates, notes)
    
    return next_week_plan_markdown


def check_next_week_avail(dates):
    today = datetime.today()
    prev_start_date = datetime.strptime(dates[0].strip(), '%d/%m/%Y')
    prev_end_date = datetime.strptime(dates[1].strip(), '%d/%m/%Y')
    next_week_avail = False
    if prev_start_date< today and today >= prev_end_date:
        next_week_avail = True
    return next_week_avail

def workout_days_plan_to_markdown(workout_json, dates, notes, overview):
    markdown_output = []
    
    # Add Date Range
    markdown_output.append(f"##  Dates-  ({dates})\n")

    if overview!="":
        markdown_output.append(f"##  Overview\n")
        markdown_output.append(f"{overview}\n")
    
    
    # Add Workout Plan
    markdown_output.append("## Workout Plan\n")
    
    for day_plan in workout_json:
        markdown_output.append(f"### {day_plan['day']}\n")
        for workout in day_plan["workouts"]:
            markdown_output.append(f"  - **{workout['type']}**: {workout['details']}")

    # Add Notes
    if notes:
        markdown_output.append("\n## Notes\n")
        for note in notes:
            markdown_output.append(f"- {note}")

    return "\n".join(markdown_output)

    
def workout_plan_to_markdown(workout_json):
    markdown_output = []

    # Add Date Range
    markdown_output.append(f"## Workout Plan ({workout_json['date_range']})\n")

    # Add Overview
    if "overview" in workout_json and workout_json["overview"]:
        markdown_output.append(f"### Overview\n{workout_json['overview']}\n")

    # Add Workout Plan
    markdown_output.append("### Workout Plan")
    
    for day_plan in workout_json["workout_plan"]:
        markdown_output.append(f"#### {day_plan['day']}")
        for workout in day_plan["workouts"]:
            markdown_output.append(f"- **{workout['type']}**: {workout['details']}")

    # Add Notes
    if "notes" in workout_json and workout_json["notes"]:
        markdown_output.append("\n### Notes")
        for note in workout_json["notes"]:
            markdown_output.append(f"- {note}")

    return "\n".join(markdown_output)

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
    
    goal_prompt_template = utils.load_prompt("generate_goal_prompt") 
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

def work_on_user_query(user_input, current_plan, goal_summary):
    prompt_template  = utils.load_prompt("user_query_prompt")
    prompt = prompt_template.substitute(
                    current_date=datetime.now().strftime("%B %d, %Y"),
                    current_day=datetime.today().strftime('%A'),
                    current_plan=current_plan,
                    goal_summary=goal_summary,
                    user_input=user_input
                )

    gpt_response = ai.get_json_response_from_groq(prompt)
    response = gpt_response['response']
    is_plan_updated = gpt_response['is_plan_updated']
    # response, is_plan_updated = extract_response_and_plan_status(gpt_response)
    
    return response, is_plan_updated

def format_prompt_for_llm(athlete_goal, athlete_baseline, past_3m_summarised, past_month_runs_details):
    for section in ['road_baseline_stats', 'trail_baseline_stats']:
        athlete_baseline[section]['speed_mean'] = utils.convert_speed_to_pace(athlete_baseline[section]['speed_mean'])
        athlete_baseline[section]['speed_std'] = utils.convert_speed_to_pace(athlete_baseline[section]['speed_std'])

    baseline_stats = ', '.join(f'{key}={value}' for key, value in athlete_baseline['road_baseline_stats'].items()if key != "speed_std")
    current_day = datetime.today().strftime('%A')
    current_date = datetime.now().strftime("%B %d, %Y")
    prompt_template = utils.load_prompt('generate_plan_new_user')
    
    prompt =prompt_template.substitute(current_date=current_date,current_day=current_day, baseline_stats=baseline_stats, athlete_goal=athlete_goal, past_3m_summarised=past_3m_summarised,past_month_runs_details=past_month_runs_details)
    
    return prompt