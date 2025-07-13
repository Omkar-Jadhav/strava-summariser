import os

from flask import jsonify, request
import ai
import database
import requests
import time, datetime
import logging
import utils
import data_processing
import json
import workout_classifier
from ai import get_insights_by_llm
from workout_classifier import get_run_type 
import strava
import calendar

STRAVA_CLIENT_ID = os.environ.get('CLIENT_ID')
STRAVA_CLIENT_SECRET = os.environ.get('CLIENT_SECRET')
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)s %(levelname)s %(message)s')
# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Adjust logging level as needed

# Replace these with your Strava API credentials
CLIENT_ID = os.environ.get('CLIENT_ID')
CLIENT_SECRET =  os.environ.get('CLIENT_SECRET')
VERIFY_TOKEN = "STRAVA"

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

def get_top_three_longest_runs(activities):
    runs = []
    for activity in activities:
        if activity['type'] == 'Run':
            distance_km = activity['distance'] / 1000  # Convert meters to kilometers
            moving_time = activity['moving_time']
            avg_pace_min_per_km = utils.calculate_pace_minKm(moving_time, distance_km * 1000)
            elevation_gain = activity.get('total_elevation_gain', 0)  # Elevation in meters
            
            runs.append({
                "distance": round(distance_km, 2),
                "avg_pace_min_per_km": avg_pace_min_per_km,
                "elevation_gain": elevation_gain,
                "moving_time": utils.convert_seconds_in_hhmmss(moving_time)
            })
    
    # Sort runs by distance in descending order and get the top three
    top_three_runs = sorted(runs, key=lambda x: x['distance'], reverse=True)[:3]
    
    # Format the output as a string with numbered runs and details
    output = ""
    for i, run in enumerate(top_three_runs, 1):
        output += f"{i}. Distance: {run['distance']} km, Pace: {run['avg_pace_min_per_km']} min/km, Elevation Gain: {run['elevation_gain']} m with moving time:{run['moving_time']}\n"
    
    return output

def get_race_details(activities):
    races = []
    for activity in activities:
        if activity.get('workout_type') == 1:  # Strava identifies races with workout_type = 1
            distance_km = activity['distance'] / 1000  # Convert meters to kilometers
            moving_time = activity['moving_time']
            avg_pace_min_per_km = utils.calculate_pace_minKm(moving_time, distance_km * 1000)
            elevation_gain = activity.get('total_elevation_gain', 0)  # Elevation in meters
            races.append({
                "name": activity.get('name', 'Unnamed Race'),
                "distance": round(distance_km, 2),
                "moving_time": utils.convert_seconds_in_hhmmss(moving_time),
                "avg_pace_min_per_km": avg_pace_min_per_km,
                "elevation_gain": elevation_gain
            })
    
    # Format the output as a string with numbered races and details
    output = ""
    for i, race in enumerate(races, 1):
        output += f"{i}. Name: {race['name']}, Distance: {race['distance']} km, Moving Time: {race['moving_time']}, Pace: {race['avg_pace_min_per_km']} min/km, Elevation Gain: {race['elevation_gain']} m\n"
    
    return output

def get_activities_for_period(weeks, athlete_id, sport_type=None, access_token = ''):
    """Get activities for a specific time period and sport type."""
    # Step 1: Retrieve Access Token
    if access_token=='':
        access_token = get_access_token(athlete_id)
        logger.info('Access token retrieved')
    
    # Step 2: Define API Endpoint and Parameters
    today = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    now = int(time.time()) 
    start_day = today - datetime.timedelta(weeks=weeks)
    
    BEFORE = now  # Midnight of today
    AFTER = calendar.timegm(start_day.timetuple())  # Midnight N weeks ago

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
            logger.info(f"Fetched page {page-1} with {len(page_activities)} activities")
        else:
            logger.error(f"Error fetching activities: {response.status_code}")
            break
    
    logger.info(f"Total activities fetched: {len(all_activities)}")
    
    month_wise_activities = get_month_wise_activities(all_activities, weeks, sport_type)
    
    return month_wise_activities

def get_month_wise_activities(all_activities, weeks, sport_type):
    current_time = int(time.time())
    week_seconds = 7 * 24 * 60 * 60
    
    segmented_activities = []
    for i in range(weeks // 4 + 1):  # Creates enough groups for 4+4+1 pattern
        segmented_activities.append([])

    for activity in all_activities:
        activity_time = activity['start_date']
        activity_timestamp = int(datetime.datetime.strptime(activity_time, '%Y-%m-%dT%H:%M:%SZ').timestamp())
        
        week_index = (current_time - activity_timestamp) // week_seconds
        
        if week_index < weeks:
            segment_index = week_index // 4  # Determines which group it belongs to
            segmented_activities[segment_index].append(activity)

    # Filter by sport type if provided
    if sport_type:
        segmented_activities = [
            [activity for activity in segment if activity['type'] == sport_type] 
            for segment in segmented_activities
        ]
    
    # Remove empty segments
    segmented_activities = [segment for segment in segmented_activities if segment]

    # Logging segment counts
    for i, segment in enumerate(segmented_activities):
        logger.info(f"Segment {i+1} activities: {len(segment)}")

    return segmented_activities


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
                    
                    all_activities[0]["type"]="Yoga"
                    all_activities[0]["sport_type"]="Yoga"
                    
                    update_message = utils.update_activity(activity_url=latest_activity_url, update_json=updated_activity_json, headers=headers)
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
                if summary_header not in latest_activity_data['description'] and url not in latest_activity_data['description']:
                # if True:
                    activities_of_type = [activity for activity in all_activities if activity['type'] == latest_activity_data['type']]
                    result_table = getattr(data_processing, f"give_{latest_activity_data['type'].lower()}_summary")(activities_of_type)
                    logger.info(f"description:{latest_activity_data['description']} \n  url: {url}" )
                    out_message+=result_table
                    if latest_activity_data['type'] == 'Run':
                        run_types = workout_classifier.get_run_type(activities_of_type, headers)
                        past_runs_details = "\n".join([f"{i+1}. {run_type}" for i, run_type in enumerate(run_types)])
                        insights = ai.get_insights_by_llm(result_table, past_runs_details)
                        out_message += "\nLast 4 weeks by strava-summariser :\n"+insights+'\n'
                   
                    footer = "\nSubscribe on strava-summariser.vercel.app/ \nStats generated using StravaAPI by Omkar Jadhav"
                    
                    out_message += footer

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