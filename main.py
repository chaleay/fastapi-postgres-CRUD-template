import databases
from api.routes import notes
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from db.session import get_db_url

db = databases.Database(get_db_url())

def get_app() -> FastAPI:
    """Creates and returns FastAPI app with routes attached"""
    app = FastAPI(title='REST API using fastapi, posgresSQL')


    # settings 
    app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], #not recommended for production - recommended to use an array of origins such as 
    # allow_origins=['client-facing-example-app.com', 'localhost:5000']
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

    # Add base route at localhost:8000
    #app.include_router(be.router)

    # Add additional routes under localhost:8000/api
    app.include_router(get_router(), prefix="/api")
    return app


def get_router() -> APIRouter:
    """Creates router that will contain additional routes under localhost:8000/api"""
    router = APIRouter()

    # Example route
    router.include_router(notes.router, prefix="/notes")
    return router   
    
    

# Starts FastAPI app
app = get_app()   

#Python decorators - startup func is passed into app.on_event("startup"), etc
@app.on_event("startup")
async def startup():
    await db.connect()
    app.state.db = db

@app.on_event("shutdown")
async def shutdown():
    await db.disconnect()
    












