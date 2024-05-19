import redis.asyncio as redis
from fastapi import FastAPI
from fastapi_limiter import FastAPILimiter
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
# from src.routes import contacts, auth
from src.routes import images, admin
from src.conf.config import settings

app = FastAPI()

app.include_router(images.router, prefix='/api')
app.include_router(admin.router, prefix="/admin", tags=["admin"])

@app.get("/")
def read_root():
    return {"message": "Hello World"}
    
if __name__ == '__main__':
    uvicorn.run(app, host='localhost', port=8000, reload=True)
