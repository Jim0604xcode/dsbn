from sqlalchemy import Column, Integer, func, Boolean, DATETIME, String, ForeignKey, Enum
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import relationship
import uuid
from src.databaseBase import Base
from datetime import datetime
import enum
from zoneinfo import ZoneInfo

from src.utils.modelTimestamp import TimestampMixin_create, TimestampMixin_update_create

class User(TimestampMixin_create,Base):
    __tablename__ = 'users'
    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    authgear_id = Column(CHAR(36), unique=True, nullable=False)
    settings = relationship("UserSettings", back_populates="user", uselist=False)
    life_moments = relationship("src.posts.models.LifeMoment", backref="user")
    user_beneficiaries = relationship('UserBeneficiaries',back_populates='users') # 一对多关系
    user_testament = relationship('UserTestament',back_populates='users',uselist=False) # 一对一关系
    goods_donor = relationship('GoodsDonor',back_populates='users') # 一对多关系
    organs_donor = relationship('OrgansDonor',back_populates='users',uselist=False) # 一对一关系
    love_left_in_the_world = relationship('LoveLeftInTheWorld',back_populates='users') # 一对多关系
    family_office = relationship('FamilyOffice',back_populates='users',uselist=False) # 一对一关系
    trust = relationship('Trust',back_populates='users',uselist=False) # 一对一关系

    transaction = relationship('Transaction',back_populates='users') # 一对多关系
    
    secret_base = relationship('SecretBase',back_populates='users',uselist=False)
    push_notification = relationship('PushNotification',back_populates='users') # 一对多关系
    
    palliative_care = relationship('PalliativeCare',back_populates='users',uselist=False) # 一对一关系
    medical_preference = relationship('MedicalPreference',back_populates='users',uselist=False) # 一对一关系
    enduring_power_of_attorney = relationship('EnduringPowerOfAttorney',back_populates='users',uselist=False) # 一对一关系
    ceremony_preference = relationship('CeremonyPreference',back_populates='users',uselist=False) # 一对一关系
    coffin = relationship('Coffin',back_populates='users',uselist=False) # 一对一关系
    funeral = relationship('Funeral',back_populates='users',uselist=False) # 一对一关系
    ashes = relationship('Ashes',back_populates='users',uselist=False) # 一对一关系
    
    describe_yourself_ten_sentences = relationship('DescribeYourselfTenSentences',back_populates='users') # 一对多关系
    value_of_life = relationship('ValueOfLife',back_populates='users') # 一对多关系
    life_insights = relationship('LifeInsights',back_populates='users') # 一对多关系
    epitaph = relationship('Epitaph',back_populates='users') # 一对多关系
    favorite_headshot = relationship('FavoriteHeadshot',back_populates='users') # 一对多关系

    phone_master = relationship('PhoneMaster',back_populates='users',uselist=False) # 一对一关系
    # 与 UserInheritor 的关系，使用 user_id 外键
    user_inheritor_relationship_user_id = relationship('UserInheritor', back_populates='user_relation_id', foreign_keys='UserInheritor.user_id',uselist=False) # 一对一关系 
    
    # 与 UserInheritor 的关系，使用 inheritor_user_id 外键
    user_inheritor_relationship_inheritor_user_id = relationship('UserInheritor', back_populates='user_relation_authgear_id', foreign_keys='UserInheritor.inheritor_user_id') # 一对多关系


class LanguageEnum(enum.Enum):
    en = "en"
    zh_hans = "zh_hans"
    zh_hk = "zh_hk"
    

class UserSettings(TimestampMixin_update_create,Base):
    __tablename__ = 'user_settings'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(CHAR(36), ForeignKey('users.id'), nullable=False)  
    notification_enabled = Column(Boolean, default=False)
    language = Column(Enum(LanguageEnum), nullable=False,default='en')
    maximum_number_inheritor = Column(Integer,nullable=False,default=5)
    user = relationship("User", back_populates="settings")    

class PhoneMaster(TimestampMixin_update_create,Base):
    __tablename__ = 'phone_master'
    id = Column(Integer, primary_key=True, autoincrement=True)
    phone_number = Column(String(100),nullable=False)

    user_inheritor = relationship('UserInheritor',back_populates='phone_master') # 一对多关系
    # posts_permissions_group_members = relationship('PostsPermissionsGroupMembers',back_populates='phone_master') # 一对多关系
    
    # 反向关系
    user_id = Column(CHAR(36), ForeignKey('users.id'), nullable=True)  # 一对多关系
    users = relationship("User", back_populates="phone_master")

    

class AckTypeEnum(enum.Enum):
    TNC = "TNC"
    PRIVACY = "PRIVACY"
    
