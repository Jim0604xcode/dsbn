from sqlalchemy import Column, Integer, String, DATETIME, ForeignKey, DECIMAL, JSON, CHAR, Enum, Text, Boolean,func
from sqlalchemy.orm import relationship
from datetime import datetime
from src.databaseBase import Base
import enum
from zoneinfo import ZoneInfo

from sqlalchemy.sql.sqltypes import DateTime

from src.utils.modelTimestamp import TimestampMixin_update, TimestampMixin_update_create
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


class InviateStatusEnum(enum.Enum):
    WIP = "WIP"
    ACCEPT = "ACCEPT"
    REJECT = "REJECT"
    EXPIRE = "EXPIRE"

class UserInheritor(TimestampMixin_update_create,Base):
    __tablename__ = 'user_inheritor'
    id = Column(Integer, primary_key=True)
    inviate_status = Column(Enum(InviateStatusEnum), nullable=False)
    invitation_expire_date = Column(DATETIME, nullable=False)
    first_name = Column(String(50),nullable=False)
    last_name = Column(String(100),nullable=False)
    # phone_number = Column(String(100), nullable=False)
    jwt = Column(Text,nullable=False)
    
    user_inheritor_meta = relationship('UserInheritorMeta',back_populates='user_inheritor',uselist=False) # 一对一关系
    pass_away_info = relationship('PassAwayInfo',back_populates='user_inheritor',uselist=False) # 一对一关系
    
    # 反向关系
    user_id = Column(CHAR(36), ForeignKey('users.id'), nullable=False, unique=True)  # 一对一关系
    inheritor_user_id = Column(CHAR(36), ForeignKey('users.authgear_id'), nullable=True)  # 一对多关系
    
    inheritor_phone_master_id = Column(Integer, ForeignKey('phone_master.id'), nullable=False, unique=True)#一对一关系
    phone_master = relationship('PhoneMaster',back_populates='user_inheritor')
    
    user_relation_id = relationship('User', back_populates='user_inheritor_relationship_user_id', foreign_keys='UserInheritor.user_id')
    user_relation_authgear_id = relationship('User', back_populates='user_inheritor_relationship_inheritor_user_id', foreign_keys='UserInheritor.inheritor_user_id')
    
    
class UserInheritorMeta(Base):
    __tablename__ = 'user_inheritor_meta'
    id = Column(Integer, primary_key=True)
    LB = Column(Boolean, default=False)
    OP = Column(Boolean, default=False)
    LET = Column(Boolean, default=False)
    SB = Column(Boolean, default=False)
    HM = Column(Boolean, default=False)
    MTS = Column(Boolean, default=False)
    LS = Column(Boolean, default=False)
    FC = Column(Boolean, default=False)
    PE = Column(Boolean, default=False)
    meta_id = Column(Integer, ForeignKey('user_inheritor.id'), nullable=False, unique=True)#一对一关系
    user_inheritor = relationship('UserInheritor',back_populates='user_inheritor_meta')
    



class BeneficiaryTypeEnum(enum.Enum):
    PHONE = "PHONE"
    INSURANCE = "INSURANCE"
    
class UserBeneficiaries(TimestampMixin_update,Base):
    __tablename__ = 'user_beneficiaries'
    id = Column(Integer, primary_key=True)
    beneficiary_type = Column(Enum(BeneficiaryTypeEnum), nullable=False)
    platform_or_company = Column(Text, nullable=False)
    first_name = Column(Text, nullable=False)
    last_name = Column(Text, nullable=False)
    relation = Column(Text, nullable=False)    
    user_beneficiaries_meta = relationship('UserBeneficiariesMeta',back_populates='user_beneficiaries',uselist=False) # 一对一关系
    user_id = Column(CHAR(36), ForeignKey('users.id'), nullable=False) # 一对多关系
    users = relationship('User',back_populates='user_beneficiaries')
    

