from sqlalchemy.orm import Session
from src.posts.schemas import (CreatePermissionsGroupRequest, LifeMomentsBaseInputRequest,
    LifeTrajectoryBaseInputRequest, MessageToYouBaseInputRequest, SharePostReadPermission)
from src.posts.models import (CustomLifeMomentsPostTypes, CustomLifeTrajectoriesPostTypes,
    LifeMoment, LifeTrajectory, MessageToYou, PostMaster, PostPermissionsGroups,
    PostSharedRecipients, PostSourceEnum, PostsPermissionsGroupMembers, PostUserPermissions)
from src.exceptions import BadReqExpection
from pydantic import BaseModel
from typing import Union, List, Tuple, Dict, Any
from sqlalchemy import or_
from src.replies.models import RepliesMaster


def post_master_db_mapping(post_data: LifeMomentsBaseInputRequest) -> PostMaster:
    return PostMaster(
            title = post_data.title,
            content = post_data.content,
            start_date=post_data.start_date,
            end_date=post_data.end_date,
            motion_rate=post_data.motion_rate,
            videos_name=post_data.videos_name,
            voices_name=post_data.voices_name,
            images_name=post_data.images_name,
        )

def life_moment_db_mapping(life_moment_data: LifeMomentsBaseInputRequest, post_master_id: int, user_id:str) -> LifeMoment:
    return LifeMoment(
        post_master_id=post_master_id,
        user_id=user_id,
        post_type_code=life_moment_data.post_type_code,
        custom_post_type_id=life_moment_data.custom_post_type_id,
        weather=life_moment_data.weather,
        participants=life_moment_data.participants,
        restaurant_name=life_moment_data.restaurant_name,
        food_name=life_moment_data.food_name,
        academic_work_interest=life_moment_data.academic_work_interest,
        school_score=life_moment_data.school_score,
        age=life_moment_data.age,
        location=life_moment_data.location,
    )

def life_trajectory_db_mapping(life_trajectory_data: LifeTrajectoryBaseInputRequest, post_master_id: int, user_id:str) -> LifeTrajectory:
    return LifeTrajectory(
        post_master_id=post_master_id,
        user_id=user_id,
        post_type_code=life_trajectory_data.post_type_code,
        custom_post_type_id=life_trajectory_data.custom_post_type_id,
        age=life_trajectory_data.age,
    )

def message_to_you_db_mapping(message_to_you_data: MessageToYouBaseInputRequest, post_master_id: int, user_id:str) -> MessageToYou:
    return MessageToYou(
        post_master_id=post_master_id,
        user_id=user_id,
        post_type_code=message_to_you_data.post_type_code,
        when_can_read_the_post=message_to_you_data.when_can_read_the_post,
    )

def new_post_permission_db_mapping(share_post_read_permission: SharePostReadPermission, post_id: int, user_id: str, post_type:PostSourceEnum):
    permission = PostUserPermissions(
        shared_post_id=post_id,
        shared_by=user_id,
        post_source=post_type
    )
    permission.recipients = [
        PostSharedRecipients(shared_to=recipient_id)
        for recipient_id in share_post_read_permission.shared_to_group_member_id
    ]
    return permission

def new_permission_group_db_mapping(group_data: CreatePermissionsGroupRequest, user_id: str):
    return PostPermissionsGroups(group_name=group_data.group_name, create_by=user_id)

def get_share_permission_obj(shared_to_group_member_id: str) -> SharePostReadPermission:
    shared_ids = shared_to_group_member_id or []
    return SharePostReadPermission(shared_to_group_member_id=shared_ids)

def check_group_is_exist(group_id: int, user_id: str, db: Session):
    group = db.query(PostPermissionsGroups).filter(PostPermissionsGroups.id == group_id, PostPermissionsGroups.create_by == user_id).first()
    if not group:
        raise BadReqExpection(details="Group not found or you are not the owner")
    return group

def get_group_is_exist_query(group_id: int, user_id: str, db: Session):
    return db.query(PostPermissionsGroups).filter(PostPermissionsGroups.id == group_id, PostPermissionsGroups.create_by == user_id).count() > 0

def get_member_by_id_and_group_id(member_id: str, group_id: int, db: Session):
    member = db.query(PostsPermissionsGroupMembers).filter(PostsPermissionsGroupMembers.user_id == member_id, PostsPermissionsGroupMembers.group_id == group_id).first()
    if not member:
        raise BadReqExpection(details="Member not found")
    return member

def check_life_custom_type_is_exist(model:Union[CustomLifeTrajectoriesPostTypes,CustomLifeMomentsPostTypes] ,custom_type_id: int, user_id: str, db: Session):
    return db.query(model).filter(model.id == custom_type_id, model.id == custom_type_id,model.user_id == user_id).count() > 0

def exclude_post_type_fields(data: BaseModel):
    fields_to_exclude = {"is_life_moment", "is_life_trajectory"}
    return data.model_dump(exclude=fields_to_exclude)

def get_subq_permissions(user_id: str, post_source: PostSourceEnum, db: Session):
    """
    Return a subquery of shared_post_id for a given user and post_source.
    """
    query = (
        db.query(PostUserPermissions.shared_post_id)
        .filter(PostUserPermissions.post_source == post_source)
        .join(PostSharedRecipients, PostUserPermissions.id == PostSharedRecipients.permission_id)
        .join(PostsPermissionsGroupMembers, PostSharedRecipients.shared_to == PostsPermissionsGroupMembers.id)
        .filter(PostsPermissionsGroupMembers.user_id == user_id)
    )
    return query.scalar_subquery()  # 改用 scalar_subquery()，返回相容 IN() 的物件


def build_shared_replies_count_map(
    db: Session,
    post_master_ids: List[int],
    user_id: str,
    post_master_to_owner: Dict[int, Any],
) -> Dict[int, int]:
    """
    Shared replies count statistics logic.
    """
    my_replies_count_map: Dict[int, int] = {}
    if not post_master_ids:
        return my_replies_count_map

    all_replies = (
        db.query(RepliesMaster)
        .filter(
            RepliesMaster.post_master_id.in_(post_master_ids),
            RepliesMaster.is_deleted == False,
        )
        .all()
    )

    for post_master_id in post_master_ids:
        count = 0
        post_owner_id = post_master_to_owner[post_master_id]

        user_reply_ids = [
            r.id
            for r in all_replies
            if r.post_master_id == post_master_id and r.user_id == user_id
        ]

        owner_chain_reply_ids: set[int] = set()

        # Find the replies from the post owner to the user
        for reply in all_replies:
            if (
                reply.post_master_id == post_master_id
                and reply.user_id == post_owner_id
                and reply.parent_reply_master_id in user_reply_ids
            ):
                owner_chain_reply_ids.add(reply.id)

        # Find the replies from the post owner to the user in the same chain
        changed = True
        while changed:
            changed = False
            for reply in all_replies:
                if (
                    reply.post_master_id == post_master_id
                    and reply.user_id == post_owner_id
                    and reply.parent_reply_master_id in owner_chain_reply_ids
                    and reply.id not in owner_chain_reply_ids
                ):
                    owner_chain_reply_ids.add(reply.id)
                    changed = True

        # Count all relevant replies
        for reply in all_replies:
            if reply.post_master_id != post_master_id:
                continue
            if reply.user_id == user_id:
                count += 1
            elif reply.id in owner_chain_reply_ids:
                count += 1

        my_replies_count_map[post_master_id] = count

    return my_replies_count_map