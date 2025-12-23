from sqlalchemy import Column,Enum, String
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import relationship
import uuid
from src.databaseBase import Base
import enum

from src.utils.modelTimestamp import TimestampMixin_create


class RoleEnum(enum.Enum):
    admin = "admin"
    staff = "staff"
    

class Staff(TimestampMixin_create,Base):
    __tablename__ = 'staff'
    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    authgear_id = Column(CHAR(36), unique=True, nullable=False)
    role = Column(Enum(RoleEnum), nullable=False)
    phone_number = Column(String(100),nullable=True)
    pass_away_info_meta = relationship('PassAwayInfoMeta',back_populates='staff') # 一对多关系
    