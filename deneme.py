from fastapi import FastAPI, Body, Query, Path, HTTPException
from typing import Optional
from pydantic import BaseModel, Field
from starlette import status

app = FastAPI()

class Course:
    id: int
    title: str
    instructor: str
    rating: int
    publish_date: int

    def __init__(self, id, title, instructor, rating, publish_date):
        self.id = id
        self.title = title
        self.instructor = instructor
        self.rating = rating
        self.publish_date = publish_date

class CourseRequest(BaseModel):
    id: Optional[int] = Field(description="The is id of the course, optional.", default=None)
    title: str = Field(min_length=3)
    instructor: str = Field(min_length=3)
    rating: int = Field(gt=0, lt=6)
    publish_date: int = Field(gt=1900, lt=2100)

    model_config = {
        "json_schema_extra":{
            "example":{
                "title":"My Course",
                "instructor":"Name",
                "rating":5,
                "publish_date":2025,
            }
        }
    }

courses_db = [
    Course(id=1, title="Python", instructor="Atil", rating=5, publish_date=2019),
    Course(id=2, title="Fitness", instructor="Arda", rating=2, publish_date=2002),
    Course(id=3, title="Kubernetes", instructor="Irem", rating=3, publish_date=2005),
    Course(id=4, title="Jenkins", instructor="Arda", rating=4, publish_date=1992),
    Course(id=5, title="C", instructor="Ilker", rating=5, publish_date=2025),
    Course(id=6, title="Dentistiry", instructor="Ceren", rating=5, publish_date=2016),
    Course(id=7, title="Economy", instructor="Kaan", rating=2, publish_date=2022),
    Course(id=8, title="Fitness", instructor="Efe", rating=4, publish_date=2023),
    Course(id=9, title="Game", instructor="Burak", rating=2, publish_date=2024),
    Course(id=10, title="Calculus", instructor="Ceyda", rating=3, publish_date=2019),
]

@app.get(path="/courses", status_code=status.HTTP_200_OK)
async def get_all_courses():
    return courses_db

@app.get(path="/courses/{course_id}", status_code=status.HTTP_200_OK)
async def get_course_by_id(course_id: int = Path(gt=0)):
    for course in courses_db:
        if course.id == course_id:
            return course
    raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail="Course not found.")

@app.get(path="/courses/", status_code=status.HTTP_200_OK)
async def get_course_by_rating(course_rating: int = Query(gt=0, lt=6)):
    courses_to_return = []
    for course in courses_db:
        if course.rating == course_rating:
            courses_to_return.append(course)
    return courses_to_return

@app.get(path="/courses/by_publish_date/", status_code=status.HTTP_200_OK)
async def get_course_by_rating(course_publish_date: int):
    courses_to_return = []
    for course in courses_db:
        if course.publish_date == course_publish_date:
            courses_to_return.append(course)
    return courses_to_return

@app.post(path="/create_course", status_code=status.HTTP_201_CREATED)
async def create_course(course_request: CourseRequest):
    new_course= Course(**course_request.model_dump())
    courses_db.append(find_course_id(new_course))

@app.put("/courses/update_course", status_code=status.HTTP_204_NO_CONTENT)
async def update_course(course_request: CourseRequest):
    course_updated = False
    for i in range(len(courses_db)):
        if courses_db[i].id == course_request.id:
            courses_db[i] = course_request
            course_updated = True
    if not course_updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found.")

@app.delete("/courses/delete_id/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(course_id:int = Path(gt=0)):
    course_deleted = False
    for i in range(len(courses_db)):
        if courses_db[i].id == course_id:
            courses_db.pop(i)
            course_deleted = True
            break
    if not course_deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found.")

def find_course_id(course: Course):
    course.id = len(courses_db)+1
    return course

