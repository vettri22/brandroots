from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    email: str
    full_name: str
    role: str = "creator"

class UserCreate(UserBase):
    password: str
    workspace_id: Optional[str] = None
    organization_id: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class PasswordResetRequest(BaseModel):
    email: str

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str

class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    workspace_id: Optional[str] = None
    organization_id: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool = True
    created_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class TokenData(BaseModel):
    user_id: Optional[str] = None
    role: Optional[str] = None
    organization_id: Optional[str] = None

class OrganizationBase(BaseModel):
    name: str
    slug: str

class OrganizationCreate(OrganizationBase):
    pass

class OrganizationResponse(OrganizationBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

class OrganizationMembershipCreate(BaseModel):
    user_id: str
    role: str = "creator"

class OrganizationMembershipResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    organization_id: str
    user_id: str
    role: str
    created_at: datetime
    user: Optional[UserResponse] = None

class OrganizationInvitationCreate(BaseModel):
    email: str
    role: str = "creator"

class OrganizationInvitationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    organization_id: str
    email: str
    role: str
    token: str
    is_accepted: bool
    expires_at: datetime
    created_at: datetime
