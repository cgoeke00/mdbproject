from flask import Flask, render_template, request, jsonify
from database import NeoConnection, RedisConnection
import atexit

app = Flask(__name__)

Neo = NeoConnection("bolt://localhost:7687", "neo4j", "password")
atexit.register(Neo.close)

Redis = RedisConnection('localhost', 6379)

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

    # Similarity Query
    similarity_query = f"""
        MATCH (source:User {{id: {user_id}}})-[:FOLLOWS]->(follower:User)
        WITH source, COLLECT(follower) AS followers
        MATCH (source)-[similarity:SIMILARITY]-(similarUser:User)
        RETURN similarUser.id AS similarUserId, similarity.cosineSimilarity AS similarityPercentage
        ORDER BY similarityPercentage DESC
        LIMIT 5;
    """
    similarity_data = Neo.query(similarity_query)

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

    return render_template('results.html', similarity_data=similarity_data, recommended_data=recommended_data, user_id=user_id)

if __name__ == '__main__':
    app.run(debug=True)