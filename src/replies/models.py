from sqlalchemy import Column, Integer, String, CHAR, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from src.databaseBase import Base
from src.utils.modelTimestamp import TimestampMixin_update_create

class RepliesMaster(TimestampMixin_update_create, Base):
    __tablename__ = 'replies_master'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    post_master_id = Column(Integer, ForeignKey('posts_master.id'), nullable=False)
    user_id = Column(CHAR(36), ForeignKey('users.id'), nullable=False)
    parent_reply_master_id = Column(Integer, ForeignKey('replies_master.id'), nullable=True)
    content = Column(Text, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    post_master = relationship("src.posts.models.PostMaster", back_populates="replies", foreign_keys=[post_master_id])
    user = relationship("src.auth.models.User", foreign_keys=[user_id])
    parent_reply = relationship("RepliesMaster", remote_side=[id], foreign_keys=[parent_reply_master_id])
    child_replies = relationship("RepliesMaster", remote_side=[parent_reply_master_id], overlaps="parent_reply")