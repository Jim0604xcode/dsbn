import aiohttp
from sqlalchemy.orm import Session
from sqlalchemy import select, func, desc
from typing import List, Dict
from src.exceptions import GeneralErrorExcpetion
from src.authgear.adminApi import query_user_by_authgear_id
from src.auth.models import LanguageEnum, UserSettings, User
from src.posts.models import (
    PostsPermissionsGroupMembers,
    PostPermissionsGroups,
    PostSourceEnum,
    LifeMoment,
    LifeTrajectory,
    MessageToYou,
)
from src.replies.models import RepliesMaster
from src.loggerServices import log_error
from src.pushNotification.models import PushNotification
from src.pushNotification.schemas import PushNotificationBaseInputRequest
from src.transaction import wrap_insert_mapping_func, wrap_update_func
from src.loggerServices import log_info
from src.config import CLOUD_MESSAGING_API_ENDPOINT
import asyncio
from concurrent.futures import ThreadPoolExecutor


def run_async(coroutine):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coroutine)
    finally:
        loop.close()


def _build_post_preview(text: str, max_length: int = 20) -> str:
    """
    Build a preview of the post content based on the text.
    The preview is a string of at most max_length characters,
    which is the first max_length characters of the text.
    If the text is longer than max_length, the preview will be truncated.
    """
    if not text:
        return ""
    text = text.strip()
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."




# Query

async def get_push_notification_trx(fl: List,db:Session):
        result = db.query(PushNotification.device_uuid,PushNotification.token).filter(*fl).all()
        result_list = [row._asdict() for row in result]
        return result_list[0] if result_list else {}
        


    

# Insert / Edit
             
async def register_push_notification_token_trx(reqData: PushNotificationBaseInputRequest,user_id: str, db: Session):
    try:
        device_uuid = reqData.device_uuid
        fl:List = [PushNotification.user_id == user_id,PushNotification.device_uuid == device_uuid]
        
        user = db.query(PushNotification).filter(*fl).first()
        log_info(f"register_push_notification_token_trx user: {user}")
        if not user:
            log_info(f"not exist user")
            insert_obj = PushNotification(**reqData.model_dump(),user_id=user_id)
            
            res = wrap_insert_mapping_func(db, insert_obj)
            db.commit()
            return res.id
        else:
            log_info(f"exist user")
            updates = reqData.model_dump(include={"token"})
            wrap_update_func(PushNotification,{"user_id":user_id,"device_uuid":device_uuid},updates,db,True)
            db.commit()
            return user.id
    except Exception as e:
        db.rollback()
        raise GeneralErrorExcpetion(str(e))            


