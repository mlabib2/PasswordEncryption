from datetime import datetime, timezone
from random import randint
from fastapi import Depends, FastAPI, HTTPException, Request, Response, status 
from typing import Annotated, Any, Generic, TypeVar
T = TypeVar("T")
from fastapi.concurrency import asynccontextmanager
from pydantic import BaseModel
from sqlmodel import Field, SQLModel, Session, create_engine, select

class Campaign(SQLModel, table = True):
    campaign_ID : int | None = Field(default = None, primary_key = True)
    name : str = Field(index = True)
    due_date : datetime | None = Field(default=None, index = True)
    created_at: datetime = Field(default_factory= lambda: datetime.now(timezone.utc), nullable= True, index = True)

class CampaignCreate(SQLModel):
    name: str 
    due_date : datetime | None = None 

sqlite_file_name = 'database.db'
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args = connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    with Session(engine) as session: 
        if not session.exec(select(Campaign)).first():
            session.add_all([
                Campaign(name = "Summer Launch", due_date=datetime.now()),
                Campaign(name = "Black Friday", due_date=datetime.now())
            ])
            session.commit()
    yield


app = FastAPI(root_path = "/api/v1", lifespan=lifespan)

data: Any = [
    {
        "Campaign_ID": 1,
        "name": "Summer Launch",
        "due_date": datetime.now(),
        "created_at": datetime.now()
    },
    {
        "Campaign_ID": 2,
        "name": "Black Friday",
        "due_date": datetime.now(),
        "created_at": datetime.now()
    }
]

class Response(BaseModel, Generic[T]):
    data: T

@app.get("/campaigns", response_model=Response[list[Campaign]])
async def read_campaign(session: SessionDep):
    data = session.exec(select(Campaign)).all()
    return Response(data=data)  

@app.get("/campaigns/{id}", response_model=Response[Campaign])
async def read_campaign(id: int, session: SessionDep):
    data = session.get(Campaign, id)
    if not data: 
        raise HTTPException(status_code=404)
    return Response(data=data)  # FIXED


@app.post("/campaigns", status_code=201, response_model=Response[Campaign])
async def create_campaign(campaign: CampaignCreate, session: SessionDep):
    db_campaign = Campaign.model_validate(campaign)
    session.add(db_campaign)
    session.commit()
    session.refresh(db_campaign)
    return Response(data=db_campaign)


@app.put("/campaigns/{id}", response_model=Response[Campaign])
async def update_campaign(id: int, campaign: CampaignCreate, session : SessionDep):
    data = session.get(Campaign, id)
    if not data: 
        raise HTTPException(status_code=404)
    data.name = campaign.name
    data.due_date = campaign.due_date
    session.add(data)
    session.commit()
    session.refresh(data)
    return Response(data=data)


@app.delete("/campaigns/{id}", status_code=204)
async def delete_campaign(id: int, session: SessionDep):
    data = session.get(Campaign, id)
    if not data: 
        raise HTTPException(status_code=404)
    session.delete(data)
    session.commit()


# @app.post("/campaigns", status_code=201)
# async def create_campaign(body: dict[str,Any]):

#     new: Any = {
#         "Campaign_ID": randint(100,1000),
#         "name": body.get("name"),
#         "due_date": datetime.now(),
#         "created_at": datetime.now()
#     }

#     data.append(new)
#     return {"campaign": new}


# @app.get("/campaigns")
# async def campaigns():
#     return {"Campaigns": data}

# @app.get("/campaigns/{id}")
# async def read_campaign(id: int):
#     for campaign in data:
#         if campaign.get("Campaign_ID") == id:  
#             return {"Campaign": campaign}       
#     raise HTTPException(status_code=404, detail="Campaign not found")



# @app.put("/campaigns/{id}")
# async def update_campaign(id: int, body: dict[str, Any]):
#     for index, campaign in enumerate(data):
#         print(enumerate(data))
#         if campaign.get("Campaign_ID") == id:  
#             updated = {
#                 "Campaign_ID": id,
#                 "name": body.get("name", campaign.get("name")),
#                 "due_date": body.get("due_date", campaign.get("due_date")),
#                 "created_at": campaign.get("created_at"),
#             } 
#             data[index] = updated
#             return {"Campaign": updated}
        
#     raise HTTPException(status_code=404, detail="Campaign not found")

# @app.delete("/campaigns/{id}", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_campaign(id: int):
#     for index, campaign in enumerate(data):
#         if campaign.get("Campaign_ID") == id:
#             data.pop(index)
#             return Response(status_code=status.HTTP_204_NO_CONTENT)
#     raise HTTPException(status_code=404, detail="Campaign not found")