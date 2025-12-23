from sqlalchemy import Column, Integer, String, DATETIME, ForeignKey, DECIMAL, JSON, CHAR, Enum, Text, Boolean,func
from sqlalchemy.orm import relationship
from datetime import datetime
from src.databaseBase import Base
import enum
from zoneinfo import ZoneInfo

from src.utils.modelTimestamp import TimestampMixin_update_create


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


class PushNotification(TimestampMixin_update_create,Base):
    __tablename__ = 'push_notification'
    id = Column(Integer, primary_key=True)
    token = Column(String(100), nullable=True)
    device_uuid = Column(String(100), nullable=False)
    user_id = Column(CHAR(36), ForeignKey('users.id'), nullable=False)  # 一对多关系
    users = relationship('User',back_populates='push_notification')

