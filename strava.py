import database
import requests
import time, datetime
import logging
import utils
import data_processing
import json
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)s %(levelname)s %(message)s')
# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Adjust logging level as needed

# Replace these with your Strava API credentials
CLIENT_ID = '114698'
CLIENT_SECRET = '858dd455b9a1d41095727a9285943ec4210810b2'
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
import logging
import time
import requests
from utils import make_url_request, update_activity, update_description
from data_processing import give_run_summary, give_yoga_summary, give_swim_summary  # import other summary functions as needed

def get_latest_activities(inputs):
    """Main function to retrieve and process latest activities."""
    logging.info('Inside get_latest_activities')
    athlete_id = inputs.get('athlete_id')
    
    # Step 1: Retrieve Access Token
    access_token = get_access_token(athlete_id)
    logging.info('Access token retrieved')
    
    # Step 2: Fetch activities within date range
    activities = fetch_activities(access_token)
    if not activities:
        logging.error("No activities found in the date range")
        return
    
    logging.info(f"Total activities fetched: {len(activities)}")
    
    # Step 3: Process the latest activity
    latest_activity = activities[0]
    process_latest_activity(access_token, latest_activity, activities)

def get_access_token(athlete_id):
    """Retrieve the access token for the athlete."""
    # Replace this with actual token retrieval logic
    return "your_access_token"

def fetch_activities(access_token):
    """Fetches activities within the last 4 weeks for the athlete."""
    activities_url = "https://www.strava.com/api/v3/athlete/activities"
    headers = {'Authorization': f'Bearer {access_token}'}
    before = int(time.time())
    after = before - (28 * 24 * 60 * 60)
    
    all_activities = []
    page = 1
    
    while True:
        params = {'before': before, 'after': after, 'page': page, 'per_page': 200}
        response = requests.get(activities_url, headers=headers, params=params)
        
        if response.status_code == 200:
            page_activities = response.json()
            if not page_activities:
                break
            all_activities.extend(page_activities)
            page += 1
            logging.info(f"Fetched page {page-1} with {len(page_activities)} activities")
        else:
            logging.error(f"Error fetching activities: {response.status_code}")
            break
    
    return all_activities

def process_latest_activity(access_token, latest_activity, all_activities):
    """Processes the latest activity, updating type and description if necessary."""
    activity_url = f"https://www.strava.com/api/v3/activities/{latest_activity['id']}"
    headers = {'Authorization': f'Bearer {access_token}'}
    
    # Step 4: Update Activity Type if 'Workout'
    latest_activity_data = fetch_activity_data(activity_url, headers)
    if latest_activity_data and latest_activity_data['type'] == 'Workout':
        update_activity_type_to_yoga(activity_url, latest_activity_data, headers)
    
    # Step 5: Update Activity Description Based on Type
    if latest_activity_data:
        update_activity_description(activity_url, latest_activity_data, all_activities, headers)

def fetch_activity_data(activity_url, headers):
    """Fetches activity data for a given activity URL."""
    response = make_url_request(activity_url=activity_url, headers=headers)
    if response:
        return response.json()
    logging.error(f"Error fetching activity data: {response.status_code}")
    return None

def update_activity_type_to_yoga(activity_url, activity_data, headers):
    """Updates the activity type to 'Yoga' if the current type is 'Workout'."""
    updated_name = activity_data['name'].rsplit(' ', 1)[0] + " Yoga"
    update_json = {'type': 'Yoga', 'sport_type': 'Yoga', 'name': updated_name}
    
    update_message = update_activity(activity_url=activity_url, update_json=update_json, headers=headers)
    print(update_message)

def update_activity_description(activity_url, latest_activity_data, all_activities, headers):
    """Updates the activity description with a summary if not already present."""
    url = 'https://strava-summariser.vercel.app'
    summary_header = "Four-Week Rolling"
    
    # Check if description already contains summary
    if (latest_activity_data['description'] is None or 
        (summary_header not in latest_activity_data['description'] and url not in latest_activity_data['description'])):
        
        activities_of_type = [activity for activity in all_activities if activity['type'] == latest_activity_data['type']]
        result_table = getattr(data_processing, f"give_{latest_activity_data['type'].lower()}_summary")(activities_of_type)
        
        update_json = update_description(activity_data=latest_activity_data, summary=result_table)
        update_message = update_activity(activity_url=activity_url, update_json=update_json, headers=headers)
        print(update_message)
    else:
        logging.info("Summary already exists in description, skipping update")