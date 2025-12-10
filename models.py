from pydantic import BaseModel

class Organization(BaseModel):
    organization_name: str
    collection_name: str
    admin_id: str
