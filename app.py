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
    user_id = request.args.get('user_id', '')
    if not user_id:
        return "Please enter a user ID."

    # Retrieve original user data from Redis
    user_data_redis = client.smembers(user_id)
    json_data = []
    for item in user_data_redis:
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

    # Original user_data
    original_user_data = {
        'name': username,
        'tags': tags,
        'pfp': pfp
    }

    # Similarity Query
    
    # STEP 1 in Neo4j ***** 
    # Create a graph projection named 'SimilarUsers' based on the 'FOLLOWS' relationship, considering nodes with the 'User' label.
    # CALL gds.graph.project('SimilarUsers', ['User'], 'FOLLOWS')  ​

    # STEP 2 in Neo4j ***** 
    # nodeLabels: Labels of nodes to include in the similarity computation ('User' in this case).
    # relationshipTypes: Types of relationships to consider ('FOLLOWS' in this case).
    # topK: The number of top similar nodes to store for each node (5 in this case).
    # similarityCutoff: The similarity cutoff value to filter out weak similarities (0.2 in this case).
    # writeRelationshipType: The type of relationship to write to store the similarity information ('SIMILARITY').
    # writeProperty: The property to write on the relationship to store the similarity value ('cosineSimilarity').

    # CALL gds.nodeSimilarity.write('SimilarUsers', {  ​
    #     nodeLabels: ['User'],  ​
    #     relationshipTypes: ['FOLLOWS'],  ​
    #     topK: 5,  ​
    #     similarityCutoff: 0.2,  ​
    #     writeRelationshipType: 'SIMILARITY',  ​
    #     writeProperty: 'cosineSimilarity'  });  
    
    similarity_query = f"""
        MATCH (source:User {{id: {user_id}}})-[:FOLLOWS]->(follower:User)
        WITH source, COLLECT(follower) AS followers
        MATCH (source)-[similarity:SIMILARITY]-(similarUser:User)
        RETURN DISTINCT similarUser.id AS similarUserId, similarity.cosineSimilarity*100 AS similarityPercentage
        ORDER BY similarityPercentage DESC
        LIMIT 5;
    """
    similarity_data = Neo.query(similarity_query)
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

        # Similarity user_data
        similarity_user_data = {
            'id': user['similarUserId'],
            'name': username,
            'tags': tags,
            'pfp': pfp,
            'similarity': user['similarityPercentage']
        }
        similarity_list.append(similarity_user_data)

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

        # Recommended user_data
        recommended_user_data = {
            'id': user['commonUser.id'],
            'name': username,
            'tags': tags,
            'pfp': pfp
        }
        recommended_list.append(recommended_user_data)

    return render_template('results.html', similarity_data=similarity_list, recommended_data=recommended_list, user_id=user_id, user_data=original_user_data)

if __name__ == '__main__':
    app.run(debug=True, port=5001)