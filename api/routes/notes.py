from fastapi import APIRouter, Depends, status, Request, HTTPException
from typing import List

from fastapi.param_functions import Query
from models.Note import * 
from db.models import create_notes_table
from db.session import get_db_url
import databases

router = APIRouter()
    
#prelims
notes = create_notes_table()

"""
This file requires: models/note, sqlAlchemy and sqlAlchemy.Note, database
"""
@router.post("/", response_model=Note, status_code = status.HTTP_201_CREATED)
async def create_note(request: Request, note: NoteIn):
    #define values to insert according to our model
    #none to quiety pylint
    query = notes.insert(None).values(text=note.text, completed=note.completed)
    #execute query and store id
    last_record_id = await request.app.state.db.execute(query)
    #double ** merges two dictionarites in python
    return {**note.dict(), "id": last_record_id}

#update
@router.put("/{note_id}/", response_model=Note, status_code = status.HTTP_200_OK)
async def update_note(request: Request, note_id: int, payload: NoteIn):
    #first we create a query to select note from table
    q = notes.select().where(notes.c.id == note_id)
    #then we select the row from the app.state.db using fetch_one
    row = await request.app.state.db.fetch_one(q)    
    #if row doesnt exist, raise exception
    if not row:
        raise HTTPException(
            status_code=404, 
            detail='note not found'
        )
    #then we store the data into varialbes
    text = payload.text or row['text']
    completed = payload.completed or row['completed']
    #make the query - don't forget to assign the parameter variables accordingly 
    query = notes.update(None).where(notes.c.id == note_id).values(text=text, completed=completed)
    #send it to db
    await request.app.state.db.execute(query)
    return {**payload.dict(), "id": note_id}

#GET - get all
@router.get("/", response_model=List[Note], status_code = status.HTTP_200_OK)
#Here the skip and take arguments will define how may notes to be skipped and how many notes to be returned in the collection respectively. 
# If you have a total of 13 notes in your app.state.db and if you provide skip a value of 10 and take a value of 20, 
# then only 3 notes will be returned. skip will ignore the value based on the identity of the collection starting from old to new.
async def read_notes(request: Request, skip: int = 0, take: int = 20):
    query = notes.select().offset(skip).limit(take)
    return await request.app.state.db.fetch_all(query)

#GET - one based on the id
@router.get("/{note_id}/", response_model=Note, status_code= status.HTTP_200_OK)
async def read_note(request: Request, note_id: int):
    query = notes.select().where(notes.c.id == note_id)
    result = await request.app.state.db.fetch_one(query)
    if not result:
        raise HTTPException(
            status_code=404, 
            detail='note not found'
        )
    return result

#delete
@router.delete("/{note_id}/", status_code=status.HTTP_200_OK)
async def delete_note(request: Request, note_id: int):
    query = notes.delete(None).where(notes.c.id == note_id)
    await request.app.state.db.execute(query)
    return {"message": "note with id: {} deleted successfully".format(note_id)}

@router.delete("/deleteAll")
async def delete_all_notes(request: Request):
    query = notes.delete()
    await request.app.state.db.execute(query)
    return {"message": f"{query}"}
    