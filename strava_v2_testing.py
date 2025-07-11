import ai
import database
import requests
import time, datetime
import logging
import training_utils
import utils
import data_processing
import json
import workout_classifier
import workout_classifier_testing
from ai import get_insights_by_llm
# from datetime import datetime
from workout_classifier import get_run_type 
import os
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)s %(levelname)s %(message)s')
# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Adjust logging level as needed

# Replace these with your Strava API credentials
CLIENT_ID = os.environ.get('CLIENT_ID')
CLIENT_SECRET =  os.environ.get('CLIENT_SECRET')
# REFRESH_TOKEN = '239efcb1a295abda6e7d930587d120817cb5997d'

# Step 1: Get Access Token (you may do this once to obtain the token)
def get_access_token(athlete_id):
    client = database.initiate_mango_connection()
    refresh_token = database.check_athlete_in_data(client,athlete_id)
    database.close_client(client)
    logger.info(f'Refresh token{refresh_token} for athlete ID {athlete_id}')
    # Check if the athlete_id exists in the refresh_tokens
    if refresh_token is not None:
        # Retrieve the refresh_token for the athlete_id
        logger.info('inside if refresh-token condition')
        REFRESH_TOKEN = refresh_token
        
        auth_url = 'https://www.strava.com/oauth/token'
        payload = {
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'grant_type': 'refresh_token',
            'refresh_token': REFRESH_TOKEN
        }
        response = requests.post(auth_url, data=payload)
        logger.info(f"Access token is {response.json()['access_token']}")
        logger.info(f"response is {response.json()}")
        return response.json()['access_token']
    else:
        # Handle the case where athlete_id is not found in the refresh_tokens
        print("Athlete ID not found in data")
        return "Athlete ID not found in data"

def get_latest_activities(inputs):
    logging.info('Inside get_latest_activities')
    latest_activity_id = inputs.get('activity_id')
    athlete_id = inputs.get('athlete_id')
    # Step 1: Retrieve Access Token
    access_token = get_access_token(athlete_id)
    logging.info('Access token retrieved')
    
    # Step 2: Define API Endpoint and Parameters
    now = int(time.time())
    today = datetime.datetime.now()

    # Get midnight of today
    midnight_today = datetime.datetime.combine(today.date(), datetime.time.min)

    # Get midnight of 28 days ago
    midnight_28_days_ago = midnight_today - datetime.timedelta(days=27)

    # Convert to UNIX timestamps
    BEFORE = now
    AFTER = int(midnight_28_days_ago.timestamp())

    activities_url = "https://www.strava.com/api/v3/athlete/activities"
    headers = {'Authorization': f'Bearer {access_token}'}   
    
    all_activities = []
    page = 1
    while True:
        params = {
            'before': BEFORE,
            'after': AFTER,
            'page': page,
            'per_page': 200  # Strava's maximum allowed
        }
        
        response = requests.get(activities_url, headers=headers, params=params)
        if response.status_code == 200:
            page_activities = response.json()
            if not page_activities:  # No more activities to fetch
                break
                
            all_activities.extend(page_activities)
            page += 1
            logging.info(f"Fetched page {page-1} with {len(page_activities)} activities")
        else:
            logging.error(f"Error fetching activities: {response.status_code}")
            break
    
    logging.info(f"Total activities fetched: {len(all_activities)}")
    out_message=""
    if all_activities:
        result_table = []
        
        # Step 4: Process Latest Activity
        latest_activity_id = all_activities[0]['id']
        latest_activity_url = f"https://www.strava.com/api/v3/activities/{latest_activity_id}"
        latest_activity_response = utils.make_url_request(activity_url=latest_activity_url, headers=headers)
        
        if latest_activity_response:
            latest_activity_data = latest_activity_response.json()
            if athlete_id==64768690:
                if latest_activity_data['type'] == 'Workout':
                    # updated_name = latest_activity_data['name'].rsplit(' ', 1)[0] + " Yoga"
                    updated_name = "Daily Sadhna"
                    updated_activity_json = {'type': 'Yoga', 'sport_type': 'Yoga', 'name': updated_name}
                    update_message = utils.update_activity(activity_url=latest_activity_url, update_json=updated_activity_json, headers=headers)
                    
                    all_activities[0]["type"]="Yoga"
                    all_activities[0]["sport_type"]="Yoga"
                    print(update_message)
                    
                else:
                    print(f"Latest activity is not of type Workout.")
        else:
            print(f"Error while getting latest activity. Please check the logs for details.")
        
        # Step 5: Update Activity Description Based on Type
        latest_activity_url = f"https://www.strava.com/api/v3/activities/{latest_activity_id}"
        latest_activity_response = requests.get(latest_activity_url, headers=headers)
        latest_activity_data = latest_activity_response.json()
        update_message = ""
        url = "https://strava-summariser.vercel.app"
        summary_header = "Four-Week Rolling"  # This is the common header text used in summaries
        
        if latest_activity_response.status_code == 200:
            # Step 5: Update Activity Description Based on Type
            if latest_activity_data['type'] in ['Run', 'Yoga', 'Swim','Ride', 'Walk', 'WeightTraining']:
                # Initialize description if None
                if latest_activity_data['description'] is None:
                    latest_activity_data['description'] = ""
                
                # Check if summary already exists
                # if summary_header not in latest_activity_data['description'] and url not in latest_activity_data['description']:
                if True:
                    activities_of_type = [activity for activity in all_activities if activity['type'] == latest_activity_data['type']]
                    result_table = getattr(data_processing, f"give_{latest_activity_data['type'].lower()}_summary")(activities_of_type)
                    logger.info(f"description:{latest_activity_data['description']} \n  url: {url}" )
                    
                    today = datetime.now().strftime("%B %d, %Y")
                    
                    # athlete_goal = f"Run a marathon under 3 hours 10 minutes on March 16th, 2025 today is {today}"
                    athlete_goal = f"Run a 100km trail ultra marathon with 3380m elevation gain on March 16th, 2025 today is {today}"
                    
                    if latest_activity_data['type'] == 'Run':
                        run_types, athlete_baseline_stats = workout_classifier_testing.get_run_type(activities_of_type, latest_activity_data, headers)
                        past_runs_details = "\n".join([f"{i+1}. {run_type}" for i, run_type in enumerate(run_types)])
                        # insights = ai.get_insights_by_llm(result_table, past_runs_details)
                        # out_message = "\nLast 4 weeks by strava-summariser :\n"+insights+'\n'
                        inp_message = training_utils.format_prompt_for_llm(result_table, past_runs_details, athlete_baseline_stats, athlete_goal)
                        workout_plan, reasoning = ai.get_response_from_deepseek(inp_message)
                    out_message+=result_table
                    
                    update_json = utils.update_description(activity_data=latest_activity_data, summary=out_message)
                    update_message = utils.update_activity(activity_url=latest_activity_url, update_json=update_json, headers=headers)  
                    print(update_message)
                else:
                    logger.info("Summary already exists in description, skipping update")
            
        else:
            print(f"Error: {latest_activity_response.status_code}, {latest_activity_response.text}")
    else:
        print(f"Error: No activities found in the date range")
    

        
def fetch_complete_activity_detail(activty_id, headers):
    """Fetch complete activity details."""
    activity_url = f"https://www.strava.com/api/v3/activities/{activty_id}"
    response = requests.get(activity_url, headers)
    if response.status_code == 200:
        return response.json()
    return None
