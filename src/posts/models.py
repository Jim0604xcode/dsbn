from sqlalchemy import Column, Integer, String, DATETIME, ForeignKey, DECIMAL, JSON, CHAR, Enum, Text, func, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from src.databaseBase import Base
import enum
from zoneinfo import ZoneInfo

from src.utils.modelTimestamp import TimestampMixin_create, TimestampMixin_update_create
from src.ai_feedback.constants import AIFeedbackLangEnum

class AIFeedbackStatusEnum(enum.Enum):
    NA = "NA"
    ALLOWED = "ALLOWED"
    COMPLETED = "COMPLETED"
    ERROR_SAFEGUARD = "ERROR_SAFEGUARD"
    ERROR_MASKING = "ERROR_MASKING"
    ERROR_AI_FEEDBACK = "ERROR_AI_FEEDBACK"
    ERROR_OTHER = "ERROR_OTHER"
class PostMaster(TimestampMixin_update_create,Base):
    __tablename__ = 'posts_master'
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    motion_rate = Column(DECIMAL)
    images_name = Column(JSON)
    videos_name = Column(JSON)
    voices_name = Column(JSON)
    start_date = Column(DATETIME, nullable=True)
    end_date = Column(DATETIME, nullable=True)
    ai_feedback_content = Column(Text, nullable=True)
    ai_feedback_status = Column(Enum(AIFeedbackStatusEnum), nullable=True, default=AIFeedbackStatusEnum.NA)
    ai_feedback_count = Column(Integer, nullable=False, default=0)
    ai_feedback_hotline = Column(Boolean, nullable=True, default=False)
    ai_feedback_lang = Column(Enum(AIFeedbackLangEnum), nullable=True)    
    life_moments = relationship("LifeMoment", back_populates="posts_master", uselist=False)
    life_trajectories = relationship("LifeTrajectory", back_populates="posts_master", uselist=False)
    message_to_you = relationship("MessageToYou", back_populates="posts_master")
    replies = relationship("RepliesMaster", back_populates="post_master")

class LifeMoment(TimestampMixin_update_create,Base):
    __tablename__ = 'life_moments'
    id = Column(Integer, primary_key=True, autoincrement=True)
    post_master_id = Column(Integer, ForeignKey('posts_master.id'), nullable=False)
    post_type_code =  Column(String(255), ForeignKey('default_life_moments_post_types.type_code'), nullable=True)
    custom_post_type_id = Column(Integer, ForeignKey('custom_life_moments_post_types.id'), nullable=True)
    user_id = Column(CHAR(36), ForeignKey('users.id'), nullable=False)
    weather = Column(String(255), nullable=True)
    participants = Column(String(255), nullable=True)
    restaurant_name = Column(String(255), nullable=True)
    food_name = Column(String(255), nullable=True)
    academic_work_interest = Column(String(255), nullable=True)
    school_score = Column(String(20), nullable=True)
    age = Column(Integer, nullable=True)  # Age column
    location = Column(String(255), nullable=True)
    post_type = relationship("DefaultLifeMomentsPostType", back_populates="life_moments", uselist=False)
    posts_master = relationship("PostMaster", back_populates="life_moments",foreign_keys=[post_master_id], uselist=False)
    custom_life_moments_post_types = relationship("CustomLifeMomentsPostTypes", back_populates="life_moments",foreign_keys=[custom_post_type_id], uselist=False)

class DefaultLifeMomentsPostType(TimestampMixin_create,Base):
    __tablename__ = 'default_life_moments_post_types'
    id = Column(Integer, primary_key=True)
    type_code = Column(String(255), nullable=False, unique=True)
    zh_hk_type_name = Column(String(255), nullable=False)
    zh_hk_type_description = Column(String(255), nullable=False)
    en_type_name = Column(String(255), nullable=False)
    en_type_description = Column(String(255), nullable=False)
    zh_hans_type_name = Column(String(255), nullable=False)
    zh_hans_type_description = Column(String(255), nullable=False)
    life_moments = relationship("LifeMoment", back_populates="post_type", uselist=False)

class CustomLifeMomentsPostTypes(TimestampMixin_update_create,Base):
    __tablename__ = 'custom_life_moments_post_types'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    type_name = Column(String(255), nullable=False)
    type_description = Column(String(255), nullable=False)
    life_moments = relationship("LifeMoment", back_populates="custom_life_moments_post_types", uselist=False)

class LifeTrajectory(Base):
    __tablename__ = "life_trajectories"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(CHAR(36), ForeignKey("users.id"), nullable=False)
    post_type_code = Column(String(255), ForeignKey("default_life_trajectory_post_types.type_code"), nullable=True)
    post_master_id = Column(Integer, ForeignKey("posts_master.id"), nullable=False)
    custom_post_type_id = Column(Integer, ForeignKey('custom_life_trajectory_post_types.id'), nullable=True)
    age = Column(Integer, nullable=True)  # Age column    
    post_type = relationship("DefaultLifeTrajectoryPostType", back_populates="life_trajectories", uselist=False)
    posts_master = relationship("PostMaster", back_populates="life_trajectories",foreign_keys=[post_master_id], uselist=False)
    custom_life_trajectories_post_types = relationship("CustomLifeTrajectoriesPostTypes", back_populates="life_trajectories",foreign_keys=[custom_post_type_id], uselist=False)

