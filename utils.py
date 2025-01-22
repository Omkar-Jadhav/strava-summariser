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

def calculate_speed(moving_time, distance):
    if distance == 0:
        return "00:00 min/Km"
    mov_speed_min, mov_speed_sec = map(int, divmod(moving_time / distance, 60))
def calculate_speed_in_kmph(moving_time, distance):
    if moving_time == 0:
        return "0.00 km/hr"
    speed_kph = (distance / 1000) / (moving_time / 3600)
def calculate_pace_minKm(moving_time, distance):
    if distance == 0:
        return "00:00 min/Km"
    pace_seconds_per_km = moving_time / (distance / 1000)
    pace_minutes = int(pace_seconds_per_km // 60)
    pace_seconds = int(pace_seconds_per_km % 60)
    return f"{pace_minutes:02d}:{pace_seconds:02d} min/Km"
   