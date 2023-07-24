import uvicorn
from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_pagination import add_pagination
from redis import asyncio as aioredis

from app.blog.routers import post_router
from app.user.routers import user_router
from config import APP_PORT, REDIS_HOST, REDIS_PORT

app = FastAPI(title='blog_app')

app.include_router(user_router)
app.include_router(post_router)
add_pagination(app)


@app.on_event("startup")
async def startup_event():
    redis = aioredis.from_url(f"redis://{REDIS_HOST}:{REDIS_PORT}",
                              encoding="utf8",
                              decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")


if __name__ == "__main__":
    uvicorn.run('main:app', host="0.0.0.0", port=APP_PORT, reload=True)
