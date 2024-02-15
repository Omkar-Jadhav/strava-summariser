import requests
import time, datetime
from tabulate import tabulate
import logging
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
        latest_activity_response = requests.get(latest_activity_url, headers=headers)
        
        ## this can be added in a separate util file
        if(latest_activity_response.status_code == 200):
            if(latest_activity_response['type']=='Workout'):
                updated_name = latest_activity_response['name'].rsplit()[-1] + " Yoga"
                updated_activity_type = {'type':'Yoga', 'sport_type':'Yoga', 'name':updated_name}
                update_activity_response = requests.put(latest_activity_url, headers=headers, json=updated_activity_type)
                
                if update_activity_response.status_code == 200:
                    print("Activity description updated successfully.")
                else:
                    print(f"Error updating activity description: {update_activity_response.status_code}, Error description : {update_activity_response.text}")
        else:
            print(f"Error while getting latest activity: {latest_activity_response.status_code}, Error description : {latest_activity_response.text}")
        ## --- ##
            
        latest_activity_url = f"https://www.strava.com/api/v3/activities/{latest_activity_id}"
        latest_activity_response = requests.get(latest_activity_url, headers=headers)
        
        if(latest_activity_response.status_code == 200):    
            if(latest_activity_response['type']=='Run'):
                run_activities = [activity for activity in activities if activity['type']=='Run']
                result_table = give_run_summary(run_activities) 
                
            elif(latest_activity_response['type']=='Yoga'):
                yoga_activities = [activity for activity in activities if activity['type']=='Yoga']
                result_table = give_yoga_summary(yoga_activities)    
        
            latest_activity = latest_activity_response.json()
            
            #updating the activity can be added to util file
            #Updating the description
            description = latest_activity['description']
            updated_description = f"{description} \n {result_table}"
            update_description = {"description": updated_description}
            
            update_response = requests.put(latest_activity_url, headers=headers, json=update_description)
            if update_response.status_code == 200:
                print("Activity description updated successfully.")
            else:
                print(f"Error updating activity description: {update_response.status_code}, Error description : {update_response.text}")
      
    else:   
        print(f"Error: {response.status_code}, {response.text}")
        
