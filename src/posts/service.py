from src.pushNotification.service import send_push_by_create_post

from src.posts.schemas import (AddPermissionsGroupMembersRequest, CreatePermissionsGroupRequest,
    CustomLifePostTypeBase, DefineWhichCustomLifePostType, EditPermissionsGroupMemberRequest,
    EditPermissionsGroupRequest, GetMyCreatedMsgQueryParams,
    LifeMomentAndLifeTrajectoryBaseQueryParams, LifeMomentBase, LifeMomentsBaseInputRequest,
    LifeTrajectoryBase, LifeTrajectoryBaseInputRequest, ManageUserGroupBaseInputRequest, MessageToYouBase,
    MessageToYouBaseInputRequest, PostMasterBase, SharePostReadPermission)
from sqlalchemy.orm import Session
from src.posts.utils import (check_group_is_exist, check_life_custom_type_is_exist,
     exclude_post_type_fields, get_group_is_exist_query, get_member_by_id_and_group_id,
    get_share_permission_obj, life_moment_db_mapping, life_trajectory_db_mapping,
    message_to_you_db_mapping, new_permission_group_db_mapping, new_post_permission_db_mapping,
    post_master_db_mapping, get_subq_permissions, build_shared_replies_count_map)
from src.posts.models import (CustomLifeMomentsPostTypes, CustomLifeTrajectoriesPostTypes,
    DefaultLifeMomentsPostType, DefaultLifeTrajectoryPostType, LifeMoment, LifeTrajectory,
    MessageToYou, PostMaster, PostPermissionsGroups, PostSharedRecipients, PostSourceEnum,
    PostsPermissionsGroupMembers, PostUserPermissions, AIFeedbackStatusEnum)
from datetime import datetime
import math
from src.utils.pagination import build_empty_post_paginated_results, paginate
from src.transaction import (wrap_bulk_insert_orm_trx_func, wrap_delete_func, wrap_delete_trx,
    wrap_insert_mapping_func, wrap_insert_trx, wrap_update_trx,wrap_orm_handler,
    wrap_async_bulk_insert_orm_trx_func)
from src.utils.fileUtil import get_media_urls
from src.loggerServices import log_error, log_info
from src.utils.commonUtil import build_post_result, exclude_fields_from_model
from src.models import OperationsList
from src.exceptions import BadReqExpection, GeneralErrorExcpetion

from zoneinfo import ZoneInfo
from src.replies.models import RepliesMaster

from src.constants import (ORM_OPERATION_TYPE,
    TRANSACTION_CUSTOM_OPERATION_CREATE_MUTLI_RECIPIENTS,
    TRANSACTION_CUSTOM_OPERATION_DELETE_SHARED_TO_MEMBER_IN_GROUP,
    TRANSACTION_CUSTOM_OPERATION_REMOVE_ALL_POST_SHARED_TO)
from sqlalchemy import and_, or_
from src.oss.service import delete_single_file
from src.authgear.adminApi import query_user_by_phone_number, query_user_by_search_keyword
from src.authgear.utils import getAutherIDByNodeID, getUserIDWithBase64encoded
from src.auth.models import User
from sqlalchemy.sql.expression import func as sql_func
from sqlalchemy.sql import desc
from src.auth.service import get_users_info_with_cache

from typing import Union, List,Callable
from src.posts.constants import (DELETED_ACCOUNT_USER, ERROR_DELETE_CUSTOM_POST_TYPE_NOT_ALLOWED,
    ERROR_PERMISSION_USER_NOT_FOUND, ERROR_USER_ALREADY_IN_GROUP, POST_OWNER_IS_REQUESTER)
from src.utils.phonenumbers import split_phone_number

from src.ai_feedback.utils import get_ai_feedback_capability

# TODO: Refactor this function to use a generic ORM function
def create_life_post(req_data: Union[LifeTrajectoryBaseInputRequest, LifeMomentsBaseInputRequest, MessageToYouBaseInputRequest], 
                   user_id: str, post_source: PostSourceEnum, db: Session):
    try:
        share_permission_obj = get_share_permission_obj(req_data.shared_to_group_member_id)
        
        # Create post master
        post_master = wrap_insert_mapping_func(db, post_master_db_mapping(req_data))
        
        # Create specific post type based on post_source
        if post_source == PostSourceEnum.LIFE_MOMENT:
            post = wrap_insert_mapping_func(db, life_moment_db_mapping(req_data, post_master.id, user_id))
        elif post_source == PostSourceEnum.LIFE_TRAJECTORY:
            post = wrap_insert_mapping_func(db, life_trajectory_db_mapping(req_data, post_master.id, user_id))
        elif post_source == PostSourceEnum.MESSAGE_TO_YOU:
            post = wrap_insert_mapping_func(db, message_to_you_db_mapping(req_data, post_master.id, user_id))
        
        # Add ai_feedback_status field to post_master
        can_ai_feedback = get_ai_feedback_capability(post_source, post_master)
        if can_ai_feedback:
            post_master.ai_feedback_status = AIFeedbackStatusEnum.ALLOWED

        # Create permissions if needed
        permission = None
        if len(share_permission_obj.shared_to_group_member_id) > 0:
            permission = wrap_insert_mapping_func(
                db, 
                new_post_permission_db_mapping(share_permission_obj, post.id, user_id, post_source)
            )
        db.commit()
        
        db.refresh(post_master)
        db.refresh(post)
        if permission:
            db.refresh(permission)

        if post_source == PostSourceEnum.LIFE_MOMENT or post_source == PostSourceEnum.LIFE_TRAJECTORY:
            send_push_by_create_post(
                user_id,
                post_master.id,
                post.id,
                share_permission_obj.shared_to_group_member_id,
                db,
                post.post_type_code,
                post_source,
                post_master.title,
                post_master.content,
            )

        return {"post": post, "post_master": post_master, "can_ai_feedback": can_ai_feedback}
        
    except Exception as e:
        db.rollback()
        log_error(f"Error creating {post_source.value} post: {str(e)}")
        raise GeneralErrorExcpetion(str(e))

def create_life_moment(req_data: LifeMomentsBaseInputRequest, user_id: str, db: Session):
    return create_life_post(req_data, user_id, PostSourceEnum.LIFE_MOMENT, db)

def create_lift_trajectory(req_data: LifeTrajectoryBaseInputRequest, user_id: str, db: Session):
    return create_life_post(req_data, user_id, PostSourceEnum.LIFE_TRAJECTORY, db)

def create_message_to_you(req_data: MessageToYouBaseInputRequest, user_id: str, db: Session):
    return create_life_post(req_data, user_id, PostSourceEnum.MESSAGE_TO_YOU, db)    
    
