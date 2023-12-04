import redis
import csv
import json

# Redis client
redisClient = redis.Redis(port=6379);

# The CSV file containing the pokemon data
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
                "followers": followers
            }
    
            line_count += 1
            if line_count%100 == 0:
                print(f'Processed {line_count} lines.')
                return ################################## only do first 100
            ############################################# until format is finalized

            redisClient.sadd(id, json.dumps(profileObj))

    print(f'Processed {line_count} lines.')


populateRedis();
redisClient.quit();