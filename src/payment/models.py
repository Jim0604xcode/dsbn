from sqlalchemy import Column, Integer, String, DATETIME, ForeignKey, DECIMAL, JSON, CHAR, Enum, Text, Boolean,func
from sqlalchemy.orm import relationship
from datetime import datetime
from src.databaseBase import Base
import enum

from zoneinfo import ZoneInfo

from src.utils.modelTimestamp import TimestampMixin_create

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


class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    product_id = Column(String(100), unique=True, nullable=False)
    product_name = Column(String(100), nullable=False)
    price = Column(DECIMAL, nullable=False)
    currency = Column(String(3), nullable=False)
    transaction = relationship('Transaction', back_populates='products', foreign_keys='Transaction.product_id') # 一对多关系
    
    secret_base = relationship('SecretBase',back_populates='products') # 一对多关系
class PaymentServiceProviderEnum(enum.Enum):
    APPLE = "APPLE"
    GOOGLE = "GOOGLE"
class PaymentStatusEnum(enum.Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
class PaymentTypeEnum(enum.Enum):
    CONSUMPTION = "CONSUMPTION"
    SUBSCRIPTION = "SUBSCRIPTION"
    


class Transaction(TimestampMixin_create,Base):
    __tablename__ = 'transaction'
    id = Column(Integer, primary_key=True)
    payment_service_provider = Column(Enum(PaymentServiceProviderEnum), nullable=False)
    payment_status = Column(Enum(PaymentStatusEnum), nullable=False)
    payment_type = Column(Enum(PaymentTypeEnum), nullable=False)
    transaction_id = Column(String(100), nullable=True)
    purchase_date = Column(DATETIME, nullable=True)
    purchase_token = Column(Text, nullable=True)
    
    
    subscription_meta = relationship('SubscriptionMeta',back_populates='transaction',uselist=False) # 一对一关系

    user_id = Column(CHAR(36), ForeignKey('users.id'), nullable=False) # 一对多关系
    users = relationship('User',back_populates='transaction', foreign_keys='Transaction.user_id')
    
    product_id = Column(String(100), ForeignKey('products.product_id'), nullable=False) # 一对多关系
    products = relationship('Product', back_populates='transaction', foreign_keys='Transaction.product_id')

    pass_away_info_relation_transaction_id = relationship('PassAwayInfo', back_populates='transaction_relation_pass_away_info_transaction_id', foreign_keys='PassAwayInfo.transaction_id') # 一对一关系
    
class SubscriptionMeta(Base):
    __tablename__ = 'subscription_meta'
    id = Column(Integer, primary_key=True)
    subscription_expire_date = Column(DATETIME, nullable=False)
    
    meta_id = Column(Integer, ForeignKey('transaction.id'), nullable=False, unique=True)#一对一关系
    transaction = relationship('Transaction',back_populates='subscription_meta')
    