async def query_life_events(model:LifeMoment|LifeTrajectory, query_params: LifeMomentAndLifeTrajectoryBaseQueryParams, user_id: str, db: Session, post_source: PostSourceEnum,with_user_info: bool = False):

    try:

        create_from = query_params.create_from
        create_to = query_params.create_to
        min_motion_rate = query_params.min_motion_rate
        max_motion_rate = query_params.max_motion_rate
        post_type_code = query_params.post_type_code
        custom_post_type_id = query_params.custom_post_type_id
        search_text = query_params.search_text
        
        # 1. Query all posts based on user_id and filter criteria
        query = db.query(model, PostMaster).join(
            PostMaster,
            model.post_master_id == PostMaster.id,
            isouter=False
        )
        
        # Base filters
        query = query.filter(model.user_id == user_id)

        # 2. Apply filter criteria
        if create_from and create_to:
            try:
                start_date_obj = datetime.strptime(create_from, "%d-%m-%Y").replace(hour=0, minute=0, second=0, microsecond=0)
                end_date_obj = datetime.strptime(create_to, "%d-%m-%Y").replace(hour=23, minute=59, second=59, microsecond=999999)
                
                query = query.filter(
                    PostMaster.start_date.between(start_date_obj, end_date_obj)
                )
                
            except ValueError as e:
                raise BadReqExpection(details="Invalid date format. Use DD-MM-YYYY")
        
        if min_motion_rate is not None and max_motion_rate is not None:
            query = query.filter(
                PostMaster.motion_rate.between(min_motion_rate, max_motion_rate)
            )

        # Update post type filtering to use OR condition between post_type_code and custom_post_type_id
        if post_type_code or custom_post_type_id:
            filter_conditions = []
            
            if post_type_code:
                filter_conditions.append(model.post_type_code.in_(post_type_code))
            
            if custom_post_type_id:
                filter_conditions.append(model.custom_post_type_id.in_(custom_post_type_id))
            
            # Apply OR condition between the filters
            query = query.filter(or_(*filter_conditions))
        # Add search functionality if search_text is provided
        if search_text != 'null' and search_text != None and search_text != '':
            # 構建 OR 條件：user_id、title
            search_conditions = []

            search_text = f"%{search_text}%"  # Add wildcards for LIKE query
            search_conditions.extend([
                PostMaster.title.ilike(search_text),
                PostMaster.content.ilike(search_text)
            ])
            # 應用 OR 邏輯
            query = query.filter(or_(*search_conditions))

        # Add ordering
        query = query.order_by(PostMaster.start_date.desc(), model.id.desc())
        
        # Execute query and get results
        paginated_results = paginate(query, query_params.page, query_params.page_size)
        
        # Store post_masters for later use
        post_masters = []
        post_ids = []
        
        for item, post_master in paginated_results["items"]:
            post_ids.append(item.id)
            post_masters.append(post_master)

        # 5. Get shared user info in a single query  
        permissions_map = {}
        if post_ids:  # Check if we have any results
            shared_to_query = db.query(
                PostUserPermissions.shared_post_id,
                PostsPermissionsGroupMembers
            ).join(
                PostSharedRecipients, 
                PostsPermissionsGroupMembers.id == PostSharedRecipients.shared_to
            ).join(
                PostUserPermissions, 
                PostSharedRecipients.permission_id == PostUserPermissions.id
            ).filter(
                PostUserPermissions.shared_post_id.in_(post_ids),
                PostUserPermissions.post_source == post_source
            ).all()

            # Group results by post_id
            for post_id, member in shared_to_query:
                if post_id not in permissions_map:
                    permissions_map[post_id] = []
                permissions_map[post_id].append(member)

        # 7. Get total replies count
        total_replies_map = {}
        if post_masters:
            post_master_ids = [post_master.id for post_master in post_masters]
            
            replies_counts = db.query(
                RepliesMaster.post_master_id,
                sql_func.count(RepliesMaster.id).label('total_replies')
            ).filter(
                RepliesMaster.post_master_id.in_(post_master_ids),
                RepliesMaster.is_deleted == False
            ).group_by(RepliesMaster.post_master_id).all()
            
            total_replies_map = {post_master_id: count for post_master_id, count in replies_counts}

        # 8. Get media URLs
        media_url_map = {}
        for post_id, post_master in zip(post_ids, post_masters):
            media_url_map[post_id] = await get_media_urls(post_master)
    
        # 9. Get user info
        user_info_map = {}
        if with_user_info:
            user_ids = list(set([item[0].user_id for item in paginated_results["items"]]))
            user_objs = db.query(User).filter(User.id.in_(user_ids)).all()
            user_id_to_authgear_id = {str(user.id): user.authgear_id for user in user_objs if user.authgear_id}
            authgear_ids = list(user_id_to_authgear_id.values())
            users_info = await get_users_info_with_cache(authgear_ids)
            
            for item in paginated_results["items"]:
                authgear_id = user_id_to_authgear_id.get(str(item[0].user_id))
                if authgear_id and authgear_id not in users_info:
                    user_info_map[item[0].id] = DELETED_ACCOUNT_USER
                else:
                    user_info_map[item[0].id] = users_info.get(authgear_id) if authgear_id else None        
            
        # 10. Combine all results
        result_list = []
        for item, post_master in paginated_results["items"]:
            download_url = media_url_map.get(item.id, {})
            shared_to_list = permissions_map.get(item.id, [])
            total_replies = total_replies_map.get(post_master.id, 0)
            result = build_post_result(
                item=item,
                post_master=post_master,
                shared_to_list=shared_to_list,
                download_url=download_url,
                user_info=user_info_map.get(item.id, POST_OWNER_IS_REQUESTER)
            )
            result["total_replies"] = total_replies
            result_list.append(result)
        
        paginated_results["items"] = result_list
        
        return paginated_results
    
    except Exception as e:
        log_error(f"Error querying life events: {str(e)}")
        raise GeneralErrorExcpetion(str(e))

async def get_my_life_moments(query_params: LifeMomentAndLifeTrajectoryBaseQueryParams, user_id:str ,db: Session,cb: Callable[[], bool]=None):
    if cb:
        p = await cb
        if not p:
            return build_empty_post_paginated_results()
    return await query_life_events(LifeMoment, query_params, user_id, db, PostSourceEnum.LIFE_MOMENT,with_user_info=True if cb else False)
    
async def get_my_life_trajectories(query_params: LifeMomentAndLifeTrajectoryBaseQueryParams, user_id:str ,db: Session,cb: Callable[[], bool]=None):
    if cb:
        p = await cb
        if not p:
            return build_empty_post_paginated_results()
        
    return await query_life_events(LifeTrajectory, query_params, user_id, db, PostSourceEnum.LIFE_TRAJECTORY,with_user_info=True if cb else False)

async def get_my_messages_by_type_code(getMsgToYouData: GetMyCreatedMsgQueryParams, user_id: str, db: Session,cb: Callable[[], bool]=None):
    if cb:
        p = await cb
        if not p:
            return build_empty_post_paginated_results()
        
    type_code = getMsgToYouData.type_code
    page = getMsgToYouData.page
    page_size = getMsgToYouData.page_size

    messages_query = db.query(MessageToYou, PostMaster).join(
        PostMaster, MessageToYou.post_master_id == PostMaster.id
    ).filter(
        MessageToYou.post_type_code == type_code,
        MessageToYou.user_id == user_id
    )

    messages_query = messages_query.order_by(PostMaster.created_at.desc(), MessageToYou.id.desc())
    paginated_results = paginate(messages_query, page, page_size)

    # Extract message IDs
    message_ids = [message.id for message, _ in paginated_results["items"]]

    # Get ALL permissions in a single query
    permissions_map = {}
    if message_ids:
        shared_to_query = db.query(
            PostUserPermissions.shared_post_id,
            PostsPermissionsGroupMembers
        ).join(
            PostSharedRecipients,
            PostsPermissionsGroupMembers.id == PostSharedRecipients.shared_to
        ).join(
            PostUserPermissions,
            PostSharedRecipients.permission_id == PostUserPermissions.id
        ).filter(
            PostUserPermissions.shared_post_id.in_(message_ids),
            PostUserPermissions.post_source == PostSourceEnum.MESSAGE_TO_YOU
        ).all()
            
        for post_id, member in shared_to_query:
            if post_id not in permissions_map:
                permissions_map[post_id] = []
            permissions_map[post_id].append(member)

    # Get total replies count
    total_replies_map = {}
    if paginated_results["items"]:
        post_master_ids = [post_master.id for _, post_master in paginated_results["items"]]
        
        replies_counts = db.query(
            RepliesMaster.post_master_id,
            sql_func.count(RepliesMaster.id).label('total_replies')
        ).filter(
            RepliesMaster.post_master_id.in_(post_master_ids),
            RepliesMaster.is_deleted == False
        ).group_by(RepliesMaster.post_master_id).all()
        
        total_replies_map = {post_master_id: count for post_master_id, count in replies_counts}

    user_info_map = {}
    # REMARK: cb only happen in query dead user
    if cb:
        user_ids = list(set([item[0].user_id for item in paginated_results["items"]]))
        user_objs = db.query(User).filter(User.id.in_(user_ids)).all()
        user_id_to_authgear_id = {str(user.id): user.authgear_id for user in user_objs if user.authgear_id}
        authgear_ids = list(user_id_to_authgear_id.values())
        users_info = await get_users_info_with_cache(authgear_ids)
        for item in paginated_results["items"]:
            authgear_id = user_id_to_authgear_id.get(str(item[0].user_id))
            if authgear_id and authgear_id not in users_info:
                user_info_map[item[0].id] = DELETED_ACCOUNT_USER
            else:
                user_info_map[item[0].id] = users_info.get(authgear_id) if authgear_id else None    

    result_list = []
    for message, post_master in paginated_results["items"]:
        download_url = await get_media_urls(post_master)
        shared_to_list = permissions_map.get(message.id, [])
        total_replies = total_replies_map.get(post_master.id, 0)
        
        result_list.append({
            "item": message,
            "post_master": exclude_fields_from_model(post_master, ['id']),
            "shared_to_list": shared_to_list,
            "download_url": download_url,
            "user_info": user_info_map.get(message.id, POST_OWNER_IS_REQUESTER),
            "total_replies": total_replies
        })
    paginated_results["items"] = result_list
    return paginated_results


