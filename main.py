from fastapi import FastAPI, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI()

# Allow frontend to call the backend locally
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock in-memory data store
groups_data = {
    "group_1": {
        "name": "Crypto Investors Club",
        "credits": 32,
        "verifiedToday": 12,
        "unverified": 5,
        "mode": "paid",
    },
    "group_2": {
        "name": "Tech Startups",
        "credits": 0,
        "verifiedToday": 8,
        "unverified": 3,
        "mode": "trial",
    }
}

verified_users_data = {
    "group_1": [
        {"username": "@john_doe", "date": "2025-05-20"},
        {"username": "@sarah_crypto", "date": "2025-05-21"},
    ],
    "group_2": [
        {"username": "@tech_guy", "date": "2025-05-21"},
    ]
}


@app.get("/groups")
def get_groups():
    result = []
    for gid, info in groups_data.items():
        result.append({
            "id": gid,
            "name": info["name"],
            "credits": info["credits"],
            "verifiedToday": info["verifiedToday"],
            "unverified": info["unverified"],
            "mode": info["mode"]
        })
    return result


@app.get("/verified-users")
def get_verified_users(group_id: str = Query(..., description="Group ID")):
    if group_id not in verified_users_data:
        return JSONResponse(status_code=404, content={"detail": "Group not found"})
    return {"group_id": group_id, "users": verified_users_data[group_id]}


@app.post("/issue-credits")
def issue_credits(group_id: str = Body(...), amount: int = Body(...)):
    if group_id not in groups_data:
        return JSONResponse(status_code=404, content={"detail": "Group not found"})
    
    groups_data[group_id]["credits"] += amount
    return {"message": f"Issued {amount} credits to {group_id}", "new_credits": groups_data[group_id]["credits"]}
