from datetime import datetime
from fastapi import APIRouter, Depends, Request, UploadFile, Form, Query
from src.loggerServices import log_error, log_info
from src.secertBase.service import check_dead_user_permission
from src.oss.service import upload_multiple_files
from src.utils.response import create_success_response
from src.exceptions import  handle_exceptions
from src.models import get_error_response_model
from src.schemas import ApiSuccessResponseModel
from src.posts.schemas import (AddPermissionsGroupMembersRequest, CreatePermissionsGroupRequest,
    CustomLifePostTypeBase, DefineWhichCustomLifePostType, EditPermissionsGroupMemberRequest,
    EditPermissionsGroupRequest, GetMyCreatedMsgQueryParams,
    LifeMomentAndLifeTrajectoryBaseQueryParams, LifeMomentsBaseInputRequest,
    LifeTrajectoryBaseInputRequest, ManageUserGroupBaseInputRequest, MessageToYouBaseInputRequest, PostFileType)
from src.database import get_db
from sqlalchemy.orm import Session
from src.posts.service import (add_permissions_group_members, create_custom_life_post_type,
    create_life_moment, create_lift_trajectory, create_message_to_you, create_permissions_group,
    delete_custom_life_post_type, delete_life_moment, delete_life_trajectory,
    delete_message_to_you, edit_life_moment, edit_life_trajectory, edit_message_to_you,
    edit_permissions_group_member, edit_permissions_group_name, get_all_post_types,
    get_custom_life_post_types, get_my_life_moments, get_my_life_trajectories,
    get_my_messages_by_type_code, manage_user_group_trx, remove_permissions_group,
    remove_permissions_group_member_v2, update_custom_life_post_type, get_user_permissions_groups,
    get_random_my_life_moments, get_msg_to_me, get_shared_life_moments,
    get_shared_life_moments_paginated, get_shared_message_to_me_paginated, get_shared_life_moment_by_id, get_shared_life_trajectory_by_id, get_shared_message_to_me_by_id, get_shared_life_experiences,
    get_shared_life_experiences_paginated)
from src.replies.service import get_replies_only
from src.posts.models import (PostSourceEnum)
from src.posts.response import (AllPostTypesResponse, CustomLifePostTypeResponse,
    GetPermissionsGroupResponseModel, 
     PermissionsGroupsListResponseModel, PostRepliesResponse)
from src.utils.pagination import paginated_object_mapping
from src.response import PaginatedResponseModel
from typing import List, Dict, Optional
from src.utils.response_formatters import (
    format_life_moments_response,
    format_shared_life_moments_response,
    format_life_trajectories_response,
    format_messages_response,
    format_shared_messages_response,
    format_my_life_moment_items,
    format_shared_life_moment_items,
    format_shared_life_trajectory_items,
    format_message_items,
    format_shared_life_experiences_items,
    format_shared_life_experiences_paginated_response,
)
from src.myLifeChart.service import get_life_moments_by_ids, get_mood_analytics


router = APIRouter()

@router.delete("/delete/life_moment/{id}", response_model=ApiSuccessResponseModel, responses=get_error_response_model)
@handle_exceptions
async def delete_life_moment_route(request: Request, id: int, db: Session = Depends(get_db)):
    user_id = request.state.user_id
    delete_life_moment(id, user_id, db)
    return create_success_response({"detail": "Life moment deleted successfully"})

@router.delete("/delete/life_trajectory/{id}", response_model=ApiSuccessResponseModel, responses=get_error_response_model)
@handle_exceptions
async def delete_life_trajectory_route(request: Request, id: int, db: Session = Depends(get_db)):
    user_id = request.state.user_id
    delete_life_trajectory(id, user_id, db)
    return create_success_response({"detail": "Life trajectory deleted successfully"})

@router.delete("/delete/message_to_you/{id}", response_model=ApiSuccessResponseModel, responses=get_error_response_model)
@handle_exceptions
async def delete_message_to_you_route(request: Request, id: int, db: Session = Depends(get_db)):
    user_id = request.state.user_id
    delete_message_to_you(id, user_id, db)
    return create_success_response({"detail": "Message deleted successfully"})