def create_permissions_group(reqData: CreatePermissionsGroupRequest, user_id: str, db: Session):
    result = wrap_insert_trx(db, [new_permission_group_db_mapping(reqData,  user_id)])
    return result[0]["id"]

def edit_permissions_group_name(group_id: int, group_data: EditPermissionsGroupRequest, user_id: str, db: Session):
    return wrap_update_trx(PostPermissionsGroups,{"id":group_id},group_data.model_dump(), db,get_group_is_exist_query(group_id, user_id, db))

async def add_permissions_group_members(group_id: int, members_data: AddPermissionsGroupMembersRequest, user_id: str, db: Session):
    check_group_is_exist(group_id, user_id, db)

    member_user_ids = []
    async def query_func(db: Session):
        new_members = []
        for member in members_data.members:
            # 1. get authgear user id by phone number
            phone_number = f"+{member.phone_number_prefix}{member.phone_number}"
            authgear_result = await query_user_by_phone_number(phone_number)

            member_data = member.model_dump()
            db_user = None
            if authgear_result:
                # 2. get authgear id
                node_id = authgear_result[0]['node']['id']
                authgear_id = getAutherIDByNodeID(node_id)
                # 3. get user id by authgear id
                db_user = db.query(User).filter(User.authgear_id == authgear_id).first()

            if db_user:
                # 4. check if user already in the group
                exist_member = db.query(PostsPermissionsGroupMembers).filter(PostsPermissionsGroupMembers.group_id == group_id, PostsPermissionsGroupMembers.user_id == db_user.id).first()
                if exist_member:
                    raise BadReqExpection(details="User already in group", code=ERROR_USER_ALREADY_IN_GROUP)
                member_data['user_id'] = db_user.id
                member_user_ids.append(db_user.id)
            else:
                member_data['user_id'] = None
                # check if phone number is already in the group
                exist_member = db.query(PostsPermissionsGroupMembers).filter(
                    PostsPermissionsGroupMembers.group_id == group_id,
                    PostsPermissionsGroupMembers.phone_number_prefix == member.phone_number_prefix,
                    PostsPermissionsGroupMembers.phone_number == member.phone_number
                ).first()
                if exist_member:
                    raise BadReqExpection(details="This phone number is already in group", code=ERROR_USER_ALREADY_IN_GROUP)

            new_members.append(
                PostsPermissionsGroupMembers(group_id=group_id, **member_data)
            )
        db.bulk_save_objects(new_members)
        return new_members  # This returns the list of inserted objects.

    result = await wrap_async_bulk_insert_orm_trx_func(db, [query_func])
    return member_user_ids

async def edit_permissions_group_member(group_id:int, group_member_id: int, member_data: EditPermissionsGroupMemberRequest, user_id: str, db: Session):
    phone_number = f"+{member_data.phone_number_prefix}{member_data.phone_number}"
    authgear_result = await query_user_by_phone_number(phone_number)
    db_user = None
    member_user_ids = [] 
    update_data = member_data.model_dump()
    if authgear_result:
        node_id = authgear_result[0]['node']['id']
        authgear_id = getAutherIDByNodeID(node_id)
        db_user = db.query(User).filter(User.authgear_id == authgear_id).first()
    if db_user:
        update_data['user_id'] = db_user.id
        member_user_ids.append(db_user.id)
        # check if the same user_id is already in the group (but not itself)
        exist_member = db.query(PostsPermissionsGroupMembers).filter(
            PostsPermissionsGroupMembers.group_id == group_id,
            PostsPermissionsGroupMembers.user_id == db_user.id,
            PostsPermissionsGroupMembers.id != group_member_id
        ).first()
        if exist_member:
            raise BadReqExpection(details="User already in group", code=ERROR_USER_ALREADY_IN_GROUP)
    else:
        update_data['user_id'] = None
        # check if the same phone number is already in the group (but not itself)
        exist_member = db.query(PostsPermissionsGroupMembers).filter(
            PostsPermissionsGroupMembers.group_id == group_id,
            PostsPermissionsGroupMembers.phone_number_prefix == member_data.phone_number_prefix,
            PostsPermissionsGroupMembers.phone_number == member_data.phone_number,
            PostsPermissionsGroupMembers.id != group_member_id
        ).first()
        if exist_member:
            raise BadReqExpection(details="This phone number is already in group", code=ERROR_USER_ALREADY_IN_GROUP)

    wrap_update_trx(PostsPermissionsGroupMembers,{"id":group_member_id}, update_data, db, get_group_is_exist_query(group_id, user_id, db))

    return member_user_ids

# async def remove_permissions_group_member(group_id: int, member_id: int, user_id: str, db: Session):
#     try:
        
#         check_group_is_exist(group_id, user_id, db)
#         member = get_member_by_id_and_group_id(member_id, group_id, db)
#         operations = [
#             # 1.  delete all post_shared_recipients records that reference this member
#             {
#                 "model": PostSharedRecipients,
#                 "filter": {"shared_to": member.id},
#                 "values": {},
#                 "check_exists": False,
#                 "type": ORM_OPERATION_TYPE.DELETE.value
#             },
#             # 2.  delete member record
#             {
#                 "model": PostsPermissionsGroupMembers,
#                 "filter": {"id": member.id},
#                 "values": {},
#                 "check_exists": True,
#                 "type": ORM_OPERATION_TYPE.DELETE.value
#             }
#         ]
#         return wrap_orm_handler(operations, db)
    
#     except Exception as e:
#         db.rollback()
#         raise GeneralErrorExcpetion(str(e))     
async def remove_permissions_group_member_v2(group_id: int, full_phone_number:str|int, db: Session):
    try:
        area_code, phone_number = split_phone_number(f'+{full_phone_number}')
        phone_number_prefix=area_code[1:]
        
        # log_info(f'------------------->{phone_number_prefix,phone_number}')
        row = db.query(PostsPermissionsGroupMembers).filter(PostsPermissionsGroupMembers.group_id == group_id,PostsPermissionsGroupMembers.phone_number_prefix == phone_number_prefix,PostsPermissionsGroupMembers.phone_number == phone_number).first()
        if row:
            # log_info(f'user require to leave group -----> rowId={row.id}')
            # remove foreign key(shared_to) row of post_shared_recipients -> remove permission group member row
            wrap_delete_func(PostSharedRecipients,{"shared_to": row.id},db,True)
            wrap_delete_func(PostsPermissionsGroupMembers,{"id": row.id},db,True)
    
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        raise GeneralErrorExcpetion(str(e))     
    

def remove_permissions_group(group_id: int, user_id: str, db: Session):
    check_group_is_exist(group_id, user_id, db)
    operations = [
        # 1. Delete all members
        {
            "type": ORM_OPERATION_TYPE.CUSTOM.value,
            "function": TRANSACTION_CUSTOM_OPERATION_DELETE_SHARED_TO_MEMBER_IN_GROUP,
            "params": {"group_id": group_id}
        },
        # 2. Delete the group
        {
            "model": PostPermissionsGroups,
            "filter": {"id": group_id, "create_by": user_id},
            "values": {},
            "check_exists": True,
            "type": ORM_OPERATION_TYPE.DELETE.value
        }
    ]
    return wrap_orm_handler(operations, db)

# async def get_permissions_group_info(group_id: int, user_id: str, db: Session,cb: Callable[[], bool]=None):
#     # REMARK: cb only happen in query dead user
#     if cb:
#         p = await cb
#         if not p:
#             return {}
#     group = check_group_is_exist(group_id, user_id, db)
#     members = db.query(PostsPermissionsGroupMembers).filter(PostsPermissionsGroupMembers.group_id == group_id).all()
#     return {
#         "group": group,
#         "members": members
#     }

