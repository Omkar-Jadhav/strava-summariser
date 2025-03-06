from datetime import datetime
import json
import certifi
from pymongo.mongo_client import MongoClient
import logging
import os
# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Adjust logging level as needed

def initiate_mango_connection():
    """Connects to the MongoDB database and logs success or errors."""

    ca = certifi.where()  # Load the updated CA bundle
    uri = os.environ.get("mango_url")

    logger.debug("Connecting to MongoDB with URI: %s", uri)

    try:
        # Create a new client and connect to the server
        client = MongoClient(uri, tlsCAFile=ca)
        logger.info("Before ping!")
        # Send a ping to confirm a successful connection
        # client.admin.command('ping')
        logger.info(client)
        logger.info("Successfully connected to MongoDB!")
        return client
    except Exception as e:
        logger.error("Error connecting to MongoDB: %s", str(e))
        return None

def check_athlete_in_data(client, athlete_id):
    """Checks if an athlete ID exists in the database and logs results."""

    logger.debug("Checking for athlete ID %s in database", athlete_id)

    db = client["strava"]
    collection = db["refresh tokens"]

    logger.info("before find")
    results = collection.find({"athlete_id":int(athlete_id)})
    logger.info(results)

    for result in results:
        # logger.debug("Found document: %s", result)
        logger.info(result)
        refresh_token = result.get("refresh_token")
        if refresh_token:
            logger.info("Found refresh token for athlete ID %s", athlete_id)
            return refresh_token

    logger.info("No refresh token found for athlete ID %s", athlete_id)
    return None


def check_athlete_in_training_data(client, athlete_id):
    """Checks if an athlete ID exists in the database and logs results."""

    logger.debug("Checking for athlete ID %s in database", athlete_id)

    db = client["strava"]
    collection = db["workout_details"]

    logger.info("before find")
    workouts = collection.find_one({"athlete_id": int(athlete_id)})
    logger.info(workouts)
    if workouts:
        if len(workouts)>=1:
            return True
        else:
            return False
    else:
        return False

def check_session_token_in_data(client, session_token):
    logger.info("Checking for session token %s in database", session_token)
    db = client["strava"]
    collection_refresh_tokens = db["refresh tokens"]
    collection_workouts = db["workout_details"]
    results_tokens = collection_refresh_tokens.find({"session_token": session_token}) 
    previous_workout_plan=''
    athlete_id = None
    for result in results_tokens:
        athlete_id = result.get("athlete_id")
        expires_at = result.get("expires_at", datetime.now())
        refresh_token = result.get("refresh_token")
        athlete_name = result.get("athlete_name", '')
    if athlete_id:   
        results_workouts = collection_workouts.find({"athlete_id": athlete_id})
        for result in results_workouts:
            previous_workout_plan = result.get("workout_plan")[0]
        return athlete_id, expires_at, refresh_token, previous_workout_plan, athlete_name
    else:
        return None, None, None, None, None
        
def update_tokens(client, session_token, athlete_id):
    """Updates the tokens in the database and logs success or errors."""

    db = client["strava"]
    collection = db["refresh tokens"]

    try:
        result = collection.update_one(
            {"athlete_id":int(athlete_id)},
            {"$set": {"session_token": session_token}},
        )
        logger.info("Updated tokens for session token %s", session_token)
        return result.modified_count
    except Exception as e:
        logger.error("Error updating tokens: %s", str(e))
        return None
    
def key_in_any_dict(lst, key):
    for dictionary in lst:
        if key in dictionary:
            return True
    return False

def get_dict_with_key(lst, key):
    for index, dictionary in enumerate(lst):
        if key in dictionary:
            return index, dictionary
        
    return None, None  # Return None if the key is not found in any dictionary

def save_workout_plan(athlete_id, plan, dates, goal_summary='',  notes=''):
    client = initiate_mango_connection()
    collection = client["strava"]['workout_details']
    try:
        workouts = collection.find_one({"athlete_id": int(athlete_id)})
        if workouts:
            past_workouts =  workouts.get('workout_plan')
            goal_summary = workouts.get('goal_summary')
            if  key_in_any_dict(past_workouts, dates):
                index, workout =get_dict_with_key(past_workouts, dates)
                workout[dates]['workout_plan']=plan
                if notes!="":
                    workout[dates]['notes'] = notes
                past_workouts[index]= workout
                collection.update_one(
                    {"athlete_id": int(athlete_id)},
                    {"$set": {"workout_plan": past_workouts, "goal_summary":goal_summary,}},
                    upsert=False  
                )  
            elif len(past_workouts)>5:
                past_workouts.pop(0)
                past_workouts.append({dates: {"workout_plan":plan, "notes":notes} })
                collection.update_one(
                    {"athlete_id": int(athlete_id)},
                    {"$set": {"workout_plan": past_workouts, "goal_summary":goal_summary}},
                    upsert=False  
                )
            else:
                past_workouts.append({dates:{'workout_plan':plan, 'notes':notes}})
                collection.update_one(
                    {"athlete_id": int(athlete_id)},
                    {"$set": {"workout_plan": past_workouts, "goal_summary":goal_summary}},
                    upsert=False  
                )
        else:
            collection.insert_one({
                    "athlete_id": int(athlete_id),
                    "workout_plan": [{dates:{"workout_plan":plan, "notes":notes}}],
                    "goal_summary":goal_summary
                })
        logger.info("Saved workout data for athlete %s successfully for %s", athlete_id, str(dates))
        return "Workout saved"
    except Exception as e:
        logger.error("Error saving or updating athlete data: %s", str(e))
        return None
        

