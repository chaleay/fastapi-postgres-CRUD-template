import os
from dotenv import load_dotenv
import urllib
import urllib.parse
from sqlalchemy.orm import sessionmaker
import sqlalchemy

# Load file from the path.
load_dotenv()

def get_db_session():
    
    #point engine towards our database instance
    engine = sqlalchemy.create_engine(get_db_url(), pool_size=3, max_overflow=0)
    
    #define session
    # SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    # db = SessionLocal()
    return engine

def get_db_url() -> str:
    host_server = os.environ.get('HOST_SERVER', 'localhost')
    db_server_port = urllib.parse.quote_plus(str(os.environ.get('DB_PORT', '5432')))
    database_name = os.environ.get('DB_NAME')
    db_username = urllib.parse.quote_plus(str(os.environ.get('DB_USER')))
    db_password = urllib.parse.quote_plus(str(os.environ.get('PASSWORD')))
    ssl_mode = urllib.parse.quote_plus(str(os.environ.get('SSL_MODE', 'prefer')))
    return 'postgresql://{}:{}@{}:{}/{}?sslmode={}'.format(db_username, db_password, host_server, db_server_port, database_name, ssl_mode)
    
    