async def send_push_by_create_reply(reply_master_id: int, post_source, shared_post_id: int, replier_user_id: str, db: Session, parent_reply_master_id: int = None):
    """
    Send push notification when a reply is created
    """
    # Get the post owner
    if post_source == PostSourceEnum.LIFE_MOMENT:
        post = db.query(LifeMoment).filter(LifeMoment.id == shared_post_id).first()
    elif post_source == PostSourceEnum.LIFE_TRAJECTORY:
        post = db.query(LifeTrajectory).filter(LifeTrajectory.id == shared_post_id).first()
    elif post_source == PostSourceEnum.MESSAGE_TO_YOU:
        post = db.query(MessageToYou).filter(MessageToYou.id == shared_post_id).first()
    else:
        return
    
    if not post:
        return
    
    post_owner_id = post.user_id
    
    # Don't send notification if replier is the post owner
    # if replier_user_id == post_owner_id:
    #     return
    
    # Get reply details
    reply = db.query(RepliesMaster).filter(RepliesMaster.id == reply_master_id).first()
    if not reply:
        return
    
    # Determine recipients based on parent_reply_master_id
    if parent_reply_master_id:
        # If replying to another reply, notify the owner of that reply
        parent_reply = db.query(RepliesMaster).filter(RepliesMaster.id == parent_reply_master_id).first()
        if parent_reply:
            recipients = [parent_reply.user_id, post_owner_id]
        else:
            recipients = [post_owner_id]
    else:
        # If replying directly to post, notify the post owner
        recipients = [post_owner_id]
    
    # Remove replier from recipients to avoid self-notification
    recipients = [user_id for user_id in recipients if user_id != replier_user_id]
    recipients = list(set(recipients))
    
    if not recipients:
        return
    
    # Get user tokens and language preferences
    user_info_list = queryUserTokenAndLanguage(recipients, db)
    
    # Get replier's name
    replier_name = ""
    authgear_user = db.query(User).filter(User.id == replier_user_id).first()
    
    if authgear_user and authgear_user.authgear_id:
        try:
            from src.auth.service import get_users_info_with_cache
            users_info = await get_users_info_with_cache([authgear_user.authgear_id])
            if authgear_user.authgear_id in users_info:
                attrs = users_info[authgear_user.authgear_id].get('standardAttributes', {})
                if 'family_name' in attrs:
                    replier_name = attrs['family_name']
        except Exception as e:
            log_error(f"Error getting replier name: {str(e)}")
    
    # Prepare payload
    payload = {
        'reply_master_id': reply_master_id,
        'parent_reply_master_id': parent_reply_master_id,
        'post_master_id': getattr(post, 'post_master_id', None),
        'post_id': shared_post_id,
        'post_source': post_source.value,
        'post_type_code': getattr(post, 'post_type_code', None),
        'shared_with_me': post_owner_id == replier_user_id,
        'intent': 'OPEN_POST'
    }
    
    # Send notifications
    with ThreadPoolExecutor() as executor:
        for user in user_info_list:
            if user["token"]:
                is_reply_to_reply = reply.parent_reply_master_id is not None
                lang = user["language"]
                reply_preview = _build_post_preview(reply.content)
                
                if lang == LanguageEnum.en.value:
                    if is_reply_to_reply:
                        title = "New Reply to Comment"
                        body = f"{replier_name or 'Someone'} replied to a comment"
                    else:
                        title = "New Reply to Post"
                        body = f"{replier_name or 'Someone'} replied to your post"
                    if reply_preview:
                        body = f"{body}: {reply_preview}"
                elif lang == LanguageEnum.zh_hans.value:
                    if is_reply_to_reply:
                        title = "新回复评论"
                        body = f"{replier_name or '某人'} 回复了评论"
                    else:
                        title = "新回复贴文"
                        body = f"{replier_name or '某人'} 回复了你的贴文"
                    if reply_preview:
                        body = f"{body}: {reply_preview}"
                else:  # zh_hk
                    if is_reply_to_reply:
                        title = "新回覆評論"
                        body = f"{replier_name or '某人'} 回覆了評論"
                    else:
                        title = "新回覆貼文"
                        body = f"{replier_name or '某人'} 回覆了你的貼文"
                    if reply_preview:
                        body = f"{body}: {reply_preview}"
                
                executor.submit(run_async, send_push_notification(
                    user["token"], 'default', title, body, payload
                ))

def send_push_by_create_post(
    user_id: str,
    post_master_id: int,
    post_id,
    permission_group_row_ids: List[int],
    db: Session,
    post_type_code: str = None,
    post_source=None,
    post_title: str = None,
    post_content: str = None,
):
    
    # log_info(f"send_push_by_create_post_59: {permission_group_row_ids}")
    payload = {
        'post_master_id':post_master_id,
        'post_id':post_id,
        'post_source':post_source.value if post_source else None,
        'intent':'OPEN_POST',
        'post_type_code':post_type_code,
        'shared_with_me':True # for new post, always true
    }
    user_ids = get_unique_user_ids_by_permission_group_ids(permission_group_row_ids, db)
    # log_info(f"send_push_by_create_post_63: {user_ids}")
    # 輸出示例：
    # [
    #     "user_id1",
    #     "user_id2",
    #     "user_id3"
    # ]
    if user_ids:
        # Query all tokens and languages in one go
        user_info_list = queryUserTokenAndLanguage(user_ids, db)
        # 輸出示例：
        # [
        #     {"user_id": "user_id1","language": "l1", "token": "t1"},
        #     {"user_id": "user_id2","language": "l2", "token": "t2"},
        #     {"user_id": "user_id3","language": "l3", "token": "t3"},
        # ]
        # log_info(f"send_push_by_create_post_82: {user_info_list}")
        authgearID = db.query(User).filter(User.id == user_id).first()
        sender_name = ""
        family_name = ""
        
        if authgearID:   
            # 獲取當前事件循環
            with ThreadPoolExecutor() as executor:

                res = executor.submit(run_async, query_user_by_authgear_id(authgearID.authgear_id)).result()

            
            if res and len(res) > 0 and res[0].get('node') and res[0]['node'].get('standardAttributes') and 'family_name' in res[0]['node']['standardAttributes']:    
                family_name = res[0]['node']['standardAttributes']['family_name']    
                
            
            sender_name = f"{family_name}"

        source_text = (post_title or "").strip() or (post_content or "").strip()
        post_preview = _build_post_preview(source_text)

        log_info(f'user_info_list------>{user_info_list}')
        with ThreadPoolExecutor() as executor:  # 確保 ThreadPoolExecutor 用於推送通知
            for user in user_info_list:
                if user["token"]:
                    lang = user["language"]
                    if lang == LanguageEnum.en.value:
                        title = "New Post Shared"
                        if sender_name == "":
                            sender_name = "Someone"
                        body = f"{sender_name} has shared a new post with you."
                        if post_preview:
                            body = f"{body} {post_preview}"
                    elif lang == LanguageEnum.zh_hans.value:
                        title = "新贴文分享"
                        if sender_name == "":
                            sender_name = "某人"
                        body = f"{sender_name} 分享了一则新贴文给你"
                        if post_preview:
                            body = f"{body}：{post_preview}"
                    elif lang == LanguageEnum.zh_hk.value:
                        title = "新貼文分享"
                        if sender_name == "":
                            sender_name = "某人"
                        body = f"{sender_name} 分享了一則新貼文給你"
                        if post_preview:
                            body = f"{body}：{post_preview}"

                    # 使用 ThreadPoolExecutor 運行異步的 send_push_notification
                    executor.submit(
                        run_async,
                        send_push_notification(
                            user["token"], 'default', title, body, payload
                        ),
                    )
                