async def get_user_permissions_groups(user_id: str, db: Session,cb: Callable[[], bool]=None):
    # REMARK: cb only happen in query dead user
    if cb:
        p = await cb
        if not p:
            return []   
         
    groups = db.query(PostPermissionsGroups).filter(PostPermissionsGroups.create_by == user_id).order_by(PostPermissionsGroups.created_at.desc()).all()
    # Add members for each group in one single query to improve performance
    group_ids = [group.id for group in groups]
    members_map = {}
    
    if group_ids:
        members = db.query(PostsPermissionsGroupMembers).filter(PostsPermissionsGroupMembers.group_id.in_(group_ids)).all()
        for member in members:
            if member.group_id not in members_map:
                members_map[member.group_id] = []
            members_map[member.group_id].append(member)
    
    # Build response with groups and their members
    result = []
    for group in groups:
        result.append({
            "group": group,
            "members": members_map.get(group.id, [])
        })
    
    return result    

def create_custom_life_post_type(reqData: CustomLifePostTypeBase, user_id: str, db: Session):
    excluded_data = exclude_post_type_fields(reqData)

    if reqData.is_life_trajectory:
        insert_obj = CustomLifeTrajectoriesPostTypes(**excluded_data, user_id=user_id)
        model = CustomLifeTrajectoriesPostTypes
    else:
        insert_obj = CustomLifeMomentsPostTypes(**excluded_data, user_id=user_id)
        model = CustomLifeMomentsPostTypes
        
    # Insert the object
    result = wrap_insert_trx(db, [insert_obj])
    
    # Retrieve the complete object by ID
    created_type_id = result[0]["id"]
    created_type = db.query(model).filter(model.id == created_type_id).first()
    
    # Return the complete object
    return created_type

async def get_all_post_types(reqData:DefineWhichCustomLifePostType, user_id: str, db: Session,cb: Callable[[], bool]=None):
    # REMARK: cb only happen in query dead user
    if cb:
        p = await cb
        if not p:
            return []
    return {
        "default_types": get_default_life_post_types(reqData, db),
        "custom_types": await get_custom_life_post_types(reqData, user_id, db)
    }

def get_default_life_post_types(reqData:DefineWhichCustomLifePostType, db: Session):
    model = DefaultLifeTrajectoryPostType if reqData.is_life_trajectory else DefaultLifeMomentsPostType
    return db.query(model).all()

async def get_custom_life_post_types(reqData:DefineWhichCustomLifePostType, user_id: str, db: Session,cb: Callable[[], bool]=None):
    # REMARK: cb only happen in query dead user
    if cb:
        p = await cb
        if not p:
            return []
    model = CustomLifeTrajectoriesPostTypes if reqData.is_life_trajectory else CustomLifeMomentsPostTypes
    return db.query(model).filter(model.user_id == user_id).all()


def update_custom_life_post_type(type_id: int, update_data: CustomLifePostTypeBase, user_id: str, db: Session):
    excluded_data = exclude_post_type_fields(update_data)
    if update_data.is_life_trajectory:
        result = wrap_update_trx(CustomLifeTrajectoriesPostTypes,{"id":type_id}, excluded_data, db,check_life_custom_type_is_exist(CustomLifeTrajectoriesPostTypes,type_id, user_id, db))
    else:
        result = wrap_update_trx(CustomLifeMomentsPostTypes,{"id":type_id}, excluded_data, db,check_life_custom_type_is_exist(CustomLifeMomentsPostTypes,type_id, user_id, db))
    return result 

def delete_custom_life_post_type(reqData:DefineWhichCustomLifePostType, type_id: int, user_id: str, db: Session):
    conditions = {"id": type_id}
    if reqData.is_life_trajectory:
        is_used = db.query(LifeTrajectory).filter(LifeTrajectory.custom_post_type_id == type_id).first() is not None
        model = CustomLifeTrajectoriesPostTypes
    else:
        is_used = db.query(LifeMoment).filter(LifeMoment.custom_post_type_id == type_id).first() is not None
        model = CustomLifeMomentsPostTypes
    
    if is_used:
        raise BadReqExpection(details="Cannot delete this post type as it is being used by existing posts", code=ERROR_DELETE_CUSTOM_POST_TYPE_NOT_ALLOWED)
    
    check_life_custom_type_is_exist(model, type_id, user_id, db)
    
    result = wrap_delete_trx(model, conditions, db)
    return result

def delete_post_files(post_master: PostMaster) -> None:
    """
    Delete all media files (images, videos, voices) associated with a post master.
    
    Args:
        post_master (PostMaster): The post master object containing file references
        
    Returns:
        None
        
    Description:
        This function handles the deletion of all media files associated with a post.
        It processes images, videos, and voice files stored in the post_master object.
    """
    # log_info(f"Deleting post files: {post_master}")
    try:
        # Collect all file paths
        existing_files = []
        if post_master.images_name:
            existing_files.extend(post_master.images_name)
        if post_master.videos_name:
            existing_files.extend(post_master.videos_name)
        if post_master.voices_name:
            existing_files.extend(post_master.voices_name)
            
        # Delete each file if it exists
        for file_path in existing_files:
            if file_path:  # Only delete if path exists
                delete_single_file(file_path)
                
    except Exception as e:
        log_error(f"Error deleting post files: {str(e)}")
        raise BadReqExpection(details=f"Failed to delete media files: {str(e)}")

def edit_life_post(model_id: int, update_data: Union[LifeTrajectoryBaseInputRequest, LifeMomentsBaseInputRequest,MessageToYouBaseInputRequest], db: Session,user_id:str, post_source: PostSourceEnum):
    

    if post_source == PostSourceEnum.LIFE_MOMENT:
        model = LifeMoment
        model_object =  LifeMomentBase(**update_data.model_dump())
        
    elif post_source == PostSourceEnum.LIFE_TRAJECTORY:
        model = LifeTrajectory
        model_object =  LifeTrajectoryBase(**update_data.model_dump())

    elif post_source == PostSourceEnum.MESSAGE_TO_YOU:
        model = MessageToYou
        model_object =  MessageToYouBase(**update_data.model_dump())        

    post_master_id_result = db.query(model.post_master_id).filter(model.id == model_id, model.user_id == user_id).first()
    
    if not post_master_id_result:
        raise BadReqExpection(details=f"{model.__tablename__}  not found or you don't have permission to edit it")
    post_master_id = post_master_id_result[0]
    post_master_old = db.query(PostMaster).filter(PostMaster.id == post_master_id).first()

    post_master_obj = PostMasterBase(**update_data.model_dump())
    
    # Preserve ai_feedback_count from existing post_master
    post_master_obj.ai_feedback_count = post_master_old.ai_feedback_count or 0
    
    # Check if content has changed and clear AI feedback if needed
    content_changed = post_master_old.content != update_data.content
    if content_changed:
        post_master_obj.ai_feedback_content = None
    
    # print("******* content_changed:", content_changed)

    # Recalculate AI feedback capability and update status
    can_ai_feedback = get_ai_feedback_capability(post_source, post_master_obj)
    if can_ai_feedback:
        if content_changed or post_master_old.ai_feedback_status == AIFeedbackStatusEnum.NA or post_master_old.ai_feedback_status is None:
            post_master_obj.ai_feedback_status = AIFeedbackStatusEnum.ALLOWED
        # Keep existing status if content hasn't changed
        else:
            if not content_changed:        
                post_master_obj.ai_feedback_status = post_master_old.ai_feedback_status
                post_master_obj.ai_feedback_content = post_master_old.ai_feedback_content
                post_master_obj.ai_feedback_lang = post_master_old.ai_feedback_lang
                post_master_obj.ai_feedback_hotline = post_master_old.ai_feedback_hotline
    else:
        post_master_obj.ai_feedback_status = AIFeedbackStatusEnum.NA

    # print("******** can_ai_feedback:", can_ai_feedback)

    operations:OperationsList = [
        {
            "model": model,
            "filter": {"id": model_id},
            "values": model_object,
            "check_exists": True,
            "type": ORM_OPERATION_TYPE.UPDATE.value
        },
        {
            "model": PostMaster,
            "filter": {"id": post_master_id},
            "values": post_master_obj,
            "check_exists": True,
            "type": ORM_OPERATION_TYPE.UPDATE.value
        },
        {
            "type": ORM_OPERATION_TYPE.CUSTOM.value,
            "function": TRANSACTION_CUSTOM_OPERATION_REMOVE_ALL_POST_SHARED_TO,
            "params": {
                "shared_post_id": model_id, 
                "post_source": post_source
            }
        }
    ]
    share_permission_obj = get_share_permission_obj(update_data.shared_to_group_member_id)
    if len(share_permission_obj.shared_to_group_member_id) > 0:
        operations.append({
            "type": ORM_OPERATION_TYPE.CUSTOM.value,
            "function": TRANSACTION_CUSTOM_OPERATION_CREATE_MUTLI_RECIPIENTS,
            "params": {
                "share_permission_obj": share_permission_obj,
                "shared_post_id": model_id,
                "user_id": user_id,
                "post_source": post_source
            }
        })

    # Delete old post master files from OSS
    delete_post_files(post_master_old)
    result = wrap_orm_handler(operations, db)
    
    # Return result with AI feedback capability
    return {"result": result, "can_ai_feedback": can_ai_feedback}

