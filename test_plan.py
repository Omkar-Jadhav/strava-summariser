import re
import requests
import json
import test_plan_data
# Define the URL for the local Flask app
url = "https://localhost/generatePlan"

# form_data = {'goalType': 'specific', 'goal': '100Km ultra trail with 5000m elevation', 'targetDate': '2025-03-09', 'trainingDays': '5', 'fitnessLevel': 'intermediate', 'recentPerformance': '100Km ultra trail 3380D+ in 19:30, marathon in 3:45', 'strengthSessions': '4', 'timeCommitment': '1.5hr', 'injuries': '', 'preferences': 'Long runs and long trails on weekends only', 'specialConditions': '', 'otherInfo': '', 'athlete_id': '64768690'}

# form_data = json.dumps(form_data)
# response = requests.post(url, json=form_data)

# # Print the response
# if response.status_code == 200:

#     print("Response from server:")
#     print(response.json())
# else:
#     print(f"Error: {response.status_code}")
#     print(response.text)

string1 = test_plan_data.next_week_plan
string4= test_plan_data.new_plan_3
string3 = test_plan_data.new_plan_2
import json
import re
import re

def parse_workout_plan(text):
    # Extracting Dates
    dates = re.search(r"\s*(\d{2}/\d{2}/\d{4})\s*-\s*(\d{2}/\d{2}/\d{4})", text)
    dates = dates.groups() if dates else None

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

    return workouts, "-".join(dates), notes

# Parsing both strings
string = test_plan_data.new_plan
# parsed_plan1 = parse_workout_plan(string1)
parsed_plan4 = parse_workout_plan(string4)
# parsed_plan3 = parse_workout_plan(string3)
# parse_plan = parse_workout_plan(string)

# workouts = extract_daily_workouts(parse_plan[1])

# print(parsed_plan3)
# print(parsed_plan1)
# print(parsed_plan4)