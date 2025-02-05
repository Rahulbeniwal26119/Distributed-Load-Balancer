import logging
import redis.asyncio as aioredis
from fastapi import FastAPI, Request, HTTPException, Depends
import os

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("main")
app = FastAPI()

SENTINEL_HOSTS = os.getenv(
    "SENTINEL_HOSTS", "sentinel-1:26379,sentinel-2:26379,sentinel-3:26379"
).split(",")
MASTER_NAME = os.getenv("REDIS_MASTER", "redis-master")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "master")


RATE_LIMIT = int(os.getenv("RATE_LIMIT", 10))
TIME_WINDOW = int(os.getenv("TIME_WINDOW", 60))

redis_connection = None


async def get_redis_connection():
    global redis_connection
    if not redis_connection:
        sentinel = aioredis.Sentinel(
            [(host.split(":")[0], int(host.split(":")[1])) for host in SENTINEL_HOSTS],
            password=REDIS_PASSWORD,
            sentinel_kwargs={
                "socket_timeout": 0.5,
            },
        )
        # get master for writes
        redis_connection = sentinel.master_for(MASTER_NAME, max_connections=10)
    return redis_connection


def host_info():
    return {
        "HOSTNAME": os.getenv("HOSTNAME"),
        "SENTINEL_HOSTS": SENTINEL_HOSTS,
    }


async def rate_limiter(
    request: Request, redis_connection=Depends(get_redis_connection)
):
    try:
        client_ip = request.client.host
        key = f"rate_limit:{client_ip}"

        async with redis_connection.pipeline() as pipe:
            pipe.incr(key)
            pipe.expire(key, TIME_WINDOW)
            request_count, ttl = await pipe.execute()

            if request_count > RATE_LIMIT:
                raise HTTPException(status_code=429, detail="Too Many Requests")
    except Exception as e:
        logger.exception("Error occurred in rate_limiter")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    return {"message": "Hello World", "host_info": host_info()}


@app.get("/limited_endpoint", dependencies=[Depends(rate_limiter)])
async def limited_endpoint():
    return {"message": "This is a limited endpoint", "host_info": host_info()}


@app.on_event("startup")
async def startup_event():
    global redis_connection
    redis_connection = await get_redis_connection()


@app.on_event("shutdown")
async def shutdown_event():
    global redis_connection
    if redis_connection:
        await redis_connection.close()


@app.get("/health")
async def health():
    return {"status": "ok"}