def notify_user_fd_already_registered(posts_permissions_group_members_row_ids:List[int], db: Session):
    log_info(f'posts_permissions_group_members_row_ids: {posts_permissions_group_members_row_ids}')
    formatted_result = get_group_members_info(posts_permissions_group_members_row_ids,db)
    log_info(f'formatted_result: {formatted_result}')
    # Example：
    # [
    #     {
    #     "user_id": userId1, 
    #     "first_name":"Jim",
    #     "last_name":"Chan"
    #    },
    #     {
    #     "user_id": userId2,
    #     "first_name":"John",
    #     "last_name":"Li"
    #    },
    # ]
    if formatted_result:
        sender_user_ids = [item["user_id"] for item in formatted_result if item["user_id"]]
        # Query all tokens and languages in one go
        user_token_language = queryUserTokenAndLanguage(sender_user_ids, db)
        # Example：
        # [
        # {"user_id": "userId1", "language": "l1", "token": "t1"},
        # {"user_id": "userId2", "language": "l2", "token": "t2"},
        # {"user_id": "userId1", "language": "l3", "token": "t3"},
        # ]
        log_info(f"user_token_language: {user_token_language}")
        user_lookup = {user["user_id"]: user for user in formatted_result}
        combined_result = []
        for token_entry in user_token_language:
            user_id = token_entry["user_id"]
            if user_id in user_lookup:
                combined_entry = {
                "user_id": user_id,
                "first_name": user_lookup[user_id]["first_name"],
                "last_name": user_lookup[user_id]["last_name"],
                "language": token_entry["language"],
                "token": token_entry["token"]
                }
                combined_result.append(combined_entry)
        log_info(f"combined_result: {combined_result}")

        
        with ThreadPoolExecutor() as executor:  # 確保 ThreadPoolExecutor 用於推送通知
            for user in combined_result:
                if user["token"]:
                    if user["language"] == LanguageEnum.en.value:
                        title = f"Your Friend Has Registered!"
                        body = f"{user["first_name"]} {user["last_name"]} has registered."
                    elif user["language"] == LanguageEnum.zh_hans.value:
                        title = "朋友注册通知！"
                        body = f"{user["first_name"]} {user["last_name"]} 已注册"
                    elif user["language"] == LanguageEnum.zh_hk.value:
                        title = "朋友註冊通知！"
                        body = f"{user["first_name"]} {user["last_name"]} 已註冊"
                    

                    log_info(f"notifyUserFdAlreadyRegistered ready to sent push: token={user["token"]}")
                    # 使用 ThreadPoolExecutor 運行異步的 send_push_notification
                    executor.submit(run_async, send_push_notification(
                            user["token"], 'default', title, body
                    ))
                    print(f"send_push_notification: {user['token']} {title} {body}")


