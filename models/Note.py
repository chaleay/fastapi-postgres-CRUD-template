from pydantic import BaseModel #pylint: disable=no-name-in-module

#used as a payload to create or update note endpoints   
class NoteIn(BaseModel):
    text: str
    completed: bool
    
#the model in its json form that will be used as a reponse to retrieve notes collection or a single note given its id   
class Note(BaseModel):
    id: int
    text: str
    completed: bool