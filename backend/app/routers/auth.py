import secrets
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.auth import User, Workspace, UserRole, OrganizationMembership, OrganizationInvitation
from app.schemas.auth import (
    UserCreate, UserLogin, UserResponse, Token,
    PasswordResetRequest, PasswordResetConfirm,
    OrganizationCreate, OrganizationResponse,
    OrganizationMembershipCreate, OrganizationMembershipResponse,
    OrganizationInvitationCreate, OrganizationInvitationResponse
)
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.auth import get_current_user, require_role, require_permission

router = APIRouter(prefix="/auth", tags=["Authentication & Organizations"])

@router.post("/register", response_model=UserResponse)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="User with this email already exists")

    target_org_id = user_in.workspace_id or user_in.organization_id
    workspace = None
    if target_org_id:
        workspace = db.query(Workspace).filter(Workspace.id == target_org_id).first()
    if not workspace:
        workspace = db.query(Workspace).first()
    if not workspace:
        workspace = Workspace(name="Proofline Main Organization", slug="proofline-main")
        db.add(workspace)
        db.flush()

    user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        role=user_in.role or UserRole.CREATOR.value,
        workspace_id=workspace.id,
        organization_id=workspace.id,
        hashed_password=get_password_hash(user_in.password),
        is_active=True
    )
    db.add(user)
    db.flush()

    # Create membership record
    membership = OrganizationMembership(
        organization_id=workspace.id,
        user_id=user.id,
        role=user.role
    )
    db.add(membership)
    db.commit()
    db.refresh(user)
    return user

@router.post("/login", response_model=Token)
def login_user(login_in: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_in.email).first()
    if not user or not verify_password(login_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated")

    token = create_access_token(data={
        "sub": user.id,
        "role": user.role,
        "email": user.email,
        "organization_id": user.workspace_id
    })
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user
    }

@router.post("/logout")
def logout_user(current_user: User = Depends(get_current_user)):
    return {"message": "Logged out successfully", "user_id": current_user.id}

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/me", response_model=UserResponse)
def update_profile(
    full_name: str,
    avatar_url: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    current_user.full_name = full_name
    if avatar_url is not None:
        current_user.avatar_url = avatar_url
    db.commit()
    db.refresh(current_user)
    return current_user

@router.post("/password-reset/request")
def request_password_reset(req: PasswordResetRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user:
        # Avoid user enumeration by returning standard response
        return {"message": "If the email is registered, a password reset link has been generated."}
    
    reset_token = secrets.token_urlsafe(32)
    user.reset_token = reset_token
    user.reset_token_expiry = datetime.utcnow() + timedelta(hours=2)
    db.commit()
    
    # In production, dispatch email. For local dev/verification, return the token safely.
    return {
        "message": "Password reset token generated.",
        "reset_token": reset_token,
        "expires_in_hours": 2
    }

@router.post("/password-reset/confirm")
def confirm_password_reset(confirm: PasswordResetConfirm, db: Session = Depends(get_db)):
    user = db.query(User).filter(
        User.reset_token == confirm.token,
        User.reset_token_expiry > datetime.utcnow()
    ).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    
    user.hashed_password = get_password_hash(confirm.new_password)
    user.reset_token = None
    user.reset_token_expiry = None
    db.commit()
    return {"message": "Password updated successfully. Please log in with your new credentials."}

# Organizations & Multi-Tenant Endpoints
@router.get("/organizations", response_model=list[OrganizationResponse])
def list_organizations(db: Session = Depends(get_db)):
    return db.query(Workspace).all()

@router.post("/organizations", response_model=OrganizationResponse)
def create_organization(
    org_in: OrganizationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    existing = db.query(Workspace).filter(Workspace.slug == org_in.slug).first()
    if existing:
        raise HTTPException(status_code=400, detail="Organization with this slug already exists")
    
    org = Workspace(name=org_in.name, slug=org_in.slug)
    db.add(org)
    db.flush()

    # Add creator as Org Owner
    membership = OrganizationMembership(
        organization_id=org.id,
        user_id=current_user.id,
        role=UserRole.ORG_OWNER.value
    )
    db.add(membership)
    db.commit()
    db.refresh(org)
    return org

@router.get("/organizations/{org_id}/members", response_model=list[OrganizationMembershipResponse])
def list_members(org_id: str, db: Session = Depends(get_db)):
    return db.query(OrganizationMembership).filter(OrganizationMembership.organization_id == org_id).all()

@router.post("/organizations/{org_id}/invitations", response_model=OrganizationInvitationResponse)
def invite_member(
    org_id: str,
    inv_in: OrganizationInvitationCreate,
    current_user: User = Depends(require_permission("org:invite")),
    db: Session = Depends(get_db)
):
    token = secrets.token_urlsafe(32)
    inv = OrganizationInvitation(
        organization_id=org_id,
        email=inv_in.email,
        role=inv_in.role,
        token=token,
        invited_by_id=current_user.id,
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    db.add(inv)
    db.commit()
    db.refresh(inv)
    return inv

@router.post("/switch-demo-role", response_model=Token)
def switch_demo_role(role: str, db: Session = Depends(get_db)):
    """
    Convenience endpoint for local demo & hackathon evaluation to instantly switch
    between Creator, Reviewer, and Brand Owner / Admin roles.
    """
    valid_roles = [r.value for r in UserRole]
    if role not in valid_roles:
        raise HTTPException(status_code=400, detail=f"Invalid role. Choose from {valid_roles}")

    user = db.query(User).filter(User.role == role).first()
    if not user:
        user = User(
            email=f"{role}@proofline.io",
            full_name=f"Proofline {role.replace('_', ' ').title()}",
            role=role,
            hashed_password=get_password_hash("demo1234"),
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    token = create_access_token(data={"sub": user.id, "role": user.role, "email": user.email})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user
    }
