from typing import TypedDict
from sqlalchemy import Column, Integer, String, DATETIME, ForeignKey, DECIMAL, JSON, CHAR, Enum, Text, Boolean,func
from sqlalchemy.orm import relationship
from datetime import datetime
from src.databaseBase import Base
import enum
from sqlalchemy.sql.sqltypes import DateTime
from zoneinfo import ZoneInfo

from src.utils.modelTimestamp import TimestampMixin_submit

# 一对多关系
# class Parent(Base):
#     __tablename__ = 'parents'
#     id = Column(Integer, primary_key=True)
#     name = Column(String)
#     children = relationship('Child', back_populates='parent')
# class Child(Base):
#     __tablename__ = 'children'
#     id = Column(Integer, primary_key=True)
#     name = Column(String)
#     parent_id = Column(Integer, ForeignKey('parents.id'))
#     parent = relationship('Parent', back_populates='children')

# 一对一关系
# class Parent(Base):
#     _tablename_ = 'parents'
#     id = Column(Integer, primary_key=True)  # 主键
#     name = Column(String)
#     children = relationship('Child', back_populates='parent',uselist=False)
# class Child(Base):
#     _tablename_ = 'profiles'
#     id = Column(Integer, primary_key=True)  # 主键
#     name = Column(String)
#     parent_id = Column(Integer, ForeignKey('parents.id'), unique=True)  # 外键并保证唯一性
#     parent = relationship('Parent', back_populates='profile')

class PassAwayInfo(TimestampMixin_submit,Base):
    __tablename__ = 'pass_away_info'
    id = Column(Integer, primary_key=True)
    death_time = Column(DATETIME, nullable=False)
    death_certificate = Column(Text, nullable=True)
    id_card_copy = Column(Text, nullable=True)
    relationship_proof = Column(Text, nullable=True)
    inheritor_id_proof = Column(Text, nullable=True)
    
    pass_away_info_meta = relationship('PassAwayInfoMeta',back_populates='pass_away_info',uselist=False) # 一对一关系

    meta_id = Column(Integer, ForeignKey('user_inheritor.id'), nullable=False, unique=True) # 一对一关系
    user_inheritor = relationship('UserInheritor',back_populates='pass_away_info')
    
    
    transaction_id = Column(Integer, ForeignKey('transaction.id'), nullable=False, unique=True) # 一对一关系
    transaction_relation_pass_away_info_transaction_id = relationship('Transaction', back_populates='pass_away_info_relation_transaction_id', foreign_keys='PassAwayInfo.transaction_id')
    
    


class ApprovalStatusEnum(enum.Enum):
    ACTIVE = "ACTIVE"
    DEAD = "DEAD"
    VERIFY = "VERIFY"
    APPROVAL = "APPROVAL"
    REJECT = "REJECT"


class PassAwayInfoMeta(Base):
    __tablename__ = 'pass_away_info_meta'
    id = Column(Integer, primary_key=True)
    approval_status = Column(Enum(ApprovalStatusEnum), nullable=False)
    approval_comments = Column(String(500), nullable=True)
    approved_at = Column(DATETIME, nullable=True)
    
    admin_user_id = Column(CHAR(36), ForeignKey('staff.id'), nullable=True) # 一对一关系
    staff = relationship('Staff',back_populates='pass_away_info_meta', foreign_keys='PassAwayInfoMeta.admin_user_id')

    meta_id = Column(Integer, ForeignKey('pass_away_info.id'), nullable=False, unique=True) # 一对一关系
    pass_away_info = relationship('PassAwayInfo',back_populates='pass_away_info_meta')

    