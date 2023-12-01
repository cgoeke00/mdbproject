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

if __name__ == '__main__':
    app.run(debug=True)