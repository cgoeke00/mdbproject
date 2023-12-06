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
    data = Neo.query(f'MATCH (specificUser:User {{id: {user_id}}})-[:FOLLOWS]->(follower:User), '
                    '(follower)-[:FOLLOWS]->(commonUser:User) '
                    'WHERE specificUser <> commonUser '
                    'AND NOT (specificUser)-[:FOLLOWS]->(commonUser) '
                    'RETURN DISTINCT commonUser.id '
                    'LIMIT 5')
    return render_template('test.html', data=data, user_id=user_id)

if __name__ == '__main__':
    app.run(debug=True)