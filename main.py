from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime
import uuid

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for groups
clients_db: Dict[str, Dict] = {}

class GroupData(BaseModel):
    id: str
    name: str
    credits: int
    verifiedToday: int
    unverified: int
    mode: str  # "trial" or "paid"

class UserLog(BaseModel):
    telegram_username: str
    verified: bool
    timestamp: str

@app.get("/groups", response_model=List[GroupData])
def get_groups():
    return list(clients_db.values())

@app.get("/logs/{group_id}", response_model=List[UserLog])
def get_user_logs(group_id: str):
    group = clients_db.get(group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    return group.get("logs", [])

@app.post("/groups")
def add_or_update_group(group: GroupData):
    clients_db[group.id] = group.dict()
    clients_db[group.id]["logs"] = clients_db[group.id].get("logs", [])
    return {"message": "Group added/updated"}

@app.post("/logs/{group_id}")
def add_user_log(group_id: str, log: UserLog):
    if group_id not in clients_db:
        raise HTTPException(status_code=404, detail="Group not found")
    clients_db[group_id].setdefault("logs", []).append(log.dict())
    return {"message": "Log added"}

@app.post("/control/{group_id}/stop")
def stop_bot(group_id: str):
    if group_id in clients_db:
        clients_db[group_id]["bot_active"] = False
        return {"message": f"Bot for group '{group_id}' has been stopped."}
    raise HTTPException(status_code=404, detail="Group not found")

@app.post("/control/{group_id}/add_credits")
def add_credits(group_id: str, credits: int = Query(..., ge=1)):
    if group_id in clients_db:
        clients_db[group_id]["credits"] += credits
        return {"message": f"{credits} credits added to group '{group_id}'"}
    raise HTTPException(status_code=404, detail="Group not found")
