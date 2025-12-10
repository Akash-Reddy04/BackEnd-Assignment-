from fastapi import APIRouter, HTTPException, Header
from bson.objectid import ObjectId
from ..db import client, orgs_col
from ..schemas import CreateOrgRequest, LoginRequest
from ..utils.security import hash_password, verify_password
from ..utils.auth import create_access_token

router = APIRouter(prefix="/org", tags=["Organization"])

def collection_name(name: str):
    return f"org_{name.lower().replace(' ', '_')}"

@router.post("/create")
def create_org(payload: CreateOrgRequest):
    exists = orgs_col.find_one({"organization_name": payload.organization_name})
    if exists:
        raise HTTPException(400, "Organization already exists")

    coll_name = collection_name(payload.organization_name)
    db = client["dynamic_orgs"]
    coll = db[coll_name]

    admin = {"email": payload.email, "password": hash_password(payload.password), "role": "admin"}
    res = coll.insert_one(admin)

    orgs_col.insert_one({
        "organization_name": payload.organization_name,
        "collection_name": coll_name,
        "admin_id": str(res.inserted_id)
    })

    return {"message": "Org created", "collection": coll_name}

@router.get("/get")
def get_org(organization_name: str):
    org = orgs_col.find_one({"organization_name": organization_name}, {"_id":0})
    if not org:
        raise HTTPException(404, "Organization not found")
    return org

@router.post("/admin/login")
def admin_login(payload: LoginRequest):
    db = client["dynamic_orgs"]

    for org in orgs_col.find():
        coll = db[org["collection_name"]]
        admin = coll.find_one({"email": payload.email})
        if admin and verify_password(payload.password, admin["password"]):
            token = create_access_token({
                "admin_id": str(admin["_id"]),
                "org_name": org["organization_name"]
            })
            return {"token": token}

    raise HTTPException(401, "Invalid credentials")

@router.delete("/delete")
def delete_org(name: str):
    org = orgs_col.find_one({"organization_name": name})
    if not org:
        raise HTTPException(404, "Not found")

    db = client["dynamic_orgs"]
    db.drop_collection(org["collection_name"])
    orgs_col.delete_one({"_id": org["_id"]})

    return {"message": "Deleted"}
