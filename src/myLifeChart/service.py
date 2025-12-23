from sqlalchemy.orm import Session
import src.auth.service
from src.utils.fileUtil import get_media_urls
from typing import List, Dict, Any, TypedDict,Callable
from datetime import datetime, timedelta, date

from src.posts.models import LifeMoment, PostMaster, PostUserPermissions, PostSharedRecipients, PostsPermissionsGroupMembers
from src.posts.models import PostSourceEnum
from src.utils.pagination import paginate
from src.utils.commonUtil import build_post_result, exclude_fields_from_model

from src.myLifeChart.utils import group_mood_data_by_time, calculate_mood_summary
from src.posts.constants import POST_OWNER_IS_REQUESTER
from src.posts.constants import DELETED_ACCOUNT_USER
from src.auth.models import User
from src.auth.service import get_users_info_with_cache

async def get_mood_analytics(start_date: datetime, end_date: datetime, user_id: str, db: Session,cb: Callable[[], bool]=None):
    if cb:
        p = await cb
        if not p:
            return []

    query = db.query(
        LifeMoment,
        PostMaster
    ).join(
        PostMaster,
        LifeMoment.post_master_id == PostMaster.id
    ).filter(
        LifeMoment.user_id == user_id,
        PostMaster.start_date.between(start_date, end_date)
    )
    
    mood_data = query.all()
    
    delta = end_date - start_date
    
    if delta.days <= 31:  # one month
        time_dimension = 'day'
        time_points = []
        current = start_date
        while current <= end_date:
            time_points.append(current.date())
            current += timedelta(days=1)
    elif delta.days <= 366:  # one year
        time_dimension = 'month'
        time_points = []
        current = datetime(start_date.year, start_date.month, 1)
        while current <= end_date:
            time_points.append(current.date())
            if current.month == 12:
                current = datetime(current.year + 1, 1, 1)
            else:
                current = datetime(current.year, current.month + 1, 1)
    else:  # more than one year
        time_dimension = 'year'
        time_points = []
        current = datetime(start_date.year, 1, 1)
        while current <= end_date:
            time_points.append(current.date())
            current = datetime(current.year + 1, 1, 1)
    
    timeline_data = group_mood_data_by_time(mood_data, time_points)
    
    summary = calculate_mood_summary(timeline_data)
    
    return {
        "time_range": {
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "dimension": time_dimension
        },
        "timeline": timeline_data,
        "summary": summary
    }

async def get_life_moments_by_ids(is_owner: bool,post_ids: List[int], user_id: str, page: int, page_size: int, db: Session,cb: Callable[[], bool]=None):
    if cb:
        p = await cb
        if not p:
            return []

    query = db.query(
        LifeMoment,
        PostMaster
    ).join(
        PostMaster,
        LifeMoment.post_master_id == PostMaster.id
    ).filter(
        LifeMoment.id.in_(post_ids),
        LifeMoment.user_id == user_id
    )
    
    paginated_results = paginate(query, page, page_size)
    post_ids_in_page = [item[0].id for item in paginated_results["items"]]
    
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
    
    # Get total replies count
    total_replies_map = {}
    if paginated_results["items"]:
        from src.replies.models import RepliesMaster
        from sqlalchemy.sql.expression import func as sql_func
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
    if not is_owner:
        user_ids = list(set([item[0].user_id for item in paginated_results["items"]]))
        user_objs = db.query(User).filter(User.id.in_(user_ids)).all()
        user_id_to_authgear_id = {str(user.id): user.authgear_id for user in user_objs if user.authgear_id}
        authgear_ids = list(user_id_to_authgear_id.values())
        users_info = await get_users_info_with_cache(authgear_ids)
        for item, _ in paginated_results["items"]:
            authgear_id = user_id_to_authgear_id.get(str(item.user_id))
            if authgear_id and authgear_id not in users_info:
                user_info_map[item.id] = DELETED_ACCOUNT_USER
            else:
                user_info_map[item.id] = users_info.get(authgear_id) if authgear_id else None
    
    result_list = []
    for life_moment, post_master in paginated_results["items"]:
        download_url = await get_media_urls(post_master)
        shared_to_list = permissions_map.get(life_moment.id, [])
        total_replies = total_replies_map.get(post_master.id, 0)
        
        result = build_post_result(
            item=life_moment,
            post_master=post_master,
            shared_to_list=shared_to_list,
            download_url=download_url,
            user_info= user_info_map.get(life_moment.id, POST_OWNER_IS_REQUESTER) if not is_owner else POST_OWNER_IS_REQUESTER,
        )
        result["total_replies"] = total_replies
        result_list.append(result)
    
    paginated_results["items"] = result_list
    return paginated_results
