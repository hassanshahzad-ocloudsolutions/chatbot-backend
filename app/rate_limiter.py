import os 
from fastapi import HTTPException, Request
from redis.asyncio import Redis
from app.config import REDIS_URL

RATE_LIMIT = 10
WINDOW = 60

redis = Redis.from_url(REDIS_URL, decode_responses=True)

async def rate_limit(request:Request):
    client_ip = request.client.host
    key=f"rate:{client_ip}"
    
    count = await redis.get(key)
    if count:
        count = int(count)
        if count>=RATE_LIMIT:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        await redis.incr(key)
    
    else:
        await redis.set(key,1,ex=WINDOW)