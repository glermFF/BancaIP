from pymongo import MongoClient
import json

uri = "mongodb://localhost:27017/"
bancaIP_client = MongoClient(uri)

try:
    database = bancaIP_client.get_database("sample_mflix")
    movies = database.get_collection("movies")
    
    query = { "title": "Back to the Future" }
    movie = movies.find_one(query)
    print(json.dumps(movie, indent=4, default=str))
    bancaIP_client.close()
except Exception as e:
    raise Exception("Unable to find the document due to the following error: ", e)
