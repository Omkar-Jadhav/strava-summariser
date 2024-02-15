import requests
import time, datetime
from tabulate import tabulate
import logging
import utils
import data_processing
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)s %(levelname)s %(message)s')

# Replace these with your Strava API credentials
CLIENT_ID = '114698'
CLIENT_SECRET = '858dd455b9a1d41095727a9285943ec4210810b2'
REFRESH_TOKEN = '239efcb1a295abda6e7d930587d120817cb5997d'

# Step 1: Get Access Token (you may do this once to obtain the token)
def get_access_token():
    auth_url = 'https://www.strava.com/oauth/token'
    payload = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'refresh_token',
        'refresh_token': REFRESH_TOKEN
    }
    response = requests.post(auth_url, data=payload)
    return response.json()['access_token']

# Step 2: Get Latest Activities
def get_latest_activities():
    logging.info('Inside get_latest_activities')
    access_token = get_access_token()
    logging.info('after access token')
    

    # API endpoint for athlete activities
    activities_url = 'https://www.strava.com/api/v3/athlete/activities'

    headers = {'Authorization': f'Bearer {access_token}'}
    BEFORE =int(time.time()) - (7*24*60*60*30)
    AFTER = int(time.time())
    PAGE =1
    PER_PAGE = 10000
    
    parameters = {
        'page' :PAGE,
        'per_page' : PER_PAGE
    }

    # Make GET request to retrieve activities
    response = requests.get(activities_url, headers=headers)
    if response.status_code == 200:
        activities = response.json()
        result_table= []
        #Getting latest activity data this can be added in a util file
        latest_activity_id = activities[0]['id']
        latest_activity_url = f"https://www.strava.com/api/v3/activities/{latest_activity_id}"
        latest_activity_response = utils.make_url_request(activity_url=latest_activity_url, headers=headers)
        
        if latest_activity_response:
            latest_activity_data=latest_activity_response.response_json()
        
            if(latest_activity_data['type']=='Workout'):
                updated_name = latest_activity_response['name'].rsplit(' ', 1)[0] + " Yoga"
                updated_activity_json = {'type':'Yoga', 'sport_type':'Yoga', 'name':updated_name}
                
                update_message = utils.update_activity(activity_url=latest_activity_url, update_json=updated_activity_json, headers=headers)
                print(update_message)
                
        else:
            print(f"Error while getting latest activity. Please check the logs for details.")
        
            
        latest_activity_url = f"https://www.strava.com/api/v3/activities/{latest_activity_id}"
        latest_activity_response = requests.get(latest_activity_url, headers=headers)
        latest_activity_data = latest_activity_response.json()
        update_message= ""
        if(latest_activity_response.status_code == 200):    
            if(latest_activity_data['type']=='Run'):
                run_activities = [activity for activity in activities if activity['type']=='Run']
                result_table = data_processing.give_run_summary(run_activities) 
                
                update_json = utils.update_description(activity_data=latest_activity_data, summary=result_table)
                update_message = utils.update_activity(activity_url=latest_activity_url, update_json=update_json, headers=headers)
            
                
            elif(latest_activity_data['type']=='Yoga'):
                yoga_activities = [activity for activity in activities if activity['type']=='Yoga']
                result_table = data_processing.give_yoga_summary(yoga_activities)    
                
                update_json = utils.update_description(activity_data=latest_activity_data, summary=result_table)
                update_message = utils.update_activity(activity_url=latest_activity_url, update_json=update_json, headers=headers)
        
            print(update_message)
            
    else:   
        print(f"Error: {response.status_code}, {response.text}")