class UserBeneficiariesMeta(Base):
    __tablename__ = 'user_beneficiaries_meta'
    id = Column(Integer, primary_key=True)
    contact_country_code = Column(String(100), nullable=False)
    contact_number = Column(String(100), nullable=False)
    meta_id = Column(Integer, ForeignKey('user_beneficiaries.id'), nullable=False, unique=True)#一对一关系
    user_beneficiaries = relationship('UserBeneficiaries',back_populates='user_beneficiaries_meta')


class UserTestament(TimestampMixin_update,Base):
    __tablename__ = 'user_testament'
    id = Column(Integer, primary_key=True)
    did_testament = Column(Boolean, default=False)
    did_testament_date = Column(DATETIME, nullable=True)
    testament_store_in = Column(Text, nullable=True)
    comment = Column(Text, nullable=True)
    user_id = Column(CHAR(36), ForeignKey('users.id'), nullable=False, unique=True) # 一对一关系
    users = relationship('User',back_populates='user_testament')

class GoodsDonor(TimestampMixin_update,Base):
    __tablename__ = 'goods_donor'
    id = Column(Integer, primary_key=True)
    image_url_1 = Column(Text, nullable=True)
    image_url_2 = Column(Text, nullable=True)
    image_url_3 = Column(Text, nullable=True)
    goods_info = Column(Text, nullable=False)
    donor_organization = Column(Text, nullable=False)
    user_id = Column(CHAR(36), ForeignKey('users.id'), nullable=False) # 一对多关系
    users = relationship('User',back_populates='goods_donor')

class DidArrangeOrganDonorEnum(enum.Enum):
    YES = "YES"
    NO = "NO"
    NOT_YET = "NOT_YET"

class OrgansDonor(TimestampMixin_update,Base):
    __tablename__ = 'organs_donor'
    id = Column(Integer, primary_key=True)
    did_arrange_organ_donor = Column(Enum(DidArrangeOrganDonorEnum),nullable=False,default="NOT_YET")
    contact_organization = Column(Text, nullable=False)
    comment = Column(Text, nullable=False)    
    user_id = Column(CHAR(36), ForeignKey('users.id'), nullable=False, unique=True) #一对一关系
    users = relationship('User',back_populates='organs_donor')

class LoveLeftInTheWorld(TimestampMixin_update,Base):
    __tablename__ = 'love_left_in_the_world'
    id = Column(Integer, primary_key=True)
    title = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    user_id = Column(CHAR(36), ForeignKey('users.id'), nullable=False) # 一对多关系
    users = relationship('User',back_populates='love_left_in_the_world')

class FamilyOffice(TimestampMixin_update,Base):
    __tablename__ = 'family_office'
    id = Column(Integer, primary_key=True)
    did_family_office = Column(Boolean, default=False)
    did_family_office_date = Column(DATETIME, nullable=True)
    family_office_name = Column(Text, nullable=True)
    registeration_address = Column(Text, nullable=True)
    contact_person = Column(Text, nullable=True)
    mobile = Column(Text, nullable=True)
    comment = Column(Text, nullable=True)
    user_id = Column(CHAR(36), ForeignKey('users.id'), nullable=False, unique=True) # 一对一关系
    users = relationship('User',back_populates='family_office')

class Trust(TimestampMixin_update,Base):
    __tablename__ = 'trust'
    id = Column(Integer, primary_key=True)
    did_trust = Column(Boolean, default=False)
    did_trust_date = Column(DATETIME, nullable=True)
    trust_name = Column(Text, nullable=True)
    contact_person = Column(Text, nullable=True)
    mobile = Column(Text, nullable=True)
    settlor = Column(Text, nullable=True)
    beneficiary = Column(Text, nullable=True)
    comment = Column(Text, nullable=True)
    user_id = Column(CHAR(36), ForeignKey('users.id'), nullable=False, unique=True) # 一对一关系
    users = relationship('User',back_populates='trust')



