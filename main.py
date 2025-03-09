from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from starlette import status
from starlette.responses import RedirectResponse, Response
from .models import Base, Todo
from .database import engine, SessionLocal
from .routers.auth import router as auth_router
from .routers.todo import router as todo_router
import os

app = FastAPI()
script_directory = os.path.dirname(__file__)
st_abs_file_path = os.path.join(script_directory, "static/")

app.mount("/static", StaticFiles(directory=st_abs_file_path), name="static")

@app.get("/")
async def read_root(request: Request):
    return RedirectResponse(url="/todo/todo-page", status_code=status.HTTP_302_FOUND)

@app.get("/favicon.ico")
async def favicon():
    return Response(status_code=status.HTTP_204_NO_CONTENT)

app.include_router(auth_router)
app.include_router(todo_router)

Base.metadata.create_all(bind=engine)
