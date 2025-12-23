from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, DECIMAL, JSON, CHAR, Enum, Text, Boolean,func
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


# 安寧照護
class PCDidArrangeTypeEnum(enum.Enum):
    AGREE = "AGREE"
    NOT_AGREE = "NOT_AGREE"
    NOT_YET = "NOT_YET"
class PalliativeCare(TimestampMixin_update_create,Base):
    __tablename__ = 'palliative_care'
    id = Column(Integer, primary_key=True)
    did_arrange = Column(Enum(PCDidArrangeTypeEnum),nullable=False)
    contact_organization = Column(String(255), nullable=False)
    notes = Column(String(1000), nullable=True)
    user_id = Column(CHAR(36), ForeignKey('users.id'), nullable=False, unique=True)  # 一对一关系
    users = relationship('User',back_populates='palliative_care')

# 預設醫療指示
class MPDidArrangeTypeEnum(enum.Enum):
    DID = "DID"
    NOT_DID = "NOT_DID"
    NOT_YET = "NOT_YET"

class MedicalPreference(TimestampMixin_update_create,Base):
    __tablename__ = 'medical_preference'
    id = Column(Integer, primary_key=True)
    did_arrange = Column(Enum(MPDidArrangeTypeEnum),nullable=False)
    notes = Column(String(1000), nullable=True)
    user_id = Column(CHAR(36), ForeignKey('users.id'), nullable=False, unique=True)  # 一对一关系
    users = relationship('User',back_populates='medical_preference')


# 訂立持久授權書
class EPOADidArrangeTypeEnum(enum.Enum):
    DID = "DID"
    NOT_DID = "NOT_DID"
    NOT_YET = "NOT_YET"

class EnduringPowerOfAttorney(TimestampMixin_update_create,Base):
    __tablename__ = 'enduring_power_of_attorney'
    id = Column(Integer, primary_key=True)
    did_arrange = Column(Enum(EPOADidArrangeTypeEnum),nullable=False)
    notes = Column(String(1000), nullable=True)
    user_id = Column(CHAR(36), ForeignKey('users.id'), nullable=False, unique=True)  # 一对一关系
    users = relationship('User',back_populates='enduring_power_of_attorney')



# 葬禮儀式
class CPDidArrangeTypeEnum(enum.Enum):
    BUDDHISM = "BUDDHISM"
    TAOISM = "TAOISM"
    CHRISTIANITY = "CHRISTIANITY"
    NOT_YET = "NOT_YET"
    CUSTOM = "CUSTOM"

class CeremonyPreference(TimestampMixin_update_create,Base):
    __tablename__ = 'ceremony_preference'
    id = Column(Integer, primary_key=True)
    did_arrange = Column(Enum(CPDidArrangeTypeEnum),nullable=False)
    notes = Column(String(1000), nullable=True)
    custom = Column(String(100), nullable=True)
    user_id = Column(CHAR(36), ForeignKey('users.id'), nullable=False, unique=True)  # 一对一关系
    users = relationship('User',back_populates='ceremony_preference')





# # 棺木
class CDidArrangeTypeEnum(enum.Enum):
    CHINESE = "CHINESE"
    WEST = "WEST"
    EF = "EF"
    NOT_YET = "NOT_YET"
    CUSTOM = "CUSTOM"

class Coffin(TimestampMixin_update_create,Base):
    __tablename__ = 'coffin'
    id = Column(Integer, primary_key=True)
    did_arrange = Column(Enum(CDidArrangeTypeEnum),nullable=False)
    notes = Column(String(1000), nullable=True)
    custom = Column(String(100), nullable=True)
    user_id = Column(CHAR(36), ForeignKey('users.id'), nullable=False, unique=True)  # 一对一关系
    users = relationship('User',back_populates='coffin')





# 殯葬方式
class FDidArrangeTypeEnum(enum.Enum):
    CREMATION = "CREMATION"
    BURIAL = "BURIAL"
    NOT_YET = "NOT_YET"
    CUSTOM = "CUSTOM"

class Funeral(TimestampMixin_update_create,Base):
    __tablename__ = 'funeral'
    id = Column(Integer, primary_key=True)
    did_arrange = Column(Enum(FDidArrangeTypeEnum),nullable=False)
    notes = Column(String(1000), nullable=True)
    custom = Column(String(100), nullable=True)
    user_id = Column(CHAR(36), ForeignKey('users.id'), nullable=False, unique=True)  # 一对一关系
    users = relationship('User',back_populates='funeral')

    




# 骨灰處理
class ADidArrangeTypeEnum(enum.Enum):
    CB = "CB"
    SAITGOR = "SAITGOR"
    SAOTS = "SAOTS"
    CR = "CR"
    NOT_YET = "NOT_YET"
    CUSTOM = "CUSTOM"


class Ashes(TimestampMixin_update_create,Base):
    __tablename__ = 'ashes'
    id = Column(Integer, primary_key=True)
    did_arrange = Column(Enum(ADidArrangeTypeEnum),nullable=False)
    notes = Column(String(1000), nullable=True)
    custom = Column(String(100), nullable=True)
    user_id = Column(CHAR(36), ForeignKey('users.id'), nullable=False, unique=True)  # 一对一关系
    users = relationship('User',back_populates='ashes')
