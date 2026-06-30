import json
import redis
import numpy as np
from services.indexing_service import indexing_service

redis_client = redis.Redis(host="redis_broker", port=6379, db=1) # Use db=1 to isolate f

# function to check if the current query is in the cache
def check_semantic_cache(query: str):
    
    # Hash the query
    query_hash = f"cache:query:{hash(query)}"
    cached_response = redis_client.get(query_hash)
    if cached_response: # cache hit - return the cache
        print("Cache Hit: Serving exact matching answer directly from Redis!")
        return json.loads(cached_response)
        
    return None

# Function to save the query to cache
def save_to_cache(query: str, response_dict: dict, ttl_seconds=3600):
    """ Save the generated answer to Redis with an expiration timeout """
    # hash the query
    query_hash = f"cache:query:{hash(query)}"
    # Cache the result for 1 hour (3600 seconds)
    redis_client.setex(query_hash, ttl_seconds, json.dumps(response_dict))