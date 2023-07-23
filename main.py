import uvicorn
from fastapi import FastAPI
from fastapi_pagination import add_pagination

from app.blog.routers import post_router
from app.user.routers import user_router
from config import APP_PORT

app = FastAPI(title='blog_app')


app.include_router(user_router)
app.include_router(post_router)
add_pagination(app)

if __name__ == "__main__":
    uvicorn.run('main:app', host="0.0.0.0", port=APP_PORT, reload=True)
