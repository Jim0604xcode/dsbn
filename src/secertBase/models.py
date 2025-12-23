from sqlalchemy import Column, Integer, String, DATETIME, ForeignKey, DECIMAL, JSON, CHAR, Enum, Text, Boolean,func
from sqlalchemy.orm import relationship
from datetime import datetime
from src.databaseBase import Base
import enum
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





class AssetTypeEnum(enum.Enum):
    BANK_ACCOUNT = "BANK_ACCOUNT"
    PROPERTY = "PROPERTY"
    SAFETY_DEPOSIT_BOX = "SAFETY_DEPOSIT_BOX"
    CONFIDENTIAL_EVENT = "CONFIDENTIAL_EVENT"


class SecretBase(TimestampMixin_update_create,Base):
    __tablename__ = 'secret_base'
    id = Column(Integer, primary_key=True)
    asset_type = Column(Enum(AssetTypeEnum),nullable=False)
    user_id = Column(CHAR(36), ForeignKey('users.id'), nullable=False, unique=True) # 一对一关系
    users = relationship('User',back_populates='secret_base')
    product_id = Column(String(100), ForeignKey('products.product_id'), nullable=False) # 一对多关系
    products = relationship('Product', back_populates='secret_base')

    bank_account = relationship('BankAccount',back_populates='secret_base') # 一对多关系
    property = relationship('Property',back_populates='secret_base') # 一对多关系
    safety_deposit_box = relationship('SafetyDepositBox',back_populates='secret_base') # 一对多关系
    confidential_event = relationship('ConfidentialEvent',back_populates='secret_base') # 一对多关系

class BankAccount(Base):
    __tablename__ = 'bank_account'
    id = Column(Integer, primary_key=True)
    bank_account_name = Column(Text, nullable=False)
    bank_account_number = Column(Text, nullable=False)
    currency = Column(String(3), nullable=False)
    meta_id = Column(Integer, ForeignKey('secret_base.id'), nullable=False)#一对多关系
    secret_base = relationship('SecretBase',back_populates='bank_account')

class Property(Base):
    __tablename__ = 'property'
    id = Column(Integer, primary_key=True)
    property_name = Column(Text, nullable=False)
    property_address = Column(Text, nullable=False)
    remarks = Column(Text, nullable=True)
    meta_id = Column(Integer, ForeignKey('secret_base.id'), nullable=False)#一对多关系
    secret_base = relationship('SecretBase',back_populates='property')

class SafetyDepositBox(Base):
    __tablename__ = 'safety_deposit_box'
    id = Column(Integer, primary_key=True)
    safety_deposit_box_name = Column(Text, nullable=False)
    safety_deposit_box_open_method = Column(Text, nullable=False)
    safety_deposit_box_address = Column(Text, nullable=False)
    remarks = Column(Text, nullable=True)
    meta_id = Column(Integer, ForeignKey('secret_base.id'), nullable=False)#一对多关系
    secret_base = relationship('SecretBase',back_populates='safety_deposit_box')

class ConfidentialEvent(Base):
    __tablename__ = 'confidential_event'
    id = Column(Integer, primary_key=True)
    event_name = Column(Text, nullable=False)
    event_details = Column(Text, nullable=False)
    meta_id = Column(Integer, ForeignKey('secret_base.id'), nullable=False)#一对多关系
    secret_base = relationship('SecretBase',back_populates='confidential_event')
