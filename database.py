import certifi
from pymongo.mongo_client import MongoClient
import logging

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Adjust logging level as needed

def initiate_mango_connection():
    """Connects to the MongoDB database and logs success or errors."""

    ca = certifi.where()  # Load the updated CA bundle
    uri = "mongodb+srv://omkarjadhav00:mango@strava-refresh-tokens.c46zw8h.mongodb.net/?retryWrites=true&w=majority"

    logger.debug("Connecting to MongoDB with URI: %s", uri)

    try:
        # Create a new client and connect to the server
        client = MongoClient(uri, tlsCAFile=ca,serverSelectionTimeoutMS=10000)
        logger.info("Before ping!")
        # Send a ping to confirm a successful connection
        client.admin.command('ping')
        logger.info("Successfully connected to MongoDB!")
        return client
    except Exception as e:
        logger.error("Error connecting to MongoDB: %s", str(e))
        return None

def check_athlete_in_data(client, athlete_id):
    """Checks if an athlete ID exists in the database and logs results."""

    logger.debug("Checking for athlete ID %s in database", athlete_id)

    db = client["database-name"]
    collection = db["collection-name"]

    results = collection.find({"athlete_id": athlete_id})

    if results.count() == 0:
        logger.info("Athlete ID %s not found in collection", athlete_id)
        return None

    for result in results:
        logger.debug("Found document: %s", result)
        refresh_token = result.get("refresh_token")
        if refresh_token:
            logger.info("Found refresh token for athlete ID %s", athlete_id)
            return refresh_token

    logger.info("No refresh token found for athlete ID %s", athlete_id)
    return None

def save_athlete_data(client, data):
    """Saves athlete data to the database and logs success or errors."""

    athlete_id = data["athlete_id"]
    refresh_token = data["refresh_token"]
    athlete_name = data["athlete_name"]

    db = client["database-name"]
    collection = db["collection-name"]

    try:
        collection.insert_one({
            "athlete_id": athlete_id,
            "refresh_token": refresh_token,
            "athlete_name": athlete_name
        })
        logger.info("Saved athlete data for ID %s successfully", athlete_id)
        return "Saved"
    except Exception as e:
        logger.error("Error saving athlete data: %s", str(e))
        return None

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
    delete_all_data(client)
    test_json = {
    "athlete_id": "64768690",
        "refresh_token": "239efcb1a295abda6e7d930587d120817cb5997d",
        "athlete_name": "Omkar Jadhav"
    }
    # message = save_athlete_data(client,test_json)
    
    refresh_token=check_athlete_in_data(client,test_json["athlete_id"])
    print(refresh_token)
    

# test_saving()
    
    
    