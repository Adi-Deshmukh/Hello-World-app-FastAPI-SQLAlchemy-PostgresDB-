
## ALL NECESSARY IMPORTS REQUIRED

from fastapi import FastAPI , Request, Depends, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import sqlalchemy
import databases
from pydantic import BaseModel, Field
from typing import List
import jinja2

## Making Tabel and colums using sqlalchemy

DATABASE_URL = "postgresql://postgres:aditya@127.0.0.1:5433/HELLOWORLD" # --> This is the database url
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

users = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key= True),
    sqlalchemy.Column("name", sqlalchemy.String),
    sqlalchemy.Column("title", sqlalchemy.String),
    

)

engine = sqlalchemy.create_engine(
    DATABASE_URL
)

metadata.create_all(engine)


## Models

class UserList(BaseModel):
    id: int
    name: str
    title: str

class UserEntry(BaseModel):
    name: str = Field(..., example= "Enter Your Name")
    title: str = Field(..., example= "Title")

class UserUpdate(BaseModel):
    id: int = Field(..., example = "Enter the id of the user ")
    name: str = Field(..., example = "New Name")
    title: str = Field(..., example = "New Title")

class UserDelete(BaseModel):
    id: int = Field(..., example = "Enter the id of the user you want to delete ")


##   METHODS

app = FastAPI()


template =  Jinja2Templates(directory= "templates")

## Main Hello World Application Page

@app.get("/", response_class= HTMLResponse )
async def main(request: Request):
    return template.TemplateResponse("index.htm" ,{"request":request})


## connecting and disconnecting database


@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


## ALL CRUD OPERATIONS

## REEGISTERING AN USER OR CREATEING AN USER (CREATE : C)


@app.post("/users/", response_model= UserList)
async def register_user(user:UserEntry = Depends()):
    
    
    query = users.insert().values(
      
        name = user.name,
        title = user.title,
      
    )

    await database.execute(query)
    return
    {
        
        "message": "user created succesfully"

    }

## FIND THE USERS (READ : R)

@app.get("/users/", response_model= List[UserList])
async def find_all_users():
    query = users.select()
    return await database.fetch_all(query)



@app.get("/users/{userId}", response_model = UserList)
async def find_user_by_id(userId: int ):
    query = users.select().where(users.c.id == userId)
    return await database.fetch_one(query)


## UPDATE THE DATA OF THE USER (UPDATE : U)


@app.put("/users/", response_model= UserList)
async def update_user(user: UserUpdate = Depends()):
    query = users.update().\
        where(users.c.id == user.id).\
            values(
                name = user.name,
                title = user.title
            )
    await database.execute(query)

    return await find_user_by_id(user.id)


## DELETE THE USER (DELETE: D)

@app.delete("/users/{userId}")
async def delete_user(user: UserDelete = Depends()):
    query = users.delete().where(users.c.id == user.id)
    await database.execute(query)

    return {
        "status"  : True,
        "message" : "user deleted successfully"
    }

