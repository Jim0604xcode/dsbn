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


# 十句形容自己的話
class DescribeYourselfTenSentences(TimestampMixin_update_create,Base):
    __tablename__ = 'describe_yourself_ten_sentences'
    id = Column(Integer, primary_key=True)
    content = Column(String(1000), nullable=False)
    user_id = Column(CHAR(36), ForeignKey('users.id'), nullable=False)  # 一对多关系
    users = relationship('User',back_populates='describe_yourself_ten_sentences')

# 我的生命價值
class ValueOfLife(TimestampMixin_update_create,Base):
    __tablename__ = 'value_of_life'
    id = Column(Integer, primary_key=True)
    content = Column(String(1000), nullable=False)
    user_id = Column(CHAR(36), ForeignKey('users.id'), nullable=False)  # 一对多关系
    users = relationship('User',back_populates='value_of_life')

# 人生感悟
class LifeInsights(TimestampMixin_update_create,Base):
    __tablename__ = 'life_insights'
    id = Column(Integer, primary_key=True)
    content = Column(String(1000), nullable=False)
    user_id = Column(CHAR(36), ForeignKey('users.id'), nullable=False)  # 一对多关系
    users = relationship('User',back_populates='life_insights')



# 我的墓誌銘
class Epitaph(TimestampMixin_update_create,Base):
    __tablename__ = 'epitaph'
    id = Column(Integer, primary_key=True)
    content = Column(String(1000), nullable=False)
    user_id = Column(CHAR(36), ForeignKey('users.id'), nullable=False)  # 一对多关系
    users = relationship('User',back_populates='epitaph')

# 我最愛的大頭照
class FavoriteHeadshot(TimestampMixin_update_create,Base):
    __tablename__ = 'favorite_headshot'
    id = Column(Integer, primary_key=True)
    picture = Column(Text, nullable=False)
    ago = Column(Integer,nullable=False)
    user_id = Column(CHAR(36), ForeignKey('users.id'), nullable=False)  # 一对多关系
    users = relationship('User',back_populates='favorite_headshot')


