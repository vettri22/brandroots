from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.auth import User, Workspace, UserRole
from app.schemas.auth import UserCreate, UserLogin, UserResponse, Token
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.auth import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="User with this email already exists")

    workspace = db.query(Workspace).first()
    if not workspace:
        workspace = Workspace(name="NovusBio Health Brand Workspace", slug="novusbio-health")
        db.add(workspace)
        db.flush()

    user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        role=user_in.role,
        workspace_id=workspace.id,
        hashed_password=get_password_hash(user_in.password)
    )
    db.add(user)
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
    token = create_access_token(data={"sub": user.id, "role": user.role, "email": user.email})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user
    }

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/switch-demo-role", response_model=Token)
def switch_demo_role(role: str, db: Session = Depends(get_db)):
    """
    Convenience endpoint for local demo & hackathon evaluation to instantly switch
    between Creator, Reviewer, and Brand Owner roles.
    """
    valid_roles = [r.value for r in UserRole]
    if role not in valid_roles:
        raise HTTPException(status_code=400, detail=f"Invalid role. Choose from {valid_roles}")

    user = db.query(User).filter(User.role == role).first()
    if not user:
        # Create on the fly if needed
        user = User(
            email=f"{role}@novusbio.com",
            full_name=f"Demo {role.replace('_', ' ').title()}",
            role=role,
            hashed_password=get_password_hash("demo1234")
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
