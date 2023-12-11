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

# Running Similarity Relationship
# Similarity Query
  - In order to the the similarity function correct it is important to run these two queries in Neo4j first

  # STEP 1 in Neo4j ***** 
  - Create a graph projection named 'SimilarUsers' based on the 'FOLLOWS' relationship, considering nodes with the 'User' label.
  
  CALL gds.graph.project('SimilarUsers', ['User'], 'FOLLOWS')  ​

  # STEP 2 in Neo4j ***** 
  - nodeLabels: Labels of nodes to include in the similarity computation ('User' in this case).
  - relationshipTypes: Types of relationships to consider ('FOLLOWS' in this case).
  - topK: The number of top similar nodes to store for each node (5 in this case).
  - similarityCutoff: The similarity cutoff value to filter out weak similarities (0.2 in this case).
  - writeRelationshipType: The type of relationship to write to store the similarity information ('SIMILARITY').
  - writeProperty: The property to write on the relationship to store the similarity value ('cosineSimilarity').

  CALL gds.nodeSimilarity.write('SimilarUsers', {  ​
    nodeLabels: ['User'],  ​
    relationshipTypes: ['FOLLOWS'],  ​
    topK: 5,  ​
    similarityCutoff: 0.2,  ​
    writeRelationshipType: 'SIMILARITY',  ​
    writeProperty: 'cosineSimilarity'  });  