def convert_seconds_in_hhmmss(seconds):
    hours = int(seconds//3600)
    minutes = int((seconds%3600)//60)
    seconds = int(seconds % 60)
    return str(hours).zfill(2) +':' + str(minutes).zfill(2) +':'+ str(seconds).zfill(2)

def calculate_speed(moving_time, distance):
    mov_speed_min, mov_speed_sec = map(int,divmod(moving_time/distance, 60))
    return str(mov_speed_min) + ':' + str(mov_speed_sec) + ' min/Km'


def give_yoga_summary(yoga_activities):
    total_yoga_time = 0
    total_sessions = 0
    for activity in yoga_activities:
        total_yoga_time += activity["elapsed_time"]
        total_sessions += 1
    
    avg_yoga_session = convert_seconds_in_hhmmss(round(total_yoga_time/total_sessions, 2))
    total_yoga_time = convert_seconds_in_hhmmss(total_yoga_time)
    
    overall_yoga_summary_data =[
        ["Total yoga sessions:", f"{total_sessions}"],
        ["Avg yoga session:", f"{avg_yoga_session}"],
        ["Total yoga time:", f"{total_yoga_time}"],
        
    ]
    overall_yoga_summary_table = tabulate(overall_yoga_summary_data, tablefmt="plain")
    result_table = f"\n------- Four-Week Rolling Overall Yoga Summary -------\n{overall_yoga_summary_table}\n\n ------- Stats created using StravaAPI by Omkar ------"
    
    print(result_table)
    return result_table


def give_run_summary(run_activities):
    tot_distance_ran_year = 0
    tot_distance_ran_month = 0
    avg_distance_per_run = 0
    avg_distance_per_week = 0
    tot_elevation_gain = 0
    avg_elevation_gain = 0
    tot_elevation_gain_trail = 0
    avg_elevation_gain_trail = 0
    tot_trail_distance = 0
    moving_time_trail = 0
    elapsed_time_trail = 0
    total_runs_month = 0
    total_trail_runs_month = 0
    total_road_runs_month =0 
    tot_road_distance = 0
    tot_elevation_gain_road = 0
    moving_time_road = 0
    avg_elapsed_speed_trail = 0
    tot_elapsed_time = 0
    tot_moving_time = 0
    
    for activity in run_activities:
        tot_elapsed_time += activity['elapsed_time']
        tot_moving_time += activity['moving_time']
        
        moving_time_hhmm = convert_seconds_in_hhmmss(tot_moving_time)
        elapsed_time_hhmm = convert_seconds_in_hhmmss(tot_elapsed_time)
        
        # For All runs 
        total_runs_month+=1
        tot_distance_ran_month +=round(activity['distance']/1000,2)
        avg_distance_per_run = round(tot_distance_ran_month/total_runs_month,2)

        tot_elevation_gain += int(activity['total_elevation_gain'])
        avg_elevation_gain = round(tot_elevation_gain/total_runs_month,2)
        
        avg_mov_speed = calculate_speed(tot_moving_time, tot_distance_ran_month)
        avg_elapsed_speed = calculate_speed(tot_elapsed_time, tot_distance_ran_month)
        
        # For Road runs
        if(activity['sport_type']=='Run'):
            total_road_runs_month +=1
            tot_road_distance += round(activity['distance']/1000,2) #In km
            avg_road_distance = round(tot_road_distance/ total_road_runs_month,2)
            tot_elevation_gain_road += int(activity['total_elevation_gain'])
            avg_elevation_gain_road = round(tot_elevation_gain_road/total_road_runs_month,2)
            
            moving_time_road += activity['moving_time']
            avg_mov_speed_road =calculate_speed(moving_time_road, tot_road_distance)
        
        
        # For Trail runs
        if(activity['sport_type']=='TrailRun'):
            total_trail_runs_month +=1
            tot_trail_distance += round(activity['distance']/1000,2) #In km
            avg_trail_distance = round(tot_trail_distance/ total_trail_runs_month,2)
            tot_elevation_gain_trail += int(activity['total_elevation_gain'])
            avg_elevation_gain_trail = round(tot_elevation_gain_trail/total_trail_runs_month,2)
            
            moving_time_trail += activity['moving_time']
            elapsed_time_trail += activity['moving_time']
            avg_mov_speed_trail = calculate_speed(moving_time_trail,tot_trail_distance)
            avg_elapsed_speed_trail = calculate_speed(elapsed_time_trail,tot_trail_distance)
            
        

    overall_summary_data = [
    ["Total runs: ", f"{total_runs_month}"],
    ["Total distance: ", f"{tot_distance_ran_month} Km"],
    ["Average distance:", f"{avg_distance_per_run} Km/run"],
    ["Average pace: ", f"{avg_mov_speed}"],
    ["Total elevation gained: ", f"{tot_elevation_gain} m"],
    ["Avg elevation gain: ", f"{avg_elevation_gain} m/run"],
    ["Total moving time: ", f"{moving_time_hhmm}"],
    ["Total elapsed time: ", f"{elapsed_time_hhmm}"],
    ["Avg pace: ", f"{avg_mov_speed}"]
        ]

    # Data for road runs summary
    road_runs_summary_data = [
        ["Total road runs: ", f"{total_road_runs_month}"],
        ["Total distance on road: ", f"{tot_road_distance} Km"],
        ["Avg distance on road: ", f"{avg_road_distance} km/run"],
        ["Total elevation gain on road: ", f"{tot_elevation_gain_road} m"],
        ["Avg elevation gain on road: ", f"{avg_elevation_gain_road} m/run"],
        ["Avg pace on roads: ", f"{avg_mov_speed_road}"]
    ]

    # Data for trail runs summary
    trail_runs_summary_data = [
        ["Total trail runs: ", f"{total_trail_runs_month}"],
        ["Total distance on trails: ", f"{tot_trail_distance} Km"],
        ["Avg distance on trails: ", f"{avg_trail_distance} km/run"],
        ["Total elevation gain on trails: ", f"{tot_elevation_gain_trail} m"],
        ["Avg elevation gain on trails: ", f"{avg_elevation_gain_trail} m/run"],
        ["Avg moving pace on trails: ", f"{avg_mov_speed_trail}"],
        ["Avg elapsed time pace on trails: ", f"{avg_elapsed_speed_trail}"]
    ]



    # Store tables in variables with headers
    header_table = tabulate([], headers= 'Overall summary')
    overall_summary_table = tabulate(overall_summary_data, tablefmt="plain")
    road_runs_summary_table = tabulate(road_runs_summary_data, tablefmt="plain")
    trail_runs_summary_table = tabulate(trail_runs_summary_data, tablefmt="plain")

    # Combine tables and print
    result_table = f"\n------- Four-Week Rolling Overall Run Summary -------\n{overall_summary_table}\n\n  ------- Four-Week Rolling Road Run Summary -------\n {road_runs_summary_table}\n\n------- Four-Week Rolling Trail Run Summary -------\n{trail_runs_summary_table} \n \nStats created using StravaAPI by Omkar"
    print(result_table)
    
    return result_table
        
