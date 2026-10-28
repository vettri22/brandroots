import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Boolean
from sqlalchemy.orm import relationship
import enum
from app.database import Base

class UserRole(str, enum.Enum):
    ORG_OWNER = "org_owner"
    BRAND_ADMIN = "brand_admin"
    BRAND_OWNER = "brand_owner"  # Alias for brand_admin for backward compatibility
    CREATOR = "creator"
    REVIEWER = "reviewer"
    READ_ONLY = "read_only"

class Workspace(Base):
    """
    Maintains compatibility with existing table 'workspaces' while serving as Organization boundary.
    """
    __tablename__ = "workspaces"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    users = relationship("User", back_populates="workspace", cascade="all, delete-orphan")
    brands = relationship("Brand", back_populates="workspace", cascade="all, delete-orphan")
    memberships = relationship("OrganizationMembership", back_populates="organization", cascade="all, delete-orphan")
    invitations = relationship("OrganizationInvitation", back_populates="organization", cascade="all, delete-orphan")

# Synonym for modern multi-tenant nomenclature
Organization = Workspace

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id = Column(String(36), ForeignKey("workspaces.id"), nullable=True)
    organization_id = Column(String(36), nullable=True)  # Mirror for organization schema
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(String(50), default=UserRole.CREATOR.value, nullable=False)
    avatar_url = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    reset_token = Column(String(100), nullable=True)
    reset_token_expiry = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    workspace = relationship("Workspace", back_populates="users")
    memberships = relationship("OrganizationMembership", back_populates="user", cascade="all, delete-orphan")

class OrganizationMembership(Base):
    __tablename__ = "organization_memberships"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(String(36), ForeignKey("workspaces.id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    role = Column(String(50), default=UserRole.CREATOR.value, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Workspace", back_populates="memberships")
    user = relationship("User", back_populates="memberships")

class OrganizationInvitation(Base):
    __tablename__ = "organization_invitations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(String(36), ForeignKey("workspaces.id"), nullable=False)
    email = Column(String(255), nullable=False)
    role = Column(String(50), default=UserRole.CREATOR.value, nullable=False)
    token = Column(String(100), unique=True, nullable=False)
    invited_by_id = Column(String(36), nullable=True)
    is_accepted = Column(Boolean, default=False, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Workspace", back_populates="invitations")