class DefaultLifeTrajectoryPostType(TimestampMixin_create,Base):
    __tablename__ = 'default_life_trajectory_post_types'
    id = Column(Integer, primary_key=True)
    type_code = Column(String(255), nullable=False, unique=True)
    zh_hk_type_name = Column(String(255), nullable=False)
    zh_hk_type_description = Column(String(255), nullable=False)
    en_type_name = Column(String(255), nullable=False)
    en_type_description = Column(String(255), nullable=False)
    zh_hans_type_name = Column(String(255), nullable=False)
    zh_hans_type_description = Column(String(255), nullable=False)
    life_trajectories = relationship("LifeTrajectory", back_populates="post_type", uselist=False)

class CustomLifeTrajectoriesPostTypes(TimestampMixin_update_create,Base):
    __tablename__ = 'custom_life_trajectory_post_types'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    type_name = Column(String(255), nullable=False)
    type_description = Column(String(255), nullable=False)
    life_trajectories = relationship("LifeTrajectory", back_populates="custom_life_trajectories_post_types", uselist=False)
class MessageToYou(TimestampMixin_update_create,Base):
    __tablename__ = "message_to_you"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(CHAR(36), ForeignKey("users.id"), nullable=False)
    post_type_code = Column(String(255), ForeignKey("default_message_to_you_post_types.type_code"), nullable=False)
    when_can_read_the_post = Column(DATETIME, nullable=True)
    post_master_id = Column(Integer, ForeignKey("posts_master.id"), nullable=False)
    post_type = relationship("DefaultMessageToYouPostType", back_populates="message_to_you", uselist=False)
    posts_master = relationship("PostMaster", back_populates="message_to_you",foreign_keys=[post_master_id], uselist=False)

class DefaultMessageToYouPostType(TimestampMixin_create,Base):
    __tablename__ = 'default_message_to_you_post_types'
    id = Column(Integer, primary_key=True)
    type_code = Column(String(255), nullable=False, unique=True)
    zh_hk_type_name = Column(String(255), nullable=False)
    zh_hk_type_description = Column(String(255), nullable=False)
    en_type_name = Column(String(255), nullable=False)
    en_type_description = Column(String(255), nullable=False)
    zh_hans_type_name = Column(String(255), nullable=False)
    zh_hans_type_description = Column(String(255), nullable=False)
    message_to_you = relationship("MessageToYou", back_populates="post_type", uselist=False)

# Post User Permissions
class PostSourceEnum(enum.Enum):
    LIFE_MOMENT = "LIFE_MOMENT"
    MESSAGE_TO_YOU = "MESSAGE_TO_YOU"
    LIFE_TRAJECTORY = "LIFE_TRAJECTORY"

class PostUserPermissions(TimestampMixin_create,Base):
    __tablename__ = 'post_user_permissions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    shared_post_id = Column(Integer, nullable=False)
    shared_by = Column(CHAR(36), ForeignKey("users.id"), nullable=False)
    post_source = Column(Enum(PostSourceEnum), nullable=False)
    recipients = relationship("PostSharedRecipients", back_populates="permission", cascade="all, delete")

class PostSharedRecipients(TimestampMixin_create,Base):
    __tablename__ = 'post_shared_recipients'
    id = Column(Integer, primary_key=True, autoincrement=True)
    permission_id = Column(Integer, ForeignKey("post_user_permissions.id"), nullable=False)
    shared_to = Column(Integer, ForeignKey("posts_permissions_group_members.id"), nullable=False)
    permission = relationship("PostUserPermissions", back_populates="recipients")
    shared_to_group_member = relationship("PostsPermissionsGroupMembers", back_populates="shared_recipient")

class PostPermissionsGroups(TimestampMixin_create,Base):
    __tablename__ = 'post_permissions_groups'
    id = Column(Integer, primary_key=True, autoincrement=True)
    group_name = Column(String(255), nullable=False)
    create_by = Column(CHAR(36), ForeignKey("users.id"), nullable=False)
    members = relationship("PostsPermissionsGroupMembers", back_populates="group")

class PostsPermissionsGroupMembers(TimestampMixin_create,Base):
    __tablename__ = 'posts_permissions_group_members'
    id = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(Integer, ForeignKey("post_permissions_groups.id"), nullable=False)
    user_id = Column(CHAR(36), ForeignKey("users.id"), nullable=True)
    phone_number_prefix = Column(String(20), nullable=False)
    phone_number = Column(String(20), nullable=False)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    group = relationship("PostPermissionsGroups", back_populates="members")
    shared_recipient = relationship("PostSharedRecipients", uselist=False, back_populates="shared_to_group_member")
    
