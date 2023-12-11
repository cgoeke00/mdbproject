from flask import Flask, render_template, request, jsonify
from database import NeoConnection, RedisConnection
import atexit
import redis
import json

app = Flask(__name__)

Neo = NeoConnection("bolt://localhost:7687", "neo4j", "password")
atexit.register(Neo.close)

Redis = RedisConnection('localhost', 6379)
client = redis.Redis(port=6379);

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/results')
def combined():
    # user_id = 16190898  # Replace with the actual user ID
    # Retrieve the user ID from the form data
    user_id = request.args.get('user_id', '')
    if not user_id:
        # Handle the case where user ID is not provided
        return "Please enter a user ID."
    
    user_data = client.smembers(user_id)
    json_data = []
    for item in user_data:
        if isinstance(item, bytes):
            item = item.decode('utf-8')
        try:
            json_obj = json.loads(item)
            json_data.append(json_obj)
        except json.JSONDecodeError:
            print(f"Error decoding JSON for item: {item}")

    username = json_data[0].get('username', [])
    tags = json_data[0].get('tags', [])
    pfp = json_data[0].get('pfp', [])

    user_data={
        'name': username,
        'tags': tags,
        'pfp': pfp
    }

    # Similarity Query
    similarity_query = f"""
        MATCH (source:User {{id: {user_id}}})-[:FOLLOWS]->(follower:User)
        WITH source, COLLECT(follower) AS followers
        MATCH (source)-[similarity:SIMILARITY]-(similarUser:User)
        RETURN DISTINCT similarUser.id AS similarUserId, similarity.cosineSimilarity*100 AS similarityPercentage
        ORDER BY similarityPercentage DESC
        LIMIT 5;
    """
    similarity_data = Neo.query(similarity_query)
    print(similarity_data)
    similarity_list = []
    for user in similarity_data:
        data = client.smembers(user['similarUserId'])
        json_data = []
        for item in data:
            if isinstance(item, bytes):
                item = item.decode('utf-8')
            try:
                json_obj = json.loads(item)
                json_data.append(json_obj)
            except json.JSONDecodeError:
                print(f"Error decoding JSON for item: {item}")

        username = json_data[0].get('username', [])
        tags = json_data[0].get('tags', [])
        pfp = json_data[0].get('pfp', [])
        user_data = {
            'id': user['similarUserId'],
            'name': username,
            'tags':tags,
            'pfp': pfp,
            'similarity': user['similarityPercentage']
        }
        similarity_list.append(user_data)


    # Recommended Users Query
    recommended_query = f"""
        MATCH (specificUser:User {{id: {user_id}}})-[:FOLLOWS]->(follower:User),
              (follower)-[:FOLLOWS]->(commonUser:User)
        WHERE specificUser <> commonUser
        AND NOT (specificUser)-[:FOLLOWS]->(commonUser)
        RETURN DISTINCT commonUser.id
        LIMIT 5;
    """
    recommended_data = Neo.query(recommended_query)
    recommended_list = []
    for user in recommended_data:
        data = client.smembers(user['commonUser.id'])
        json_data = []
        for item in data:
            if isinstance(item, bytes):
                item = item.decode('utf-8')
            try:
                json_obj = json.loads(item)
                json_data.append(json_obj)
            except json.JSONDecodeError:
                print(f"Error decoding JSON for item: {item}")

        username = json_data[0].get('username', [])
        tags = json_data[0].get('tags', [])
        pfp = json_data[0].get('pfp', [])
        user_data = {
            'id': user['commonUser.id'],
            'name': username,
            'tags':tags,
            'pfp': pfp
        }
        recommended_list.append(user_data)

    return render_template('results.html', similarity_data=similarity_list, recommended_data=recommended_list, user_id=user_id, user_data=user_data)

if __name__ == '__main__':
    app.run(debug=True, port=5001)