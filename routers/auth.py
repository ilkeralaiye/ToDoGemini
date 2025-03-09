from fastapi import APIRouter, Depends, HTTPException, Request, Response
from jose.constants import ALGORITHMS
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status
from database import SessionLocal
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from typing import Annotated
from models import User
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import timedelta, datetime, timezone
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/auth", tags=["Authentication"])

templates = Jinja2Templates(directory="templates")

bcryptContext = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "acoztm3revp1vfj7ld5sz2ndg5xp79r9fnr2p4hx2dy63h6a8efhj6rm54u8evh8"
ALGORITHM = "HS256"


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
oauth2Bearer = OAuth2PasswordBearer(tokenUrl="/auth/token")

class CreateUserRequest(BaseModel):
    userName:str
    firstName:str
    lastName:str
    email: str
    password: str
    phoneNumber: str

class Token(BaseModel):
    access_token: str
    token_type: str


def createAccessToken(userName: str, userID: int, expiresDelta: timedelta):
    encode = {"sub":userName, "id":userID}
    expires = datetime.now(timezone.utc) + expiresDelta
    encode.update({"exp":expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

def authenticateUser(userName:str, password:str, db):
    user = db.query(User).filter(User.userName == userName).first()
    if not user:
        return False
    if not bcryptContext.verify(password, user.hashedPassword):
        return False
    return user

async def getCurrentUser(token: Annotated[str, Depends(oauth2Bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        userName = payload.get("sub")
        userID = payload.get("id")
        if userName is None or userID is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Username or ID is invalid.")
        return {"username":userName, "id":userID}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Username or ID is invalid.")

@router.get("/login-page")
async def renger_login_page(request:Request):
    return templates.TemplateResponse("login.html", {"request":request})

@router.get("/register-page")
async def renger_login_page(request:Request):
    return templates.TemplateResponse("register.html", {"request":request})


@router.post("/create_user", status_code=status.HTTP_201_CREATED)
async def create_user(db:db_dependency, createUserRequest: CreateUserRequest):
    user = User(userName=createUserRequest.userName,
                email=createUserRequest.email,
                firstName=createUserRequest.firstName,
                lastName=createUserRequest.lastName,
                is_active=True,
                hashedPassword=bcryptContext.hash(createUserRequest.password),
                phoneNumber=createUserRequest.phoneNumber,
                )
    db.add(user)
    db.commit()

@router.post("/token", response_model = Token)
async def loginForAccessToken(formData: Annotated[OAuth2PasswordRequestForm, Depends()], db:db_dependency):
    user = authenticateUser(userName=formData.username, password=formData.password, db=db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    token = createAccessToken(userName=user.userName, userID= user.id, expiresDelta=timedelta(minutes=60))
    return {"access_token": token, "token_type":"bearer"}