def get_group_members_info(posts_permissions_group_members_row_ids:List[int], db: Session)->List[Dict[str, str]]:
    result = (
        db.query(
            func.max(PostsPermissionsGroupMembers.first_name).label("first_name"),
            func.max(PostsPermissionsGroupMembers.last_name).label("last_name"),
            PostPermissionsGroups.create_by.label("create_by"),
        )
        .outerjoin(
            PostPermissionsGroups,
            PostsPermissionsGroupMembers.group_id == PostPermissionsGroups.id
        )
        .filter(PostsPermissionsGroupMembers.id.in_(posts_permissions_group_members_row_ids))
        .group_by(PostPermissionsGroups.create_by)
        .all()
    )
    # Convert query results to specified format
    formatted_result = [
        {
            "user_id": row.create_by,
            "first_name": row.first_name,
            "last_name": row.last_name
        }
        for row in result
    ]
    # Example：
    # [
    #     {
    #     "user_id": userId1, 
    #     "first_name":"Jim",
    #     "last_name":"Chan"
    #.    },
    #     {
    #     "user_id": userId2,
    #     "first_name":"John",
    #     "last_name":"Li"
    #.    },
    # ]
    return formatted_result
    
def get_unique_user_ids_by_permission_group_ids(permission_group_row_ids:List[int], db: Session) -> List[Dict[str, str]]:
    result = (
        db.query(PostsPermissionsGroupMembers.user_id)
        .filter(PostsPermissionsGroupMembers.id.in_(permission_group_row_ids))
        .distinct()
        .all()
    )
    return [user_id for user_id, in result]  # 解包元組，直接返回字串列表

def queryUserTokenAndLanguage(user_ids: List[str], db: Session):
    """
    依指定的 user_ids 取得：
      1. 每個 user 的最新 push_notification（updated_at 降冪）
      2. 再按 device_uuid 取最新一筆
      3. 回傳 (user_id, language, token)
    """

    # -------------------------------
    # 1. 每個 user 的最新一筆 push_notification
    # -------------------------------
    latest_per_user = (
        select(
            PushNotification.user_id,
            PushNotification.token,
            PushNotification.device_uuid,
            PushNotification.updated_at,
            UserSettings.language,
            func.row_number().over(
                partition_by=PushNotification.user_id,
                order_by=desc(PushNotification.updated_at)
            ).label('rn_user')
        )
        .join(UserSettings, UserSettings.user_id == PushNotification.user_id)
        .where(
            PushNotification.user_id.in_(user_ids),   # 關鍵：只查這些 user
            PushNotification.token.isnot(None)        # 確保 token 存在
        )
        .cte('per_user')
    )

    # -------------------------------
    # 2. 從上面結果中，每個 device_uuid 再取最新一筆
    # -------------------------------
    latest_per_device = (
        select(
            latest_per_user.c.user_id,
            latest_per_user.c.token,
            latest_per_user.c.device_uuid,
            latest_per_user.c.language,
            func.row_number().over(
                partition_by=latest_per_user.c.device_uuid,
                order_by=desc(latest_per_user.c.updated_at)
            ).label("rn_device")
        )
        .where(latest_per_user.c.rn_user == 1)
        .cte('latest_user')
    )

    # -------------------------------
    # 4. 最終結果
    # -------------------------------
    final_query = (
        select(
            latest_per_device.c.user_id,
            latest_per_device.c.language,
            latest_per_device.c.token
        )
        .where(latest_per_device.c.rn_device == 1)
        .order_by(latest_per_device.c.device_uuid.asc())
    )

    # 執行查詢
    result = db.execute(final_query).all()
    
    return [
        {
            "user_id": user_id,
            "language": language.value if language else 'zh_hk',
            "token": token if token else None
        }
        for user_id, language, token in result
    ]

async def send_push_notification(token:str,sound:str,title:str,body:str,data:Dict=None):
    
    
    payload = {
        "to": token,
        "sound": sound,
        "title": title,
        "body": body,
        "data": data if data else {},
        "channelId":"default"  # 必须与前端渠道 ID 匹配
    }
    
    
    async with aiohttp.ClientSession() as session:
        async with session.post(CLOUD_MESSAGING_API_ENDPOINT, json=payload) as response:
            if response.status == 200:
                # Log the token and response status
                log_info(f"Push notification sent successfully: token={token}")
            if response.status != 200:
                raise GeneralErrorExcpetion(f"Failed to send push notification: {response.status}")
