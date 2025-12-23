# from fastapi import Depends, HTTPException, status
# from sqlalchemy.orm import Session
# from .models import User
# from .schemas import TokenData
# from .utils import verify_token
# from ..database import get_db

# def get_current_user(token: str = Depends(verify_token), db: Session = Depends(get_db)) -> User:
#     user = db.query(User).filter(User.id == token.user_id).first()
#     if user is None:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid authentication credentials",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     return user

# def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
#     if not current_user.is_active:
#         raise HTTPException(status_code=400, detail="Inactive user")
#     return current_user