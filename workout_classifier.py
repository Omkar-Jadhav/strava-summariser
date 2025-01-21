import logging
import numpy as np
import requests
from utils import calculate_pace_minKm, calculate_speed
import utils
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Adjust logging level as needed

def compute_statistics(activities):
    """Compute mean and standard deviation for distance, pace, and heart rate."""
    distances = [activity.get('distance', 0) / 1000 for activity in activities]  # km
    avg_speeds = [activity.get('average_speed', 0) * 3.6 for activity in activities]  # km/h
    avg_hrs = [activity.get('average_heartrate', 0) for activity in activities]

    stats = {
        'distance_mean': np.mean(distances),
        'distance_std': np.std(distances),
        'speed_mean': np.mean(avg_speeds),
        'speed_std': np.std(avg_speeds),
        'hr_mean': np.mean(avg_hrs),
        'hr_std': np.std(avg_hrs)
    }
    return stats

def classify_workout(activity, stats, headers):
    """Classify the workout based on dynamic metrics."""
    distance = activity.get('distance', 0) / 1000  # km
    avg_speed = activity.get('average_speed', 0) * 3.6  # km/h
    avg_hr = activity.get('average_heartrate', 0)
    max_hr = activity.get('max_heartrate', 0)
    
    if activity["workout_type"] == 1:
        return "Race"+ f"\n{get_race_details(activity)}"
    
    if activity['sport_type'] == 'TrailRun':
        return "Trail Run"+ f"\n{get_trail_run_details(activity)}"
    
    if distance > stats['distance_mean'] + stats['distance_std'] and (avg_hr ==0 or avg_hr <= stats['hr_mean']+0.6*stats['hr_std']):
        return "Long Run" + f"\n{get_long_run_details(activity)}"
    
    if stats['distance_mean'] - stats['distance_std'] <= distance <= stats['distance_mean'] + stats['distance_std'] and (avg_hr ==0 or avg_hr >= stats['hr_mean']+0.7*stats['hr_std']):
        return "Tempo Workout"
    
    if distance < stats['distance_mean'] and (avg_hr ==0 or avg_hr <= stats['hr_mean']+0.4*stats['hr_std']) and (max_hr ==0 or max_hr <= stats['hr_mean']+1.1*stats['hr_std']):
        return "Easy Run"
    
    if distance < stats['distance_mean'] - stats['distance_std'] and (avg_hr ==0 or avg_hr <= stats['hr_mean']+0.25*stats['hr_std']):
        return "Recovery Run"
    
    if activity['type'] == 'Run' and (avg_hr ==0 or avg_hr >= stats['hr_mean']+0.8*stats['hr_std']) and avg_speed >= stats['speed_mean']+0.8*stats['speed_std']:
        return "Threshold Run"
    
    activity_complete = fetch_complete_activity_detail(activity['id'], headers)
    if 'laps' in activity_complete:
        laps = activity_complete.get('laps', [])
        pace_changes = [lap['average_speed'] for lap in laps]
        if len(pace_changes) >= 3 and (max(pace_changes) / min(pace_changes)) > 1.5:
            logger.info(f"Activity {activity['id']} is classified as Intervals")
            
            return "Intervals\n" + "\n".join(get_interval_run_details(laps))
        
    return "Other"

def get_interval_run_details(laps):
    """Get interval run details."""
    lap_speeds = [round(((1000/lap['average_speed'])/60),2) for lap in laps] # Avg speed in m/s converting it to min/Km
    lap_distances = [lap['distance']/1000 for lap in laps]
    
    lap_details =[f"Lap {i+1}: {lap_distances[i]:.2f} km at {lap_speeds[i]} min/Km" for i in range(len(lap_speeds))]    
    return lap_details

def get_long_run_details(activity):
    avg_pace = calculate_pace_minKm(activity['moving_time'], activity['distance'])
    return f"{activity['distance']/1000:.2f} km at Avg pace: {avg_pace} min/Km"

def get_trail_run_details(activity):
    return f"{activity['distance']/1000:.2f} km with total elevation gain of {activity['total_elevation_gain']} m"

def get_race_details(activity):
    return f"{activity['distance']/1000:.2f} km at Avg pace: {calculate_pace_minKm(activity['moving_time'], activity['distance'])} min/Km and total elevation gain of {activity['total_elevation_gain']} m"
    
def get_run_type(activities, headers):
    """Classify the workout based on dynamic metrics."""
    stats = compute_statistics(activities)
    run_types = []
    for activity in activities:
        run_types.append(classify_workout(activity, stats, headers))
    return run_types

def fetch_complete_activity_detail(activty_id, headers):
    """Fetch complete activity details."""
    activity_url = f"https://www.strava.com/api/v3/activities/{activty_id}"
    response = requests.get(activity_url,headers= headers)
    if response.status_code == 200:
        return response.json()
    return None