def edit_life_moment(life_moment_id: int, update_data: LifeMomentsBaseInputRequest, db: Session,user_id:str):
    return edit_life_post(life_moment_id, update_data, db, user_id, PostSourceEnum.LIFE_MOMENT)

def edit_life_trajectory(life_trajectory_id: int, update_data: LifeTrajectoryBaseInputRequest, db: Session,user_id:str):
    return edit_life_post(life_trajectory_id, update_data, db, user_id, PostSourceEnum.LIFE_TRAJECTORY)

def edit_message_to_you(message_to_you_id: int, update_data: MessageToYouBaseInputRequest, db: Session,user_id:str):
    return edit_life_post(message_to_you_id, update_data, db, user_id, PostSourceEnum.MESSAGE_TO_YOU)


def delete_life_post(model_id: int, db: Session, user_id: str, post_source: PostSourceEnum):
    """
    Generic function to delete any type of life post (LifeMoment, LifeTrajectory, MessageToYou)
    """
    # Determine model type based on post_source
    if post_source == PostSourceEnum.LIFE_MOMENT:
        model = LifeMoment
    elif post_source == PostSourceEnum.LIFE_TRAJECTORY:
        model = LifeTrajectory
    elif post_source == PostSourceEnum.MESSAGE_TO_YOU:
        model = MessageToYou
    else:
        raise BadReqExpection(details="Invalid post source")
        
    # Check post exists and belongs to user
    post = db.query(model).filter(model.id == model_id, model.user_id == user_id).first()
    if not post:
        raise BadReqExpection(details=f"{model.__tablename__} not found or you don't have permission to delete it")
    
    post_master_id = post.post_master_id
    post_master = db.query(PostMaster).filter(PostMaster.id == post_master_id).first()

    # Create operations for deletion
    operations:OperationsList = [
        # 1. Remove all permissions and recipients
        {
            "type": ORM_OPERATION_TYPE.CUSTOM.value,
            "function": TRANSACTION_CUSTOM_OPERATION_REMOVE_ALL_POST_SHARED_TO,
            "params": {
                "shared_post_id": model_id, 
                "post_source": post_source
            }
        },
        # 2. Delete the specific post
        {
            "model": model,
            "filter": {"id": model_id, "user_id": user_id},
            "values": {},
            "check_exists": True,
            "type": ORM_OPERATION_TYPE.DELETE.value
        },
        # 3. Delete the post master
        {
            "model": PostMaster,
            "filter": {"id": post_master_id},
            "values": {},
            "check_exists": True,
            "type": ORM_OPERATION_TYPE.DELETE.value
        }
    ]
    delete_post_files(post_master)
    # Execute all operations in a single transaction
    return wrap_orm_handler(operations, db)

def delete_life_moment(life_moment_id: int, user_id: str, db: Session):
    """Delete a life moment post along with its associated data"""
    return delete_life_post(life_moment_id, db, user_id, PostSourceEnum.LIFE_MOMENT)

def delete_life_trajectory(trajectory_id: int, user_id: str, db: Session):
    """Delete a life trajectory post along with its associated data"""
    return delete_life_post(trajectory_id, db, user_id, PostSourceEnum.LIFE_TRAJECTORY)

def delete_message_to_you(message_id: int, user_id: str, db: Session):
    """Delete a message to you post along with its associated data"""
    return delete_life_post(message_id, db, user_id, PostSourceEnum.MESSAGE_TO_YOU)



async def get_random_my_life_moments( user_id: str,  db: Session):
    # print(f"get_random_my_life_moments called for user_id: {user_id}")

    items = (db.query(
        LifeMoment,
        PostMaster
    ).join(
        PostMaster,
        LifeMoment.post_master_id == PostMaster.id
    ).filter(
        PostMaster.motion_rate > 0,
        LifeMoment.user_id == user_id
    ).order_by(sql_func.random()).limit(3).all())
    
    # print(f"Found {len(items)} items")
    
    post_ids_in_page = [item[0].id for item in items]
    post_master_ids = [item[1].id for item in items]
    # print(f"post_master_ids: {post_master_ids}")

    permissions_map = {}
    if post_ids_in_page:
        shared_to_query = db.query(
            PostUserPermissions.shared_post_id,
            PostsPermissionsGroupMembers
        ).join(
            PostSharedRecipients,
            PostsPermissionsGroupMembers.id == PostSharedRecipients.shared_to
        ).join(
            PostUserPermissions,
            PostSharedRecipients.permission_id == PostUserPermissions.id
        ).filter(
            PostUserPermissions.shared_post_id.in_(post_ids_in_page),
            PostUserPermissions.post_source == PostSourceEnum.LIFE_MOMENT
        ).all()
        
        for post_id, member in shared_to_query:
            if post_id not in permissions_map:
                permissions_map[post_id] = []
            permissions_map[post_id].append(member)
    
    # Get reply counts for all posts
    replies_count_map = {}
    if post_master_ids:
        # print("Querying replies for post_master_ids")
        replies_counts = db.query(
            RepliesMaster.post_master_id,
            sql_func.count(RepliesMaster.id).label('total_replies')
        ).filter(
            RepliesMaster.post_master_id.in_(post_master_ids),
            RepliesMaster.is_deleted == False
        ).group_by(RepliesMaster.post_master_id).all()
        
        # print(f"Raw replies_counts: {replies_counts}")
        replies_count_map = {post_master_id: count for post_master_id, count in replies_counts}
    
    result_list = []
    for life_moment, post_master in items:
        download_url = await get_media_urls(post_master)
        shared_to_list = permissions_map.get(life_moment.id, [])
        total_replies = replies_count_map.get(post_master.id, 0)
        result_list.append({
            "item": life_moment,
            "post_master": exclude_fields_from_model(post_master, ['id']),
            "shared_to_list": shared_to_list,
            "download_url": download_url,
            "user_info": POST_OWNER_IS_REQUESTER,
            "total_replies": total_replies
        })
    
    return result_list


async def get_msg_to_me(user_id: str, db: Session):
    return await query_shared_posts(
        model=MessageToYou,
        post_source=PostSourceEnum.MESSAGE_TO_YOU,
        user_id=user_id,
        db=db,
        random=False,
        limit=3,
        with_user_info=True)

async def get_shared_life_moments(user_id: str, db: Session):
    return await query_shared_posts(
        model=LifeMoment,
        post_source=PostSourceEnum.LIFE_MOMENT,
        user_id=user_id,
        db=db,
        random=False,
        limit=3,
        with_user_info=True)

async def get_shared_life_experiences(user_id: str, db: Session):
    """
    Get shared life moments and life trajectories, each最多 3 筆，
    sorted by post_master.created_at from new to old and return a single list.
    """
    # 1) Get shared life moments (max 3)
    shared_life_moments = await query_shared_posts(
        model=LifeMoment,
        post_source=PostSourceEnum.LIFE_MOMENT,
        user_id=user_id,
        db=db,
        random=False,
        limit=3,
        with_user_info=True,
    )

    for item in shared_life_moments:
        item["is_life_moment"] = True
        item["is_life_trajectory"] = False

    shared_life_trajectories = await query_shared_posts(
        model=LifeTrajectory,
        post_source=PostSourceEnum.LIFE_TRAJECTORY,
        user_id=user_id,
        db=db,
        random=False,
        limit=3,
        with_user_info=True,
    )
    for item in shared_life_trajectories:
        item["is_life_moment"] = False
        item["is_life_trajectory"] = True

    combined = shared_life_moments + shared_life_trajectories
    combined.sort(
        key=lambda r: r.get("post_master", {}).get("created_at"),
        reverse=True,
    )
    return combined[:3]


