from database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey


class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    complete = Column(Boolean, default=False)
    ownerID = Column(Integer, ForeignKey("users.id"))

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    userName = Column(String, unique=True)
    firstName = Column(String)
    lastName = Column(String)
    hashedPassword = Column(String)
    is_active = Column(Boolean, default=True)
    phoneNumber = Column(String)
