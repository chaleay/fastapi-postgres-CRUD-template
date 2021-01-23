from db.session import get_db_session
import sqlalchemy
from sqlalchemy import engine

engine = get_db_session()

def create_notes_table():
    metadata = sqlalchemy.MetaData()

    #create Notes table for our database
    notes = sqlalchemy.Table(
        "Notes-Python",
        metadata,
        sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
        sqlalchemy.Column('text', sqlalchemy.String),
        sqlalchemy.Column('completed', sqlalchemy.Boolean)
    )


    #create all the tables in our db that we originally defined in our metadata
    if not metadata.create_all(engine):
        print('Notes Table already in DB')
        
    return notes 