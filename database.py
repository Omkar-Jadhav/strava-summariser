import certifi
from pymongo.mongo_client import MongoClient

def initiate_mango_connection():
    ca = certifi.where()  # Load the updated CA bundle
    uri = "mongodb+srv://omkarjadhav00:mango@strava-refresh-tokens.c46zw8h.mongodb.net/?retryWrites=true&w=majority"

    # Create a new client and connect to the server
    client = MongoClient(uri,tlsCAFile=ca)
    # Send a ping to confirm a successful connection
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
        return client
    except Exception as e:
        print(e)
        return None
    
def check_athlete_in_data(client, athlete_id):
    db = client["database-name"]
    collection = db["collection-name"]

    # results = collection.find({"key": athlete_id})s
    results = collection.find({})
    value = None
    
        # Get the value from the retrieved document
    for result in results:
        print(result)
        if result.get(str(athlete_id)) is None:
            print(f"Key '{athlete_id}' not found in the collection.")
        else:
            value = result.get(str(athlete_id)).get('refresh_token')  # Accessing nested value
            print(f"Value for key '{athlete_id}': {value}")
            break
              # Return refresh_token if found
    
    return value
        
    

def save_athlete_data(client, data):
    athlete_id = data['athlete_id']
    refresh_token = data['refresh_token']
    athlete_name = data ['athlete_name']
    
    db = client["database-name"]
    collection = db["collection-name"]

    tokens_data={}
    tokens_data[str(athlete_id)] = {
                "refresh_token": refresh_token,
                "athlete_name": athlete_name
            }
    collection.insert_one(tokens_data)

    # Example: Reading data
    results = collection.find({})
    for result in results:
        print(result)
    
    return "Saved"
    
        
def close_client(client):
    client.close()

def delete_all_data(client):
    db = client["database-name"]
    collection = db["collection-name"]
    result = collection.delete_many({})

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
    
    
    