@router.put("/edit/life_moment/{id}", response_model=ApiSuccessResponseModel, responses=get_error_response_model)
@handle_exceptions
async def update_life_moment(request: Request,id: int, update_data: LifeMomentsBaseInputRequest, db: Session = Depends(get_db)):

    # print(f"***** update_life_moment - update_data: {update_data}")
    user_id = request.state.user_id
    result = edit_life_moment(id, update_data, db,user_id)
    return create_success_response({
        "can_ai_feedback": result.get("can_ai_feedback", False)
    })

@router.put("/edit/life_trajectory/{id}", response_model=ApiSuccessResponseModel, responses=get_error_response_model)
@handle_exceptions
async def update_life_trajectory(request: Request, id: int, update_data: LifeTrajectoryBaseInputRequest, db: Session = Depends(get_db)):
    user_id = request.state.user_id
    edit_life_trajectory(id, update_data, db,user_id)
    return create_success_response({})

@router.put("/edit/message_to_you/{id}", response_model=ApiSuccessResponseModel, responses=get_error_response_model)
@handle_exceptions
async def update_message_to_you(request: Request, id: int, update_data: MessageToYouBaseInputRequest, db: Session = Depends(get_db)):
    user_id = request.state.user_id
    edit_message_to_you(id, update_data, db, user_id)
    return create_success_response({})