async def get_shared_life_experiences_paginated(
    user_id: str,
    page: int,
    page_size: int,
    db: Session,
    search_text: str | None = None,
    cb: Callable[[], bool] | None = None,
):
    """
    Get a single SQL paginated result that contains both LIFE_MOMENT and LIFE_TRAJECTORY,
    sorted by PostMaster.created_at desc, reduce Python merge burden.
    """
    # REMARK: cb only happen in query dead user
    if cb:
        p = await cb
        if not p:
            return build_empty_post_paginated_results(page=page, page_size=page_size)

    # 1) Permission subquery: get the IDs of LifeMoment / LifeTrajectory that can be read
    subq_moment = get_subq_permissions(user_id, PostSourceEnum.LIFE_MOMENT, db)
    subq_trajectory = get_subq_permissions(user_id, PostSourceEnum.LIFE_TRAJECTORY, db)

    # 2) Start from PostMaster, LEFT JOIN two types, return all at once
    base_query = db.query(
        PostMaster,
        LifeMoment,
        LifeTrajectory,
    ).outerjoin(
        LifeMoment, LifeMoment.post_master_id == PostMaster.id
    ).outerjoin(
        LifeTrajectory, LifeTrajectory.post_master_id == PostMaster.id
    ).filter(
        or_(
            and_(
                LifeMoment.id.isnot(None),
                LifeMoment.user_id != user_id,
                LifeMoment.id.in_(subq_moment),
            ),
            and_(
                LifeTrajectory.id.isnot(None),
                LifeTrajectory.user_id != user_id,
                LifeTrajectory.id.in_(subq_trajectory),
            ),
        )
    )

    # 3) search_text: reuse the common search logic, search for user/title/content in life posts
    if search_text != "null" and search_text is not None and search_text != "":
        search_user_ids, like_text = await build_search_user_ids_and_like_text(
            search_text, db
        )
        search_conditions = []
        if search_user_ids:
            # Apply to the user_id of two life posts
            search_conditions.append(
                or_(
                    LifeMoment.user_id.in_(search_user_ids),
                    LifeTrajectory.user_id.in_(search_user_ids),
                )
            )

        search_conditions.extend(
            [
                PostMaster.title.ilike(like_text),
                PostMaster.content.ilike(like_text),
            ]
        )
        base_query = base_query.filter(or_(*search_conditions))

    # 4) Sort and paginate (directly use paginate, limit the number in SQL层面)
    base_query = base_query.order_by(PostMaster.created_at.desc(), PostMaster.id.desc())
    paginated_results = paginate(base_query, page, page_size)
    items = paginated_results["items"]

    # 5) Get media URL
    media_url_map: dict[int, dict] = {}
    post_master_ids: List[int] = []
    post_owner_map: dict[int, int] = {}  # post_master_id -> owner_user_id
    item_id_list: List[int] = []  # LifeMoment/LifeTrajectory 的 id
    for post_master, life_moment, life_trajectory in items:
        # Determine which type this record is
        item_obj = life_moment if life_moment is not None else life_trajectory
        if item_obj is None:
            # Theoretically should not happen, insurance check
            continue

        item_id_list.append(item_obj.id)
        post_master_ids.append(post_master.id)
        post_owner_map[post_master.id] = item_obj.user_id
        media_url_map[post_master.id] = await get_media_urls(post_master)

    # 6) shared_replies_count calculation logic (common helper)
    my_replies_count_map: dict[int, int] = build_shared_replies_count_map(
        db, post_master_ids, user_id, post_owner_map
    )

    # 7) Get user info (common helper)
    item_id_user_pairs: List[tuple[int, int]] = []
    for _, life_moment, life_trajectory in items:
        item_obj = life_moment if life_moment is not None else life_trajectory
        if item_obj is not None:
            item_id_user_pairs.append((item_obj.post_master_id, item_obj.user_id))

    user_info_map: dict[int, object] = await build_user_info_map(
        db, item_id_user_pairs
    )

    # 8) Assemble the result, add is_life_moment / is_life_trajectory flags
    result_list = []
    for post_master, life_moment, life_trajectory in items:
        item_obj = life_moment if life_moment is not None else life_trajectory
        if item_obj is None:
            continue

        download_url = media_url_map.get(post_master.id, {})
        shared_replies_count = my_replies_count_map.get(post_master.id, 0)

        result = build_post_result(
            item=item_obj,
            post_master=post_master,
            shared_to_list=None,
            download_url=download_url,
            user_info=user_info_map.get(item_obj.post_master_id, POST_OWNER_IS_REQUESTER),
            exclude_ai_feedback=True,
        )
        result["shared_replies_count"] = shared_replies_count
        result["is_life_moment"] = life_moment is not None
        result["is_life_trajectory"] = life_trajectory is not None
        result_list.append(result)

    paginated_results["items"] = result_list
    return paginated_results


async def get_shared_life_moments_paginated(user_id: str, page: int, page_size: int, db: Session,search_text:str=None,cb: Callable[[], bool]=None):
    # REMARK: cb only happen in query dead user
    if cb:
        p = await cb
        if not p:
            return build_empty_post_paginated_results()
        
    return await query_shared_posts(
            model=LifeMoment,
            post_source=PostSourceEnum.LIFE_MOMENT,
            user_id=user_id,
            db=db,
            search_text=search_text,
            paginated=True,
            page=page,
            page_size=page_size,
            with_user_info=True,
        )        
        

async def get_shared_message_to_me_paginated(user_id: str, page: int, page_size: int, db: Session,cb: Callable[[], bool]=None):
    # REMARK: cb only happen in query dead user
    if cb:
        p = await cb
        if not p:
            return build_empty_post_paginated_results()
        
    return await query_shared_posts(
                model=MessageToYou,
                post_source=PostSourceEnum.MESSAGE_TO_YOU,
                user_id=user_id,
                db=db,
                paginated=True,
                page=page,
                page_size=page_size,
                with_user_info=True
            )


async def build_search_user_ids_and_like_text(search_text: str, db: Session) -> tuple[List[int], str]:
    """
    Common search user + like pattern construction logic, used for life posts / message_to_you.
    """
    search_user_ids: List[int] = []
    raw_nodes = await query_user_by_search_keyword(search_text)

    if raw_nodes:
        decoded_ids = [getAutherIDByNodeID(item["node"]["id"]) for item in raw_nodes]
        rows = db.query(User).filter(User.authgear_id.in_(decoded_ids)).all()
        search_user_ids = [row.id for row in rows]

    like_text = f"%{search_text}%"
    return search_user_ids, like_text


def apply_life_post_search_filter(base_query, model, search_user_ids: List[int], like_text: str):
    """
    Common search_text filter conditions: OR search by user_id or title/content.
    """
    search_conditions = []
    if search_user_ids:
        search_conditions.append(model.user_id.in_(search_user_ids))

    search_conditions.extend(
        [
            PostMaster.title.ilike(like_text),
            PostMaster.content.ilike(like_text),
        ]
    )
    return base_query.filter(or_(*search_conditions))


async def build_user_info_map(
    db: Session,
    item_id_user_pairs: List[tuple[int, int]],
) -> dict[int, object]:
    """
    Common user_info map construction logic.
    Parameters are (item_id, user_id) pair list.
    """
    user_info_map: dict[int, object] = {}
    if not item_id_user_pairs:
        return user_info_map

    user_ids = list({user_id for _, user_id in item_id_user_pairs})
    user_objs = db.query(User).filter(User.id.in_(user_ids)).all()
    user_id_to_authgear_id = {
        str(user.id): user.authgear_id for user in user_objs if user.authgear_id
    }
    authgear_ids = list(user_id_to_authgear_id.values())
    users_info = await get_users_info_with_cache(authgear_ids)

    for item_id, user_id in item_id_user_pairs:
        authgear_id = user_id_to_authgear_id.get(str(user_id))
        if authgear_id and authgear_id not in users_info:
            user_info_map[item_id] = DELETED_ACCOUNT_USER
        else:
            user_info_map[item_id] = users_info.get(authgear_id) if authgear_id else None

    return user_info_map


