from pydantic import BaseModel, EmailStr

class CreateOrgRequest(BaseModel):
    organization_name: str
    email: EmailStr
    password: str

class UpdateOrgRequest(BaseModel):
    organization_name: str
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
