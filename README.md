# mdbproject

## Requirments
Python (https://www.python.org/downloads/)
  - Packages: flask, redis, neo4j (pip install flask redis neo4j)
Redis server (https://redis.io/)
Neo4j (https://neo4j.com/)
Dataset: (https://www.kaggle.com/datasets/hwassner/TwitterFriends)

## Instructions
1. Install the required services and run the Redis and Neo4j servers.
   - Database address and credentials are the default and can be changed in app.py if necessary. 
3. Unzip the project folder and navigate to the root directory.
4. Install required packages.
5. Download the dataset and place data.csv in the root directory.
6. Run the db population script (>python populate.py). This may take some time.
7. Run the application (> python app.py). Navigate to localhost:5001 in your browser.

## File structure
  - Templates folder contains html for the search and display page.
  - database.py contains classes for managing each database.
  - populate.py loads the dataset into the databases from a data.csv file.
  - app.py contains routing logic for querying and manipulating data.
