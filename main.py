import uvicorn
from fastapi import FastAPI

from src.routes import auth, users, admin

app = FastAPI()

app.include_router(auth.router, prefix='/api')
app.include_router(users.router, prefix='/api')
app.include_router(admin.router, prefix="/admin", tags=["admin"])

@app.get("/")
def read_root():
    """
    The read_root function is a function that returns the string &quot;Hello World&quot;
    in JSON format. This is an example of how to use FastAPI to create a ReST API.
    
    :return: A dictionary with a key &quot;message&quot; and
    :doc-author: Trelent
    """
    return {"message": "Hello World"}

if __name__ == "__main__":
    uvicorn.run('main:app', host="localhost", port=8000, reload=True)