async def query_shared_posts(
    model:LifeMoment | MessageToYou,
    post_source,
    user_id: str,
    db: Session,
    search_text:str=None,
    random: bool = False,
    limit: int = 3,
    paginated: bool = False,
    page: int = 1,
    page_size: int = 10,
    with_user_info: bool = False,
):
    try:
        subq_permissions = get_subq_permissions(user_id, post_source, db)
        
        base_query = db.query(model, PostMaster).join(
            PostMaster, model.post_master_id == PostMaster.id
        ).filter(
            model.user_id != user_id,
            model.id.in_(subq_permissions)
        )

        # LIFE_MOMENT / LIFE_TRAJECTORY Share Post Search Text Behavior
        if post_source in (PostSourceEnum.LIFE_MOMENT, PostSourceEnum.LIFE_TRAJECTORY):
            if search_text != 'null' and search_text is not None and search_text != '':
                search_user_ids, like_text = await build_search_user_ids_and_like_text(
                    search_text, db
                )
                base_query = apply_life_post_search_filter(
                    base_query, model, search_user_ids, like_text
                )

        if post_source == PostSourceEnum.MESSAGE_TO_YOU:
            # Only read messages that have reached the time 
            base_query = base_query.filter(
                MessageToYou.when_can_read_the_post
                <= datetime.now(ZoneInfo("Asia/Hong_Kong"))
            )
            # MESSAGE_TO_YOU also supports search_text (by user/title/content)
            if search_text != 'null' and search_text is not None and search_text != '':
                search_user_ids, like_text = await build_search_user_ids_and_like_text(
                    search_text, db
                )
                search_conditions = []
                if search_user_ids:
                    search_conditions.append(model.user_id.in_(search_user_ids))
                search_conditions.extend(
                    [
                        PostMaster.title.ilike(like_text),
                        PostMaster.content.ilike(like_text),
                    ]
                )
                base_query = base_query.filter(or_(*search_conditions))

        if random:
            base_query = base_query.order_by(sql_func.random()).limit(limit)
            items = base_query.all()
        elif paginated:
            if post_source == PostSourceEnum.MESSAGE_TO_YOU:
                base_query = base_query.order_by(desc(MessageToYou.when_can_read_the_post))
            else:
                base_query = base_query.order_by(desc(PostMaster.created_at))
            paginated_results = paginate(base_query, page, page_size)
            items = paginated_results["items"]
        elif limit:
            if post_source == PostSourceEnum.MESSAGE_TO_YOU:
                base_query = base_query.order_by(desc(MessageToYou.when_can_read_the_post)).limit(limit)
            else:
                base_query = base_query.order_by(desc(PostMaster.created_at)).limit(limit)
            items = base_query.all()
        else:
            if post_source == PostSourceEnum.MESSAGE_TO_YOU:
                base_query = base_query.order_by(desc(MessageToYou.when_can_read_the_post))
            else:
                base_query = base_query.order_by(desc(PostMaster.created_at))
            items = base_query.all()

        media_url_map = {}
        for item, post_master in items:
            media_url_map[post_master.id] = await get_media_urls(post_master)

        

        # Get shared_replies_count for each post, count replies from current user and replies from post owner to current user
        my_replies_count_map = {}
        if items:
            post_master_ids = [post_master.id for _, post_master in items]
            post_master_to_owner = {
                post_master.id: item.user_id for item, post_master in items
            }
            my_replies_count_map = build_shared_replies_count_map(
                db, post_master_ids, user_id, post_master_to_owner
            )

        # user info
        user_info_map = {}
        if with_user_info:
            item_id_user_pairs = [(item.id, item.user_id) for item, _ in items]
            user_info_map = await build_user_info_map(db, item_id_user_pairs)

        result_list = []
        for item, post_master in items:
            download_url = media_url_map.get(post_master.id, {})
            shared_to_list = None
            shared_replies_count = my_replies_count_map.get(post_master.id, 0)
            result = build_post_result(
                item=item,
                post_master=post_master,
                shared_to_list=shared_to_list,
                download_url=download_url,
                user_info=user_info_map.get(item.id, POST_OWNER_IS_REQUESTER),
                exclude_ai_feedback=True
            )
            result["shared_replies_count"] = shared_replies_count
            result_list.append(result)

        if paginated:
            paginated_results["items"] = result_list
            return paginated_results
        else:
            return result_list
        
    except Exception as e:
        log_error(f"Error creating {post_source.value} post: {str(e)}")
        raise GeneralErrorExcpetion(str(e))
async def get_shared_life_moment_by_id(life_moment_id: int, user_id: str, db: Session):
    """
    Get a single shared life moment post by ID that the user has permission to read
    """
    try:
        # Check if user has permission to read this post
        subq_permissions = get_subq_permissions(user_id, PostSourceEnum.LIFE_MOMENT, db)
        
        # Query the specific life moment with permission check
        result = db.query(LifeMoment, PostMaster).join(
            PostMaster, LifeMoment.post_master_id == PostMaster.id
        ).filter(
            LifeMoment.id == life_moment_id,
            or_(
                LifeMoment.user_id == user_id,  # Owner
                and_(
                    LifeMoment.user_id != user_id,  # Not owner
                    LifeMoment.id.in_(subq_permissions)  # Has permission
                )
            )
        ).first()
        
        if not result:
            raise BadReqExpection(details="Life moment not found or you don't have permission to view it")
        
        life_moment, post_master = result
        
        # Get media URLs
        download_url = await get_media_urls(post_master)
        
        # Get user info for the post owner
        user_info = POST_OWNER_IS_REQUESTER if life_moment.user_id == user_id else None
        if user_info is None:
            user_obj = db.query(User).filter(User.id == life_moment.user_id).first()
            if user_obj and user_obj.authgear_id:
                users_info = await get_users_info_with_cache([user_obj.authgear_id])
                user_info = users_info.get(user_obj.authgear_id, DELETED_ACCOUNT_USER)
        
        # Get reply count between current user and post owner
        all_replies = db.query(RepliesMaster).filter(
            RepliesMaster.post_master_id == post_master.id,
            RepliesMaster.is_deleted == False
        ).all()
        
        # Count replies from current user and post owner replies in chains
        shared_replies_count = 0
        user_reply_ids = [r.id for r in all_replies if r.user_id == user_id]
        owner_chain_reply_ids = set()
        
        # Find direct responses from post owner to user
        for reply in all_replies:
            if (reply.user_id == life_moment.user_id and 
                reply.parent_reply_master_id in user_reply_ids):
                owner_chain_reply_ids.add(reply.id)
        
        # Find chained replies from post owner
        changed = True
        while changed:
            changed = False
            for reply in all_replies:
                if (reply.user_id == life_moment.user_id and 
                    reply.parent_reply_master_id in owner_chain_reply_ids and
                    reply.id not in owner_chain_reply_ids):
                    owner_chain_reply_ids.add(reply.id)
                    changed = True
        
        # Count all relevant replies
        for reply in all_replies:
            if reply.user_id == user_id or reply.id in owner_chain_reply_ids:
                shared_replies_count += 1
        
        # Build result
        result = build_post_result(
            item=life_moment,
            post_master=post_master,
            shared_to_list=None,
            download_url=download_url,
            user_info=user_info,
            exclude_ai_feedback=True
        )
        result["shared_replies_count"] = shared_replies_count
        
        return result
        
    except Exception as e:
        log_error(f"Error getting shared life moment by ID: {str(e)}")
        raise GeneralErrorExcpetion(str(e))