def save_athlete_data(client, data, collection_name ="refresh tokens"):
    """Saves or updates athlete data in the database and logs success or errors."""

    athlete_id = data["athlete_id"]
    refresh_token = data["refresh_token"]
    athlete_name = data["athlete_name"]
    session_token = data.get("session_token", '')
    expires_at = data.get("expires_at", datetime.now())
    previous_workout_plan = data.get("previous_workout_plan", '')
    athlete_preferences = data.get("athlete_preferences", '')

    db = client["strava"]
    collection = db[collection_name]

    try:
        existing_data = collection.find_one({"athlete_id": int(athlete_id)})
        if existing_data:
            update_fields = {}
            if existing_data.get("refresh_token") != refresh_token:
                update_fields["refresh_token"] = refresh_token
            if existing_data.get("athlete_name") != athlete_name:
                update_fields["athlete_name"] = athlete_name
            if existing_data.get("session_token") != session_token:
                update_fields["session_token"] = session_token
            if existing_data.get("expires_at") != expires_at:
                update_fields["expires_at"] = expires_at
            if existing_data.get("previous_workout_plan") != previous_workout_plan:
                update_fields["previous_workout_plan"] = previous_workout_plan
            if existing_data.get("athlete_preferences") != athlete_preferences:
                update_fields["athlete_preferences"] = athlete_preferences

            if update_fields:
                collection.update_one({"athlete_id": int(athlete_id)}, {"$set": update_fields})
                logger.info("Updated athlete data for ID %s successfully", athlete_id)
            else:
                logger.info("No changes detected for athlete ID %s", athlete_id)
            return "Updated"
        else:
            collection.insert_one({
                "athlete_id": int(athlete_id),
                "refresh_token": refresh_token,
                "athlete_name": athlete_name,
                "session_token": session_token,
                "expires_at": expires_at,
                "previous_workout_plan": previous_workout_plan,
                "athlete_preferences": athlete_preferences
            })
            logger.info("Saved athlete data for ID %s successfully", athlete_id)
            return "Saved"
    except Exception as e:
        logger.error("Error saving or updating athlete data: %s", str(e))
        return None


def get_access_token_for_athlete(athlete_id):
    client=initiate_mango_connection()
    
    db = client["strava"]
    collection = db["refresh tokens"]
    results = collection.find({"athlete_id":athlete_id})
    logger.info(results)
    refresh_token =""
    
    for result in results:
        logger.info(result)
        refresh_token = result.get("refresh_token")
        
    close_client(client)
    return refresh_token

def get_athelte_training_details(athlete_id):
    client = initiate_mango_connection()
    logger.info(f"Checking athlete training details for {athlete_id}")
    db = client["strava"]
    collection = db["workout_details"]
    results = collection.find({"athlete_id":int(athlete_id)})   
    for result in results:
        # logger.info(result)
        latest_workout_plan = result.get("workout_plan")[-1]
        goal_summary = result.get("goal_summary")
        # logger.info(f"Latest workout plan is {latest_workout_plan}")
        logger.info(f"Goal summary is {goal_summary}")
    close_client(client)
    dates =list(latest_workout_plan.keys())[0]
    plan = list(latest_workout_plan.values())[0]['workout_plan']
    notes = list(latest_workout_plan.values())[0]['notes']
    
    return dates,plan, notes,goal_summary
        
    
    
def close_client(client):
    """Closes the connection to the MongoDB client and logs it."""

    logger.info("Closing connection to MongoDB")
    client.close()

def delete_all_data(client):
    """Deletes all data from the collection and logs the action."""

    db = client["database-name"]
    collection = db["collection-name"]

    logger.info("Deleting all data from collection")
    result = collection.delete_many({})
    logger.info("Deleted %d documents", result.deleted_count)

def test_saving():
    client = initiate_mango_connection()
    # delete_all_data(client)
    test_json = {
    "athlete_id": "64768690",
        "refresh_token": "239efcb1a295abda6e7d930587d120817cb5997d",
        "athlete_name": "Omkar Jadhav"
    }
    message = save_athlete_data(client,test_json)
    
    refresh_token=check_athlete_in_data(client,test_json["athlete_id"])
    close_client(client)
    print(refresh_token)
    

# test_saving()
    
    
    