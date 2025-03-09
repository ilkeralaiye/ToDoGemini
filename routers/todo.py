from fastapi import APIRouter, Depends, Path, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import RedirectResponse
from models import Base, Todo
from database import engine, SessionLocal
from typing import Annotated
from routers.auth import getCurrentUser
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import google.generativeai as genai
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage
import markdown
from bs4 import BeautifulSoup

router = APIRouter(prefix="/todo", tags=["toDo"])
templates = Jinja2Templates(directory="templates")

class TodoRequest(BaseModel):
    title:str = Field(min_length= 3)
    description:str = Field(min_length= 3, max_length= 1000)
    priority:int = Field(gt=0, lt=6)
    complete:bool

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "My Task",
                "description": "Task description",
                "priority": 5,
                "complete": False,
            }
        }
    }

def checkUser(user):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(getCurrentUser)]

def redirect_toLogin():
    redirect_response = RedirectResponse(url="/auth/login-page", status_code=status.HTTP_302_FOUND)
    redirect_response.delete_cookie("access_token")
    return redirect_response


@router.get("/todo-page")
async def render_todo_page(request: Request, db: db_dependency):
    try:
        user = await getCurrentUser(request.cookies.get("access_token"))
        if user is None:
            return redirect_toLogin()
        todos = db.query(Todo).filter(Todo.ownerID == user.get("id")).all()
        return templates.TemplateResponse("todo.html", {"request":request, "todos":todos, "user":user})
    except:
        return redirect_toLogin()

@router.get("/add-todo-page")
async def render_add_todo_page(request: Request):
    try:
        user = await getCurrentUser(request.cookies.get("access_token"))
        if user is None:
            return redirect_toLogin()
        return templates.TemplateResponse("add-todo.html", {"request":request, "user":user})
    except:
        return redirect_toLogin()

@router.get("/edit-todo-page/{todo_id}")
async def render_edit_todo_page(request: Request, todo_id: int, db: db_dependency):
    try:
        user = await getCurrentUser(request.cookies.get("access_token"))
        if user is None:
            return redirect_toLogin()
        todo = db.query(Todo).filter(Todo.id == todo_id).first()
        return templates.TemplateResponse("edit-todo.html", {"request":request, "todo":todo, "user":user})
    except:
        return redirect_toLogin()

@router.get("/")
async def read_all(user:user_dependency, db: db_dependency):
    checkUser(user)
    return db.query(Todo).filter(Todo.ownerID == user.get("id")).all()

@router.get("/{todo_id}", status_code=status.HTTP_200_OK)
async def read_by_id(user:user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    checkUser(user)
    todo = db.query(Todo).filter(Todo.id == todo_id).filter(Todo.ownerID == user.get("id")).first()
    if todo is not None:
        return todo
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="To-do not found.")

@router.post("/create_todo", status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency, db: db_dependency, todo_request: TodoRequest):
    checkUser(user)
    todo = Todo(**todo_request.model_dump(), ownerID=user.get("id"))
    todo.description = create_todo_with_gemini(todo.description)
    db.add(todo)
    db.commit()

@router.put("/update_todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user:user_dependency, db: db_dependency, todo_request: TodoRequest, todo_id: int = Path(gt=0)):
    checkUser(user)
    todo = db.query(Todo).filter(Todo.id == todo_id).filter(Todo.ownerID == user.get("id")).first()
    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="To-do not found.")
    todo.title = todo_request.title
    todo.description = todo_request.description
    todo.priority = todo_request.priority
    todo.complete = todo_request.complete
    db.add(todo)
    db.commit()

@router.delete("/delete_todo/{todo_id}", status_code = status.HTTP_204_NO_CONTENT)
async def delete_todo(user:user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    checkUser(user)
    todo = db.query(Todo).filter(Todo.id == todo_id).filter(Todo.ownerID == user.get("id")).first()
    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="To-do not found.")
    db.delete(todo)
    db.commit()

def markdown_to_text(markdown_string):
    html = markdown.markdown(markdown_string)
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text()
    return text

def create_todo_with_gemini(todo_string: str):
    load_dotenv()
    genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
    response = llm.invoke(
        [
            HumanMessage(content="I will provide you a todo item to add my to do list. What i want you to do is create a longer and comprehensive description of that todo item, my next message will be my todo: "),
            HumanMessage(content=todo_string),
        ]
    )
    return markdown_to_text(response.content)