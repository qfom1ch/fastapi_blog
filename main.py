import uvicorn
from fastapi import FastAPI
from fastapi_pagination import add_pagination

from config import APP_PORT
from app.user.routers import user_router

app = FastAPI(title='blog_app')


app.include_router(user_router)
add_pagination(app)

if __name__ == "__main__":
    uvicorn.run('main:app', host="0.0.0.0", port=APP_PORT, reload=True)
