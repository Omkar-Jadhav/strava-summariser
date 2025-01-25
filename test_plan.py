import requests
import json
# Define the URL for the local Flask app
url = "https://localhost/generatePlan"

form_data = {'goalType': 'specific', 'goal': '100Km ultra trail with 5000m elevation', 'targetDate': '2025-03-09', 'trainingDays': '5', 'fitnessLevel': 'intermediate', 'recentPerformance': '100Km ultra trail 3380D+ in 19:30, marathon in 3:45', 'strengthSessions': '4', 'timeCommitment': '1.5hr', 'injuries': '', 'preferences': 'Long runs and long trails on weekends only', 'specialConditions': '', 'otherInfo': '', 'athlete_id': '64768690'}

form_data = json.dumps(form_data)
response = requests.post(url, json=form_data)

# Print the response
if response.status_code == 200:
    print("Response from server:")
    print(response.json())
else:
    print(f"Error: {response.status_code}")
    print(response.text)