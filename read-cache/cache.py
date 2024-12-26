import redis

pool = redis.ConnectionPool(host='localhost', port=6379, db=0, decode_responses=True)
redis_client = redis.StrictRedis(connection_pool = pool)