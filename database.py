from redis import Redis
from neo4j import GraphDatabase

class NeoConnection:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def query(self, query_string):
        with self.driver.session() as session:
            result = session.run(query_string)
            return result.data()

class RedisConnection:

    def __init__(self, host, port):
        self.db = Redis(host=host, port=port, decode_responses=True)