async def get_shared_life_trajectory_by_id(life_trajectory_id: int, user_id: str, db: Session):
    """
    Get a single shared life trajectory post by ID that the user has permission to read
    """
    try:

        # Check if user has permission to read this post
        subq_permissions = get_subq_permissions(user_id, PostSourceEnum.LIFE_TRAJECTORY, db)
        
        # Query the specific life trajectory with permission check
        result = db.query(LifeTrajectory, PostMaster).join(
            PostMaster, LifeTrajectory.post_master_id == PostMaster.id
        ).filter(
            LifeTrajectory.id == life_trajectory_id,
            or_(
                LifeTrajectory.user_id == user_id,  # Owner
                and_(
                    LifeTrajectory.user_id != user_id,  # Not owner
                    LifeTrajectory.id.in_(subq_permissions)  # Has permission
                )
            )
        ).first()

        if not result:
            raise BadReqExpection(details="Life trajectory not found or you don't have permission to view it")
        
        life_trajectory, post_master = result
        
        # Get media URLs
        download_url = await get_media_urls(post_master)
        
        # Get user info for the post owner
        user_info = POST_OWNER_IS_REQUESTER if life_trajectory.user_id == user_id else None
        if user_info is None:
            user_obj = db.query(User).filter(User.id == life_trajectory.user_id).first()
            if user_obj and user_obj.authgear_id:
                users_info = await get_users_info_with_cache([user_obj.authgear_id])
                user_info = users_info.get(user_obj.authgear_id, DELETED_ACCOUNT_USER)
        
        # Get reply count between current user and post owner
        all_replies = db.query(RepliesMaster).filter(
            RepliesMaster.post_master_id == post_master.id,
            RepliesMaster.is_deleted == False
        ).all()
        
        # Count replies from current user and post owner replies in chains
        shared_replies_count = 0
        user_reply_ids = [r.id for r in all_replies if r.user_id == user_id]
        owner_chain_reply_ids = set()
        
        # Find direct responses from post owner to user
        for reply in all_replies:
            if (reply.user_id == life_trajectory.user_id and 
                reply.parent_reply_master_id in user_reply_ids):
                owner_chain_reply_ids.add(reply.id)
        
        # Find chained replies from post owner
        changed = True
        while changed:
            changed = False
            for reply in all_replies:
                if (reply.user_id == life_trajectory.user_id and 
                    reply.parent_reply_master_id in owner_chain_reply_ids and
                    reply.id not in owner_chain_reply_ids):
                    owner_chain_reply_ids.add(reply.id)
                    changed = True
        
        # Count all relevant replies
        for reply in all_replies:
            if reply.user_id == user_id or reply.id in owner_chain_reply_ids:
                shared_replies_count += 1
        
        # Build result
        result = build_post_result(
            item=life_trajectory,
            post_master=post_master,
            shared_to_list=None,
            download_url=download_url,
            user_info=user_info,
            exclude_ai_feedback=True
        )
        result["shared_replies_count"] = shared_replies_count
        
        return result
        
    except Exception as e:
        log_error(f"Error getting shared life trajectory by ID: {str(e)}")
        raise GeneralErrorExcpetion(str(e))

async def get_shared_message_to_me_by_id(message_to_you_id: int, user_id: str, db: Session):
    """
    Get a single shared message to you post by ID that the user has permission to read and passed when_can_read_the_post
    """
    try:
        # Check if user has permission to read this post
        subq_permissions = get_subq_permissions(user_id, PostSourceEnum.MESSAGE_TO_YOU, db)
        
        # Query the specific message with permission and time check
        result = db.query(MessageToYou, PostMaster).join(
            PostMaster, MessageToYou.post_master_id == PostMaster.id
        ).filter(
            MessageToYou.id == message_to_you_id,
            or_(
                MessageToYou.user_id == user_id,  # Owner (no time restriction)
                and_(
                    MessageToYou.user_id != user_id,  # Not owner
                    MessageToYou.id.in_(subq_permissions),  # Has permission
                    MessageToYou.when_can_read_the_post <= datetime.now(ZoneInfo("Asia/Hong_Kong"))  # Time check
                )
            )
        ).first()
        
        if not result:
            raise BadReqExpection(details="Message not found, you don't have permission to view it, or it's not yet available to read")
        
        message_to_you, post_master = result
        
        # Get media URLs
        download_url = await get_media_urls(post_master)
        
        # Get user info for the post owner
        user_info = POST_OWNER_IS_REQUESTER if message_to_you.user_id == user_id else None
        if user_info is None:
            user_obj = db.query(User).filter(User.id == message_to_you.user_id).first()
            if user_obj and user_obj.authgear_id:
                users_info = await get_users_info_with_cache([user_obj.authgear_id])
                user_info = users_info.get(user_obj.authgear_id, DELETED_ACCOUNT_USER)
        
        # Get reply count between current user and post owner
        all_replies = db.query(RepliesMaster).filter(
            RepliesMaster.post_master_id == post_master.id,
            RepliesMaster.is_deleted == False
        ).all()
        
        # Count replies from current user and post owner replies in chains
        shared_replies_count = 0
        user_reply_ids = [r.id for r in all_replies if r.user_id == user_id]
        owner_chain_reply_ids = set()
        
        # Find direct responses from post owner to user
        for reply in all_replies:
            if (reply.user_id == message_to_you.user_id and 
                reply.parent_reply_master_id in user_reply_ids):
                owner_chain_reply_ids.add(reply.id)
        
        # Find chained replies from post owner
        changed = True
        while changed:
            changed = False
            for reply in all_replies:
                if (reply.user_id == message_to_you.user_id and 
                    reply.parent_reply_master_id in owner_chain_reply_ids and
                    reply.id not in owner_chain_reply_ids):
                    owner_chain_reply_ids.add(reply.id)
                    changed = True
        
        # Count all relevant replies
        for reply in all_replies:
            if reply.user_id == user_id or reply.id in owner_chain_reply_ids:
                shared_replies_count += 1
        
        # Build result
        result = build_post_result(
            item=message_to_you,
            post_master=post_master,
            shared_to_list=None,
            download_url=download_url,
            user_info=user_info
        )
        result["shared_replies_count"] = shared_replies_count
        
        return result
        
    except Exception as e:
        log_error(f"Error getting shared message to you by ID: {str(e)}")
        raise GeneralErrorExcpetion(str(e))

async def manage_user_group_trx(reqBody:ManageUserGroupBaseInputRequest,user_id:str,db:Session):
    try:
        req = reqBody.model_dump()
        
        groupData = req.get('groupData')
        selected_user_data = req.get('selected_user_data')
        # log_info(f'groupData---->{groupData}')
        # log_info(f'selected_user_data---->{selected_user_data}')

        for group in groupData:
            if group.get('selected_user_is_exist'):
                # user require to join group
                # check if selected_user exist permission group member
                row = db.query(PostsPermissionsGroupMembers).filter(PostsPermissionsGroupMembers.group_id == group.get('group_id'),PostsPermissionsGroupMembers.phone_number_prefix == selected_user_data.get('phone_number_prefix'),PostsPermissionsGroupMembers.phone_number == selected_user_data.get('phone_number')).first()
                if row:
                    continue
                else:
                    # log_info(f'user require to join group -----> gid={group.get('group_id')} uid={selected_user_data.get('user_id')}')
                    insert_obj = PostsPermissionsGroupMembers(group_id=group.get('group_id'),user_id=selected_user_data.get('user_id') or None,phone_number_prefix=selected_user_data.get('phone_number_prefix'),phone_number=selected_user_data.get('phone_number'),first_name=selected_user_data.get('first_name'),last_name=selected_user_data.get('last_name'))
                    wrap_insert_mapping_func(db, insert_obj)
                    
            else:    
                # user require to leave group
                # check if selected_user exist permission group member
                row = db.query(PostsPermissionsGroupMembers).filter(PostsPermissionsGroupMembers.group_id == group.get('group_id'),PostsPermissionsGroupMembers.phone_number_prefix == selected_user_data.get('phone_number_prefix'),PostsPermissionsGroupMembers.phone_number == selected_user_data.get('phone_number')).first()
                if row:
                    # log_info(f'user require to leave group -----> rowId={row.id}')
                    # remove foreign key(shared_to) row of post_shared_recipients -> remove permission group member row
                    wrap_delete_func(PostSharedRecipients,{"shared_to": row.id},db,True)
                    wrap_delete_func(PostsPermissionsGroupMembers,{"id": row.id},db,True)
                else:
                    continue
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        raise GeneralErrorExcpetion(str(e))     