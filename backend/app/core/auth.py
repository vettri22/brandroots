from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Optional, List
from app.database import get_db
from app.models.auth import User, UserRole
from app.core.security import decode_access_token
from app.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

PERMISSION_MATRIX = {
    # Organization & Member Management
    "org:manage": ["org_owner"],
    "org:invite": ["org_owner", "brand_admin", "brand_owner"],
    "org:view": ["org_owner", "brand_admin", "brand_owner", "creator", "reviewer", "read_only"],
    
    # Brand Management
    "brand:create": ["org_owner", "brand_admin", "brand_owner"],
    "brand:edit": ["org_owner", "brand_admin", "brand_owner"],
    "brand:view": ["org_owner", "brand_admin", "brand_owner", "creator", "reviewer", "read_only"],
    
    # Guidelines & Rules
    "guidelines:manage": ["org_owner", "brand_admin", "brand_owner"],
    "guidelines:view": ["org_owner", "brand_admin", "brand_owner", "creator", "reviewer", "read_only"],
    
    # Brand Evidence Ledger
    "evidence:create": ["org_owner", "brand_admin", "brand_owner", "reviewer", "creator"],
    "evidence:approve": ["org_owner", "brand_admin", "brand_owner", "reviewer"],
    "evidence:view": ["org_owner", "brand_admin", "brand_owner", "creator", "reviewer", "read_only"],
    
    # Content & Review
    "content:create": ["org_owner", "brand_admin", "brand_owner", "creator", "reviewer"],
    "content:edit": ["org_owner", "brand_admin", "brand_owner", "creator", "reviewer"],
    "content:review": ["org_owner", "brand_admin", "brand_owner", "reviewer"],
    "content:approve": ["org_owner", "brand_admin", "brand_owner", "reviewer"],
    
    # Guideline Clarity Radar
    "radar:view": ["org_owner", "brand_admin", "brand_owner", "reviewer", "creator", "read_only"],
    "radar:resolve": ["org_owner", "brand_admin", "brand_owner"],
    
    # Audit Trail
    "audit:view": ["org_owner", "brand_admin", "brand_owner", "reviewer", "creator", "read_only"],
}

def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not token:
        if settings.DEMO_MODE:
            # Fall back to default demo user in demo mode
            user = db.query(User).filter(User.role.in_([UserRole.BRAND_OWNER.value, "brand_admin"])).first()
            if user:
                return user
        raise credentials_exception

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
        
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception
        
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated"
        )
    return user

def require_role(allowed_roles: List[str]):
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        user_roles = [current_user.role]
        if current_user.role in ("brand_owner", "brand_admin"):
            user_roles.extend(["brand_owner", "brand_admin"])
            
        if not any(r in allowed_roles for r in user_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation not permitted. Required roles: {allowed_roles}, your role: {current_user.role}"
            )
        return current_user
    return role_checker

def require_permission(permission: str):
    def perm_checker(current_user: User = Depends(get_current_user)) -> User:
        allowed_roles = PERMISSION_MATRIX.get(permission, [])
        user_roles = [current_user.role]
        if current_user.role in ("brand_owner", "brand_admin"):
            user_roles.extend(["brand_owner", "brand_admin"])

        if not any(r in allowed_roles for r in user_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: '{permission}' requires roles {allowed_roles}. Your role: {current_user.role}"
            )
        return current_user
    return perm_checker
