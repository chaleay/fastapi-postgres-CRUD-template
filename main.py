from typing import List
import databases
import sqlalchemy
from sqlalchemy import select
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from os.path import join, dirname
from dotenv import load_dotenv
import urllib

#CREATE env file path
dotenv_path = join(dirname(__file__), '.env')

# Load file from the path.
load_dotenv(dotenv_path)


host_server = os.environ.get('HOST_SERVER', 'localhost')
db_server_port = urllib.parse.quote_plus(str(os.environ.get('DB_PORT', '5432')))
database_name = os.environ.get('DB_NAME')
db_username = urllib.parse.quote_plus(str(os.environ.get('DB_USER')))
db_password = urllib.parse.quote_plus(str(os.environ.get('PASSWORD')))
ssl_mode = urllib.parse.quote_plus(str(os.environ.get('SSL_MODE', 'prefer')))
DATABASE_URL = 'postgresql://{}:{}@{}:{}/{}?sslmode={}'.format(db_username, db_password, host_server, db_server_port, database_name, ssl_mode)
print(DATABASE_URL)


database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

#create Notes table for our database
notes = sqlalchemy.Table(
    "Notes-Python",
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column('text', sqlalchemy.String),
    sqlalchemy.Column('completed', sqlalchemy.Boolean)
)

#point engine towards our database instance
engine = sqlalchemy.create_engine(DATABASE_URL, pool_size=3, max_overflow=0)

#create all the tables in our db that we originally defined in our metadata
if not metadata.create_all(engine):
    print('Notes Table already in DB')  
    
    
#used as a payload to create or update note endpoints   
class NoteIn(BaseModel):
    text: str
    completed: bool
    
#the model in its json form that will be used as a reponse to retrieve notes collection or a single note given its id   
class Note(BaseModel):
    id: int
    text: str
    completed: bool
    
#APP    
app = FastAPI(title='REST API using fastapi, posgresSQL')
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], #not recommended for production - recommended to use an array of origins such as 
    # allow_origins=['client-facing-example-app.com', 'localhost:5000']
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

#Python decorators - startup func is passed into app.on_event("startup"), etc
@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
    

#ROUTES
@app.post("/notes/", response_model=Note, status_code = status.HTTP_201_CREATED)
async def create_note(note: NoteIn):
    #define values to insert according to our model
    #none to quiety pylint
    query = notes.insert(None).values(text=note.text, completed=note.completed)
    #execute query and store id
    last_record_id = await database.execute(query)
    #double ** merges two dictionarites in python
    return {**note.dict(), "id": last_record_id}

#update
@app.put("/notes/{note_id}/", response_model=Note, status_code = status.HTTP_200_OK)
async def update_note(note_id: int, payload: NoteIn):
    #first we create a query to select note from table
    q = notes.select().where(notes.c.id == note_id)
    rows = await database.fetch_one(q)
    
 

    #text = payload.text or 
    query = notes.update(None).where(notes.c.id == note_id).values(text=payload.text, completed=payload.completed)
    await database.execute(query)
    return {**payload.dict(), "id": note_id}

#GET - get all
@app.get("/notes/", response_model=List[Note], status_code = status.HTTP_200_OK)
#Here the skip and take arguments will define how may notes to be skipped and how many notes to be returned in the collection respectively. 
# If you have a total of 13 notes in your database and if you provide skip a value of 10 and take a value of 20, 
# then only 3 notes will be returned. skip will ignore the value based on the identity of the collection starting from old to new.
async def read_notes(skip: int = 0, take: int = 20):
    query = notes.select().offset(skip).limit(take)
    return await database.fetch_all(query)

#GET - one based on the id
@app.get("/notes/{note_id}/", response_model=Note, status_code= status.HTTP_200_OK)
async def read_note(note_id: int):
    query = notes.select().where(notes.c.id == note_id)
    return await database.fetch_one(query) 

#delete
@app.delete("/notes/{note_id}/", status_code=status.HTTP_200_OK)
async def delete_note(note_id: int):
    query = notes.delete(None).where(notes.c.id == note_id)
    await database.execute(query)
    return {"message": "note with id: {} deleted successfully".format(note_id)}










