import flask
import requests

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
   