@router.post("/create/life_moment", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def create_life_moment_route(request: Request,life_moment: LifeMomentsBaseInputRequest, db: Session = Depends(get_db)):
    try:
        # print(f"***** create_life_moment_route - life_moment: {life_moment}")
        user_id = request.state.user_id
        result = create_life_moment(life_moment,user_id,db)
        # return create_success_response({})
        post_id = None
        post = result.get('post')
        # print the detail of the post
        if hasattr(post, 'id'):  # Check if post is a model object with id attribute
            post_id = post.id

        return create_success_response({
            "can_ai_feedback": result.get("can_ai_feedback"),
            "post_id": post_id
        })
    except Exception as e:
        log_error(f"Error creating life moment: {e}")
        raise

@router.post("/create/life_trajectory", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def create_life_trajectory_route(request: Request,life_trajectory: LifeTrajectoryBaseInputRequest, db: Session = Depends(get_db)):
    user_id = request.state.user_id
    create_lift_trajectory(life_trajectory,user_id, db)
    return create_success_response({})

@router.post("/create/message_to_you", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def create_message_to_you_route(request: Request,message_to_you_data: MessageToYouBaseInputRequest, db: Session = Depends(get_db)):
    user_id = request.state.user_id
    create_message_to_you(message_to_you_data, user_id, db)
    return create_success_response({})

@router.get("/get/my_life_moments", response_model=ApiSuccessResponseModel[PaginatedResponseModel], responses=get_error_response_model)
@handle_exceptions
async def my_life_moments_route(
    request: Request,
    post_ids: Optional[List[int]] = Query(None, description="expect post_ids, if provided, ignore other filters"),
    page: int = 1,
    page_size: int = 10,
    create_from: Optional[str] = None,
    create_to: Optional[str] = None,
    min_motion_rate: Optional[float] = None,
    max_motion_rate: Optional[float] = None,
    post_type_code: Optional[List[str]] = Query(None),
    custom_post_type_id: Optional[List[int]] = Query(None),
    search_text: Optional[str] = Query(None),
    deaduserID: str | None = None,
    db: Session = Depends(get_db)
):
    user_id = request.state.user_id

    if post_ids:
        # paginated_results = await get_life_moments_by_ids(post_ids, user_id, page, page_size, db)
        if deaduserID:
            paginated_results = await get_life_moments_by_ids(is_owner=False,post_ids=post_ids, user_id=deaduserID, page=page, page_size=page_size, db=db,cb=check_dead_user_permission(user_id=user_id,dead_user_id=deaduserID,db=db,key="LET"))
        else:
            paginated_results = await get_life_moments_by_ids(is_owner=True,post_ids=post_ids, user_id=user_id, page=page, page_size=page_size, db=db)
    else:
        query_params = LifeMomentAndLifeTrajectoryBaseQueryParams(
            page=page,
            page_size=page_size,
            create_from=create_from,
            create_to=create_to,
            min_motion_rate=min_motion_rate,
            max_motion_rate=max_motion_rate,
            post_type_code=post_type_code,
            custom_post_type_id=custom_post_type_id,
            search_text=search_text
        )
        
        # paginated_results = await get_my_life_moments(query_params=query_params,user_id=user_id, db=db)
        if deaduserID:
            paginated_results = await get_my_life_moments(query_params=query_params,user_id=deaduserID, db=db,cb=check_dead_user_permission(user_id=user_id,dead_user_id=deaduserID,db=db,key="LET"))
        else:
            paginated_results = await get_my_life_moments(query_params=query_params,user_id=user_id, db=db)
    
    result_mapping = format_life_moments_response(paginated_results) if paginated_results != [] else []
    return create_success_response(result_mapping)

@router.get("/get/my_life_trajectories", response_model=ApiSuccessResponseModel[PaginatedResponseModel], responses=get_error_response_model)
@handle_exceptions
async def my_life_trajectories_route(
    request: Request,
    page: int = 1,
    page_size: int = 10,
    create_from: Optional[str] = None,
    create_to: Optional[str] = None,
    min_motion_rate: Optional[float] = None,
    max_motion_rate: Optional[float] = None,
    post_type_code: Optional[List[str]] = Query(None),
    custom_post_type_id: Optional[List[int]] = Query(None),
    search_text: Optional[str] = Query(None),
    deaduserID: str | None = None,

    db: Session = Depends(get_db)
):
    # 添加内存监控
    import os, psutil, logging
    def log_mem(marker):
        proc = psutil.Process(os.getpid())
        mem = proc.memory_info().rss / 1024 / 1024
        logging.warning(f"【内存监控】{marker}: {mem:.2f}MB")
    
    log_mem("my_life_trajectories 开始")
    
    user_id = request.state.user_id
    
    query_params = LifeMomentAndLifeTrajectoryBaseQueryParams(
        page=page,
        page_size=page_size,
        create_from=create_from,
        create_to=create_to,
        min_motion_rate=min_motion_rate,
        max_motion_rate=max_motion_rate,
        post_type_code=post_type_code,
        custom_post_type_id=custom_post_type_id,
        search_text=search_text
    )
    
    log_mem("参数准备完成")
    
    # paginated_results = await get_my_life_trajectories(query_params=query_params,user_id=user_id, db=db)
    if deaduserID:
        log_mem("查询deaduserID前")
        paginated_results = await get_my_life_trajectories(query_params=query_params,user_id=deaduserID, db=db,cb=check_dead_user_permission(user_id=user_id,dead_user_id=deaduserID,db=db,key="LET"))
        log_mem("查询deaduserID后")
    else:
        log_mem("查询普通用户前")
        paginated_results = await get_my_life_trajectories(query_params=query_params,user_id=user_id, db=db)
        log_mem("查询普通用户后")
        
    log_mem("格式化结果前")
    result_mapping = format_life_trajectories_response(paginated_results) if paginated_results != [] else []
    log_mem("格式化结果后")
    
    log_mem("my_life_trajectories 结束")
    return create_success_response(result_mapping)

@router.get("/get/my_created_msg_by_type_code", response_model=ApiSuccessResponseModel[PaginatedResponseModel], responses=get_error_response_model)
@handle_exceptions
async def my_messages_by_type_code_route(request: Request, page: int = 1,
    page_size: int = 10, type_code: Optional[str] = None, db: Session = Depends(get_db),deaduserID: str | None = None):
    user_id = request.state.user_id
    getMsgToYouData = GetMyCreatedMsgQueryParams(page=page, page_size=page_size, type_code=type_code)
    # paginated_results = await get_my_messages_by_type_code(getMsgToYouData, user_id, db=db)
    if deaduserID:
        paginated_results = await get_my_messages_by_type_code(getMsgToYouData, deaduserID, db=db,cb=check_dead_user_permission(user_id=user_id,dead_user_id=deaduserID,db=db,key="MTS"))
    else:
        paginated_results = await get_my_messages_by_type_code(getMsgToYouData, user_id, db=db)
    response = format_messages_response(paginated_results) if paginated_results != [] else []
    return create_success_response(response)

# @router.post("/file/upload", status_code=200 , response_model=ApiSuccessResponseModel,responses=get_error_response_model)
# @handle_exceptions
# async def file_upload_route(request: Request, files: List[UploadFile], file_type: PostFileType = Form(...)):
        
#     user_id = request.state.user_id
#     file_list =  await upload_multiple_files(user_id,files,file_type.value,"posts")
    
#     return create_success_response(file_list)

@router.post("/create/permissions_group", response_model=ApiSuccessResponseModel, responses=get_error_response_model)
@handle_exceptions
async def create_permissions_group_route(request: Request, group_data: CreatePermissionsGroupRequest, db: Session = Depends(get_db)):
    user_id = request.state.user_id
    group_id = create_permissions_group(group_data, user_id, db)
    return create_success_response({"group_id": group_id})

@router.post("/add/permissions_group/{group_id}/members", response_model=ApiSuccessResponseModel, responses=get_error_response_model)
@handle_exceptions
async def add_permissions_group_members_route(request: Request, group_id: int, members_data: AddPermissionsGroupMembersRequest, db: Session = Depends(get_db)):
    user_id = request.state.user_id
    member_user_id = await add_permissions_group_members(group_id, members_data, user_id, db)
    return create_success_response({ "user_ids": member_user_id })

@router.put("/edit/permissions_group/{group_id}", response_model=ApiSuccessResponseModel, responses=get_error_response_model)
@handle_exceptions
async def edit_permissions_group_name_route(request: Request, group_id: int, group_data: EditPermissionsGroupRequest, db: Session = Depends(get_db)):
    user_id = request.state.user_id
    edit_permissions_group_name(group_id, group_data, user_id, db)
    return create_success_response({})

@router.put("/edit/permissions_group/{group_id}/group_member/{group_member_id}", response_model=ApiSuccessResponseModel, responses=get_error_response_model)
@handle_exceptions
async def edit_permissions_group_member_route(request: Request, group_id: int, group_member_id: str, member_data: EditPermissionsGroupMemberRequest, db: Session = Depends(get_db)):
    user_id = request.state.user_id
    member_user_id = await edit_permissions_group_member(group_id, group_member_id, member_data, user_id, db)
    return create_success_response({ "user_ids": member_user_id })

# @router.delete("/remove/permissions_group/{group_id}/members/{member_id}", response_model=ApiSuccessResponseModel, responses=get_error_response_model)
# @handle_exceptions
# async def remove_permissions_group_member_route(request: Request, group_id: int, member_id: str, db: Session = Depends(get_db)):
#     user_id = request.state.user_id
#     result = await remove_permissions_group_member(group_id=group_id, member_id=member_id, user_id=user_id, db=db)
#     return create_success_response(result)

@router.delete("/removeV2/permissions_group/{group_id}/members/{full_phone_number}", response_model=ApiSuccessResponseModel, responses=get_error_response_model)
@handle_exceptions
async def remove_permissions_group_member_route(request: Request, group_id: int, full_phone_number: str, db: Session = Depends(get_db)):
    user_id = request.state.user_id
    result = await remove_permissions_group_member_v2(group_id=group_id,full_phone_number=full_phone_number, db=db)
    return create_success_response(result)


@router.delete("/remove/permissions_group/{group_id}", response_model=ApiSuccessResponseModel, responses=get_error_response_model)
@handle_exceptions
async def remove_permissions_group_route(request: Request, group_id: int, db: Session = Depends(get_db)):
    user_id = request.state.user_id
    remove_permissions_group(group_id, user_id, db)
    return create_success_response({})






# @router.get("/get/permissions_group/{group_id}", response_model=ApiSuccessResponseModel, responses=get_error_response_model)
# @handle_exceptions
# async def get_permissions_group_info_route(request: Request, group_id: int, db: Session = Depends(get_db),deaduserID: str | None = None):
#     user_id = request.state.user_id
#     # group_info = get_permissions_group_info(group_id, user_id, db)

#     if deaduserID:
#         group_info = await get_permissions_group_info(group_id, deaduserID, db,cb=check_dead_user_permission(user_id=user_id,dead_user_id=deaduserID,db=db,key="LET"))
#     else:
#         group_info = await get_permissions_group_info(group_id, user_id, db)

#     response = GetPermissionsGroupResponseModel(
#         group=group_info["group"],
#         members=group_info["members"]
#     ) if group_info != [] else []
#     return create_success_response(response)

@router.get("/get/permissions_groups", response_model=ApiSuccessResponseModel[PermissionsGroupsListResponseModel], responses=get_error_response_model)
@handle_exceptions
async def get_user_permissions_groups_route(request: Request, db: Session = Depends(get_db),deaduserID: str | None = None):
    user_id = request.state.user_id
    # groups_data = get_user_permissions_groups(user_id, db)

    if deaduserID:
        groups_data = await get_user_permissions_groups(deaduserID, db,cb=check_dead_user_permission(user_id=user_id,dead_user_id=deaduserID,db=db,key="LET"))
    else:
        groups_data = await get_user_permissions_groups(user_id, db)

    # Transform the data to match the expected response model
    groups_response = []
    for group_data in groups_data:
        groups_response.append(
            GetPermissionsGroupResponseModel(
                group=group_data["group"],
                members=group_data["members"]
            )
        )
    
    response = PermissionsGroupsListResponseModel(groups=groups_response) if groups_response != [] else []
    return create_success_response(response)

@router.post("/create/custom_life_post_types", response_model=ApiSuccessResponseModel[CustomLifePostTypeResponse],responses=get_error_response_model)
async def create_custom_post_type(req: CustomLifePostTypeBase, request: Request, db: Session = Depends(get_db)):
    user_id = request.state.user_id
    new_type = create_custom_life_post_type(req, user_id, db)
    return create_success_response(new_type)

@router.get("/get/get_all_post_types", response_model=ApiSuccessResponseModel[AllPostTypesResponse],responses=get_error_response_model)
async def list_all_post_types(request: Request, req:DefineWhichCustomLifePostType = Depends(), db: Session = Depends(get_db),deaduserID: str | None = None):
    user_id = request.state.user_id
    # types_list = get_all_post_types(req,user_id, db)

    if deaduserID:
        types_list =  await get_all_post_types(req,deaduserID, db,cb=check_dead_user_permission(user_id=user_id,dead_user_id=deaduserID,db=db,key="LET"))
    else:
        types_list = await get_all_post_types(req,user_id, db)
    
    response = AllPostTypesResponse(
        default_types=types_list["default_types"],
        custom_types=types_list["custom_types"]
    ) if types_list != [] else []
    return create_success_response(response)

@router.get("/get/custom_life_post_types", response_model=ApiSuccessResponseModel[List[CustomLifePostTypeResponse]],responses=get_error_response_model)
async def list_custom_post_types(request: Request, req:DefineWhichCustomLifePostType = Depends(), db: Session = Depends(get_db),deaduserID: str | None = None):
    user_id = request.state.user_id
    # types_list = get_custom_life_post_types(req,user_id, db)

    if deaduserID:
        types_list = await get_custom_life_post_types(req,deaduserID, db,cb=check_dead_user_permission(user_id=user_id,dead_user_id=deaduserID,db=db,key="LET"))
    else:
        types_list = await get_custom_life_post_types(req,user_id, db)

    return create_success_response(types_list)

@router.put("/update/custom_life_post_types/{type_id}", response_model=ApiSuccessResponseModel, responses=get_error_response_model)
async def edit_custom_post_type(type_id: int, update_data: CustomLifePostTypeBase, request: Request, db: Session = Depends(get_db)):
    user_id = request.state.user_id
    update_custom_life_post_type(type_id, update_data, user_id, db)
    return create_success_response({"detail": "Update successfully"})

@router.post("/remove/custom_life_post_types/{type_id}",response_model=ApiSuccessResponseModel, responses=get_error_response_model)
async def delete_custom_post_type(req:DefineWhichCustomLifePostType, type_id: int, request: Request, db: Session = Depends(get_db)):
    user_id = request.state.user_id
    delete_custom_life_post_type(req, type_id, user_id, db)
    return create_success_response({"detail": "Deleted successfully"})

@router.get("/get/homepage_data", response_model=ApiSuccessResponseModel, responses=get_error_response_model)
@handle_exceptions
async def get_my_life_homepage_data(request: Request,
                                    start_date: datetime,
                                    end_date: datetime,
                                     db: Session = Depends(get_db)):

    user_id = request.state.user_id
    my_life_moments = await get_random_my_life_moments(user_id, db)
    msg_to_me = await get_msg_to_me(user_id, db)
    shared_life_moments = await get_shared_life_moments(user_id, db)
    shared_life_experiences = await get_shared_life_experiences(user_id, db)
    # Calculate average_mood_of_month
    mood_analytics = await get_mood_analytics(start_date, end_date, user_id, db)
    average_mood_of_month = mood_analytics.get('summary', {}).get('average_mood', 0)
    total_posts = mood_analytics.get('summary', {}).get('total_posts', 0)

    response = {
        'myLifeFeedback': {
            'average_mood_of_month': average_mood_of_month,
            'total_posts': total_posts
        },
        'mylifemome': format_my_life_moment_items(my_life_moments),
        'sharedLifeExperiences': format_shared_life_experiences_items(shared_life_experiences),
        'msgToMe': format_message_items(msg_to_me),
        'sharedLifeMoments': format_shared_life_moment_items(shared_life_moments),

    }
    return create_success_response(response)
@router.get("/get/shared_with_me/life_experiences", response_model=ApiSuccessResponseModel[PaginatedResponseModel], responses=get_error_response_model)
@handle_exceptions
async def shared_life_experiences_paginated_route(
    request: Request,
    page: int = 1,
    page_size: int = 10,
    search_text: str = None,
    db: Session = Depends(get_db),
    deaduserID: str | None = None
):
    user_id = request.state.user_id
    if deaduserID:
        paginated_results = await get_shared_life_experiences_paginated(
            user_id=deaduserID,
            page=page,
            page_size=page_size,
            db=db,
            search_text=search_text,
            cb=check_dead_user_permission(user_id=user_id, dead_user_id=deaduserID, db=db, key="LET"),
        )
    else:
        paginated_results = await get_shared_life_experiences_paginated(
            user_id=user_id,
            page=page,
            page_size=page_size,
            db=db,
            search_text=search_text,
        )
    result_mapping = format_shared_life_experiences_paginated_response(paginated_results)
    # print(result_mapping)
    return create_success_response(result_mapping)

@router.get("/get/shared_with_me/life_moments", response_model=ApiSuccessResponseModel[PaginatedResponseModel], responses=get_error_response_model)
@handle_exceptions
async def shared_life_moments_paginated_route(
    request: Request,
    page: int = 1,
    page_size: int = 10,
    search_text: str = None,
    db: Session = Depends(get_db),
    deaduserID: str | None = None
):
    user_id = request.state.user_id
    # paginated_results = await get_shared_life_moments_paginated(user_id=user_id, page=page, page_size=page_size, db=db)
    if deaduserID:
        paginated_results = await get_shared_life_moments_paginated(user_id=deaduserID, page=page, page_size=page_size, db=db,search_text=search_text,cb=check_dead_user_permission(user_id=user_id,dead_user_id=deaduserID,db=db,key="LET"))
    else:
        paginated_results = await get_shared_life_moments_paginated(user_id=user_id, page=page, page_size=page_size, db=db,search_text=search_text)
    result_mapping = format_shared_life_moments_response(paginated_results) if paginated_results != [] else []
    return create_success_response(result_mapping)

@router.get("/get/shared_with_me/msg_to_me", response_model=ApiSuccessResponseModel[PaginatedResponseModel], responses=get_error_response_model)
@handle_exceptions
async def shared_message_to_me_paginated_route(
    request: Request,
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db),
    deaduserID: str | None = None
):
    user_id = request.state.user_id
    if deaduserID:
        paginated_results = await get_shared_message_to_me_paginated(user_id=deaduserID, page=page, page_size=page_size, db=db,cb=check_dead_user_permission(user_id=user_id,dead_user_id=deaduserID,db=db,key="MTS"))
    else:
        paginated_results = await get_shared_message_to_me_paginated(user_id=user_id, page=page, page_size=page_size, db=db)
    result_mapping = format_shared_messages_response(paginated_results) if paginated_results != [] else []
    return create_success_response(result_mapping)

@router.get("/get/shared_with_me/life_moments/{life_moment_post_id}", response_model=ApiSuccessResponseModel, responses=get_error_response_model)
@handle_exceptions
async def get_shared_life_moment_by_id_route(
    request: Request,
    life_moment_post_id: int,
    db: Session = Depends(get_db)
):
    """Get a single shared life moment post by ID that the user has permission to read"""
    user_id = request.state.user_id
    result = await get_shared_life_moment_by_id(life_moment_post_id, user_id, db)
    formatted_result = format_shared_life_moment_items([result])[0]
    return create_success_response(formatted_result)

@router.get("/get/shared_with_me/life_trajectories/{life_trajectory_post_id}", response_model=ApiSuccessResponseModel, responses=get_error_response_model)
@handle_exceptions
async def get_shared_life_trajectory_by_id_route(
    request: Request,
    life_trajectory_post_id: int,
    db: Session = Depends(get_db)
):
    """Get a single shared life trajectory post by ID that the user has permission to read"""
    user_id = request.state.user_id
    result = await get_shared_life_trajectory_by_id(life_trajectory_post_id, user_id, db)
    formatted_result = format_shared_life_trajectory_items([result])[0]
    return create_success_response(formatted_result)

@router.get("/get/shared_with_me/msg_to_me/{message_to_you_post_id}", response_model=ApiSuccessResponseModel, responses=get_error_response_model)
@handle_exceptions
async def get_shared_message_to_me_by_id_route(
    request: Request,
    message_to_you_post_id: int,
    db: Session = Depends(get_db)
):
    """Get a single shared message to you post by ID that the user has permission to read and passed when_can_read_the_post"""
    user_id = request.state.user_id
    result = await get_shared_message_to_me_by_id(message_to_you_post_id, user_id, db)
    formatted_result = format_message_items([result])[0]
    return create_success_response(formatted_result)

@router.get("/replies/life_moment/{id}", response_model=ApiSuccessResponseModel[PostRepliesResponse], responses=get_error_response_model)
@handle_exceptions
async def get_life_moment_with_replies(
    request: Request,
    id: int,
    db: Session = Depends(get_db)
):
    """Get life_moment Replies"""
    user_id = request.state.user_id
    
    result = await get_replies_only(PostSourceEnum.LIFE_MOMENT, id, user_id, db)
    
    return create_success_response(result)

@router.get("/replies/life_trajectory/{id}", response_model=ApiSuccessResponseModel[PostRepliesResponse], responses=get_error_response_model)
@handle_exceptions
async def get_life_trajectory_with_replies(
    request: Request,
    id: int,
    db: Session = Depends(get_db)
):
    """Get life_trajectory Replies"""
    user_id = request.state.user_id
    
    result = await get_replies_only(PostSourceEnum.LIFE_TRAJECTORY, id, user_id, db)
    
    return create_success_response(result)

@router.get("/replies/message_to_you/{id}", response_model=ApiSuccessResponseModel[PostRepliesResponse], responses=get_error_response_model)
@handle_exceptions
async def get_message_to_you_with_replies(
    request: Request,
    id: int,
    db: Session = Depends(get_db)
):
    """Get message_to_you Replies"""
    user_id = request.state.user_id
    
    result = await get_replies_only(PostSourceEnum.MESSAGE_TO_YOU, id, user_id, db)
    
    return create_success_response(result)

@router.post("/manage_user_group", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def manage_user_group(request: Request,reqBody:ManageUserGroupBaseInputRequest,db:Session = Depends(get_db)):
    user_id = request.state.user_id
    result = await manage_user_group_trx(reqBody=reqBody,user_id=user_id,db=db)
    return create_success_response(result)
