from flask import Flask, render_template
from database import NeoConnection, RedisConnection
import atexit

app = Flask(__name__)

Neo = NeoConnection("bolt://localhost:7687", "neo4j", "password")
atexit.register(Neo.close)

Redis = RedisConnection('localhost', 6379)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/test')
def test():
    user_id = 16190898  # Replace with the actual user ID
    result = Neo.query(f'MATCH (specificUser:User {{id: {user_id}}})-[:FOLLOWS]->(follower:User), '
                    '(follower)-[:FOLLOWS]->(commonUser:User) '
                    'WHERE specificUser <> commonUser '
                    'AND NOT (specificUser)-[:FOLLOWS]->(commonUser) '
                    'RETURN DISTINCT commonUser.id '
                    'LIMIT 5')
    return render_template('test.html', data=result, user_id=user_id)

@app.route('/test1')
def test1():
    # Step 3 and 4: Cypher Query
    user_id = 16190898  # Replace with the actual user ID
    query = f"""
        MATCH (source:User {{id: {user_id}}})-[:FOLLOWS]->(follower:User)
        WITH source, COLLECT(follower) AS followers
        MATCH (source)-[similarity:SIMILARITY]-(similarUser:User)
        RETURN similarUser.id AS similarUserId, similarity.cosineSimilarity AS similarityPercentage
        ORDER BY similarityPercentage DESC
        LIMIT 5;
    """
    result = Neo.query(query)

    return render_template('test1.html', data=result, user_id=user_id)

if __name__ == '__main__':
    app.run(debug=True)