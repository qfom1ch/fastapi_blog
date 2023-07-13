import uvicorn
from fastapi import FastAPI
from config import APP_PORT

app = FastAPI(title='blog_app')

@app.get('/')
async def get_a():
    return {'Helloy'}

if __name__ == "__main__":
    uvicorn.run('main:app', host="0.0.0.0", port=APP_PORT, reload=True)
