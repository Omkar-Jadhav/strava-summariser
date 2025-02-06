from pymongo.mongo_client import MongoClient
import database
from test_plan_data import athlete_id
uri = "mongodb+srv://omkarjadhav00:mango@strava-token.6r1ebob.mongodb.net/?ssl=true&ssl_cert_reqs=CERT_NONE&retryWrites=true&w=majority"

# Create a new client and connect to the server
# client = MongoClient(uri)
# # Send a ping to confirm a successful connection
# try:
#     client.admin.command('ping')
#     print("Pinged your deployment. You successfully connected to MongoDB!")
# except Exception as e:
#     print(e)
athlete_id="64768690"
database.get_athelte_training_details(athlete_id)