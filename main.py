from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from starlette import status
from starlette.responses import RedirectResponse, Response

from models import Base, Todo
from database import engine, SessionLocal
from routers.auth import router as auth_router
from routers.todo import router as todo_router

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_root(request: Request):
    return RedirectResponse(url="/todo/todo-page", status_code=status.HTTP_302_FOUND)

@app.get("/favicon.ico")
async def favicon():
    return Response(status_code=status.HTTP_204_NO_CONTENT)

app.include_router(auth_router)
app.include_router(todo_router)

Base.metadata.create_all(bind=engine)
