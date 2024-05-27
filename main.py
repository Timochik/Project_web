import uvicorn
import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from src.repository.users import get_user_by_id
from src.utils.users import add_first_user_admin
from src.routes import auth, users, admin, images, comments, ratings


app = FastAPI()
templates = Jinja2Templates(directory="src/templates")

app.include_router(auth.router, prefix='/api')
app.include_router(users.router, prefix='/api')
app.include_router(admin.router, prefix='/api')
app.include_router(images.router, prefix='/api')
app.include_router(comments.router, prefix='/api')
app.include_router(ratings.router, prefix='/api')


@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    """
    The read_root function is a function that returns the string &quot;Hello World&quot;
    in JSON format. This is an example of how to use FastAPI to create a ReST API.
    
    :return: A dictionary with a key &quot;message&quot; and
    :doc-author: Trelent
    """
    return templates.TemplateResponse("index.html", {"request": request})

async def main():
    """
    The main function is the entry point for this application.
    It creates an instance of FastAPI, and then starts a Uvicorn server with it.
    
    
    :return: A coroutine
    :doc-author: Trelent
    """
    admin = await get_user_by_id(user_id=1)
    if not admin:
        await add_first_user_admin()


if __name__ == "__main__":
    asyncio.run(main())
    uvicorn.run('main:app', host="localhost", port=8000, reload=True)