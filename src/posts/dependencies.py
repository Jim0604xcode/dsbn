# from fastapi import Depends, HTTPException
# from sqlalchemy.orm import Session
# from ..database import get_db
# from .models import Post
# from .exceptions import PostNotFoundError

# def get_post_by_id(post_id: int, db: Session = Depends(get_db)):
#     post = db.query(Post).filter(Post.id == post_id).first()
#     if not post:
#         raise HTTPException(status_code=404, detail="Post not found")
#     return post

# def get_all_posts(db: Session = Depends(get_db)):
#     return db.query(Post).all()