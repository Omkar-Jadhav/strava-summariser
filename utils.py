import flask
import requests

def update_activity(activity_url, update_json, headers):
    update_response = requests.put(activity_url, 
                                   headers=headers, json=update_json)
    
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
    updated_description = f"{description} \n {summary}"
    update_json = {"description": updated_description}
    
    return update_json