import redis
from neo4j import GraphDatabase
import csv
import json

# Redis client
redisClient = redis.Redis(port=6379);
redisClient.flushdb()

# Neo client
neo4jUrl = "bolt://localhost:7687"
neo4jDriver = GraphDatabase.driver(neo4jUrl, auth=('neo4j', 'password'))
session = neo4jDriver.session()
session.run('MATCH (n) DETACH DELETE n')

# The CSV file containing the profile data
csvFilename = "data.csv"
# Track how many file lines we've processed
processedLines = 0


## This function loops through the
## CSV data file and populates Redis
def populateRedis():
    line_count = 0
    with open(csvFilename, encoding="utf8") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for data in csv_reader:

            id = data['id'];
            user = data['screenName']
            tags = data['tags']
            pfp = data['avatar']
            followersCount = data['followersCount']
            followers = data['friends']
            if followers != '[]':
                followers = data['friends'].split('[ ') + data[None]

            profileObj = {
                "userId": id,
                "username": user,
                "tags": tags,
                "pfp": pfp,
                "followersCount": followersCount,
                "followers": clean_strings(followers)
            }
    
            line_count += 1
            if line_count%100 == 0:
                print(f'Processed {line_count} lines.')

            # Populate Redis
            redisClient.sadd(id, json.dumps(profileObj))

            # Create Neo nodes
            session.run('CREATE (u:User {id: ' + id + '})')


    print(f'Processed {line_count} lines.')

# Add follow relationships to Neo nodes
def addRelationships():
    rel_count = 0;
    with open(csvFilename, encoding="utf8") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for data in csv_reader:

            id = data['id'];
            followers = data['friends']
            if followers != '[]':
                followers = data['friends'].split('[ ') + data[None]

            followers = clean_strings(followers)

            for follower in followers:
                # Create Neo relationships
                if follower and follower != '':
                    session.run('MATCH (u1:User {id: ' + id + '}) MATCH (u2:User {id: ' + follower + '}) MERGE (u1)-[:FOLLOWS]->(u2)')
                    rel_count += 1

                if rel_count%500 == 0:
                    print(f'Added {rel_count} Relationships.')

    print(f'Added {rel_count} relationships.')


def clean_strings(string_list):
    # Remove unwanted characters and filter out empty strings
    cleaned_list = [s.replace('"', '').replace(']', '').replace(' ', '').replace('[', '') for s in string_list if s != ''and s != '[']
    return cleaned_list


populateRedis();
addRelationships();
redisClient.quit();