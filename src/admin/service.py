from enum import Enum
from sqlalchemy.orm import Session
from sqlalchemy import Integer, and_, case, exists, false, literal, literal_column, null, or_, select, func, desc,asc, true, union_all
from src.personalLifeOverviewChart.models import DescribeYourselfTenSentences, Epitaph, FavoriteHeadshot, LifeInsights, ValueOfLife
from src.secertBase.models import SecretBase
from src.finalChapter.models import Ashes, CeremonyPreference, Coffin, EnduringPowerOfAttorney, Funeral, MedicalPreference, PalliativeCare
from src.posts.models import LifeMoment, LifeTrajectory, MessageToYou, PostMaster, PostSharedRecipients,PostUserPermissions
from src.loggerServices import log_info
from src.pushNotification.service import send_push_notification
from src.auth.models import PhoneMaster, User,UserSettings
from src.pushNotification.models import PushNotification
from src.shareLove.models import FamilyOffice, GoodsDonor, LoveLeftInTheWorld, OrgansDonor, Trust, UserBeneficiaries, UserInheritor, UserTestament
from src.passAway.models import PassAwayInfo,PassAwayInfoMeta
from src.payment.models import Transaction
from src.exceptions import GeneralErrorExcpetion
from src.oss.service import download_single_file
from src.transaction import wrap_update_func
from src.passAway.schemas import (PassAwayInfoMetaBaseInputRequest)
from src.admin.schemas import SendPushNotificationBaseInputRequest, SendPushNotificationToSpecificMemberBaseInputRequest, reqParam
from datetime import datetime
from typing import Any, Dict, List, Literal, Type, Union

class Keys(Enum):
    KEY1 = "death_certificate"
    KEY2 = "id_card_copy"
    KEY3 = "relationship_proof"
    KEY4 = "inheritor_id_proof"
# Query

async def get_push_users_table_trx(db:Session):
        try:
            base_query = db.query(PushNotification.id,User.id.label("user_id"),User.authgear_id,PushNotification.token).join(PushNotification,PushNotification.user_id==User.id)
            
            # ===（total）===
            subquery = base_query.subquery()
            count_query = db.query(func.count()).select_from(subquery)
            total = count_query.scalar()

            result = base_query.all()    
            result_list = [row._asdict() for row in result]
            return {
                "results":result_list,
                "total":total
            }
        except Exception as e:        
                raise GeneralErrorExcpetion(str(e))

async def get_approval_user_table_trx(db:Session):
        try:
            base_query = db.query(PassAwayInfo.id,User.id.label("user_id"),User.authgear_id,PassAwayInfoMeta.approval_status,PhoneMaster.phone_number).join(UserInheritor,UserInheritor.inheritor_user_id==User.id).join(PassAwayInfo,PassAwayInfo.meta_id==UserInheritor.id).join(PassAwayInfoMeta,PassAwayInfoMeta.meta_id==PassAwayInfo.id).join(PhoneMaster,PhoneMaster.id==UserInheritor.inheritor_phone_master_id)
            # ===（total）===
            subquery = base_query.subquery()
            count_query = db.query(func.count()).select_from(subquery)
            total = count_query.scalar()
            result = base_query.all()
            result_list = [row._asdict() for row in result]
            return {
                "results":result_list,
                "total":total
            }
        except Exception as e:        
                raise GeneralErrorExcpetion(str(e))

async def get_approval_user_table_by_id_trx(id:int,db:Session):
        try:
                result = db.query(PassAwayInfo.id,Transaction.payment_status,Transaction.product_id,PassAwayInfoMeta.approval_status,PassAwayInfo.death_certificate,PassAwayInfo.id_card_copy,PassAwayInfo.inheritor_id_proof,PassAwayInfo.relationship_proof,PassAwayInfo.death_time,Transaction.user_id).join(PassAwayInfo,Transaction.id==PassAwayInfo.transaction_id).join(PassAwayInfoMeta,PassAwayInfoMeta.meta_id==PassAwayInfo.id).filter(PassAwayInfo.id==id).all()
                result_list = [row._asdict() for row in result]
                if len(result_list) > 0:
                        # list(map(lambda x: {key: download_single_file(value, 3600) if key in {Keys.KEY1.value, Keys.KEY2.value,Keys.KEY3.value,Keys.KEY4.value} else value for key, value in x.items()}, result_list))
                        for row in result_list:
                                for k in row:
                                        if k in {Keys.KEY1.value, Keys.KEY2.value,Keys.KEY3.value,Keys.KEY4.value}:
                                                r = await download_single_file(row[k],True)
                                                row[k] = r
                else:
                        raise Exception("Not exist")
                return result_list
        except Exception as e:        
                raise GeneralErrorExcpetion(str(e))

async def edit_pass_away_meta_by_admin_trx(pass_away_info_id: int,updates:PassAwayInfoMetaBaseInputRequest,admin_user_id:str, db: Session):
    try:
        
        updates = updates.model_dump()
        merged_dict = {**updates, **{'admin_user_id':admin_user_id}}
        wrap_update_func(PassAwayInfoMeta,{"meta_id":pass_away_info_id},merged_dict,db,True)
        db.commit()   
        return True
    except Exception as e:        
        db.rollback()
        raise GeneralErrorExcpetion(str(e))


async def send_push_notification_all_device_trx(reqData:SendPushNotificationBaseInputRequest,db:Session):
    try:
        reqData = reqData.model_dump()
        # return reqData
        # 1. Each user_id latest push_notification（base on updated_at ASC）
        per_user = (
            select(
                PushNotification.token,
                UserSettings.language,
                PushNotification.user_id,
                PushNotification.updated_at,
                PushNotification.device_uuid,
                func.row_number().over(
                    partition_by=PushNotification.user_id,
                    order_by=desc(PushNotification.updated_at)
                ).label('rn_user')
            )
            .join(UserSettings, UserSettings.user_id == PushNotification.user_id)
            .where(PushNotification.token.isnot(None))
            .cte('per_user')
        )

        # 2. 取出 rn_user = 1 的記錄（每個 user 的最新）
        latest_user = (
            select(per_user.c.token, per_user.c.language, per_user.c.user_id,
                   per_user.c.updated_at, per_user.c.device_uuid)
            .where(per_user.c.rn_user == 1)
            .cte('latest_user')
        )

        # 3. 從 latest_user 中，按 device_uuid 再取最新的（避免同一 device 多筆）
        per_device = (
            select(
                latest_user.c.token,
                latest_user.c.language,
                latest_user.c.user_id,
                latest_user.c.updated_at,
                latest_user.c.device_uuid,
                func.row_number().over(
                    partition_by=latest_user.c.device_uuid,
                    order_by=desc(latest_user.c.updated_at)
                ).label('rn_device')
            )
            .cte('per_device')
        )

        # 4. 最終結果：rn_device = 1，並排序
        final_query = (
            select(
                per_device.c.token,
                per_device.c.language,
                per_device.c.user_id,
                per_device.c.updated_at,
                per_device.c.device_uuid
            )
            .where(per_device.c.rn_device == 1)
            .order_by(per_device.c.device_uuid.asc())
        )

        result = db.execute(final_query).all()
        
        result_list = [row._asdict() for row in result]
        if len(result_list) > 0:
             for row in result_list:
                  language = row['language']
                  for k in row:
                       if k in "token":
                            if language.value == 'en':
                                await send_push_notification(row['token'],reqData['sound'],reqData['en_title'],reqData['en_body'])
                            if language.value == 'zh_hans':    
                                await send_push_notification(row['token'],reqData['sound'],reqData['zh_hans_title'],reqData['zh_hans_body'])
                            if language.value == 'zh_hk':    
                                await send_push_notification(row['token'],reqData['sound'],reqData['zh_hk_title'],reqData['zh_hk_body'])
        else:
            raise Exception('Not Any Token in DB')             
        return True       
    except Exception as e:        
         raise GeneralErrorExcpetion(str(e))



async def send_push_notification_specific_device_trx(reqData:SendPushNotificationToSpecificMemberBaseInputRequest,db:Session):
    try:
        reqData = reqData.model_dump()
        row_id_list = reqData.get('row_id_list')
        
        # 主查詢：JOIN + 過濾最新 + 選取欄位
        result = (
            db.query(PushNotification.token, UserSettings.language)
            .join(UserSettings, UserSettings.user_id == PushNotification.user_id)  # JOIN settings
            .filter(
                PushNotification.id.in_(row_id_list),
                # UserSettings.language.in_(['en', 'zh_hans'])  # 示例
            ).all()
        )
        
        result_list = [row._asdict() for row in result]
        if len(result_list) > 0:
             for row in result_list:
                  language = row['language']
                  for k in row:
                       if k in "token":
                            if language.value == 'en':
                                await send_push_notification(row['token'],reqData['sound'],reqData['en_title'],reqData['en_body'])
                            if language.value == 'zh_hans':    
                                await send_push_notification(row['token'],reqData['sound'],reqData['zh_hans_title'],reqData['zh_hans_body'])
                            if language.value == 'zh_hk':    
                                await send_push_notification(row['token'],reqData['sound'],reqData['zh_hk_title'],reqData['zh_hk_body'])
        else:
            raise Exception('Not Any Token in DB')             
        return True       
    except Exception as e:         
        raise GeneralErrorExcpetion(str(e))


def get_sort_col(sort_field,sort,post_model,post_type_column,custom_sort_map=None):
    sort_order = sort.get("order", "ASC").upper()
    if custom_sort_map is not None:
        sort_col = custom_sort_map.get(sort_field)
        return sort_col,sort_order
    
    default_sort_map = {
            "postMasterID":         post_model.post_master_id,
            "postID":               post_model.id,
            "postUserPermissionID": PostUserPermissions.id,
            "AuthgearID":           User.authgear_id,
            "createdAt":            PostMaster.created_at,
            "eventStartDate":       PostMaster.start_date,
            "postSubType":          post_type_column,
            "numberOfRecipients":   func.count(PostSharedRecipients.id).label("numberOfRecipients"),
    }
    sort_col = default_sort_map.get(sort_field)    
    return sort_col,sort_order

def get_select_item(post_model,post_type_column,custom_select=None):
    if custom_select is not None:
        return custom_select    
    default_select = [
            post_model.post_master_id.label("postMasterID"),
            post_model.id.label("postID"),
            PostUserPermissions.id.label("postUserPermissionID"),
            User.authgear_id.label("authgearID"),
            PostMaster.created_at.label("createdAt"),
            PostMaster.start_date.label("eventStartDate"),
            post_type_column.label("postSubType"),
            func.count(PostSharedRecipients.id).label("numberOfRecipients"),
    ]
    return default_select    

def get_group_by_item(post_model,post_type_column,custom_group_by=None):
    if custom_group_by is not None:
        return custom_group_by
    
    default_group_by = [
            post_model.post_master_id,
            post_model.id,
            PostUserPermissions.id,
            User.authgear_id,
            PostMaster.created_at,
            PostMaster.start_date,
            post_type_column,
    ]
    return default_group_by 

def handle_filter_query(base_query,filt,post_type_column,post_model):
    if authgearID := filt.get("searchAuthgearID"):
        base_query = base_query.filter(User.authgear_id==authgearID) 
    
    if gte := filt.get("createAtStartDate"):
        gte_date = datetime.strptime(gte, "%Y-%m-%d")
        base_query = base_query.filter(PostMaster.created_at >= gte_date)

    if lte := filt.get("createAtEndDate"):
        lte_date = datetime.strptime(lte, "%Y-%m-%d").replace(
            hour=23, minute=59, second=59, microsecond=999999
        )
        base_query = base_query.filter(PostMaster.created_at <= lte_date)
    
    if event_gte := filt.get("eventAtStartDate"):
        gte_date = datetime.strptime(event_gte, "%Y-%m-%d")
        base_query = base_query.filter(PostMaster.start_date >= gte_date)

    if event_lte := filt.get("eventAtEndDate"):
        lte_date = datetime.strptime(event_lte, "%Y-%m-%d").replace(
            hour=23, minute=59, second=59, microsecond=999999
        )
        base_query = base_query.filter(PostMaster.start_date <= lte_date)

    if sub_types := filt.get("postSubType", []):
        conds = []
        for v in sub_types:
            v = str(v).strip().upper()
            if v == "CUSTOM":
                conds.append(post_type_column.is_(None))
            else:
                conds.append(post_type_column == v)
        base_query = base_query.filter(or_(*conds))

    count_recipients = func.count(PostSharedRecipients.id)
    numberOfRecipientsFrom = filt.get("numberOfRecipientsFrom")
    if numberOfRecipientsFrom is not None:
        numberOfRecipientsFrom = int(numberOfRecipientsFrom)    
        base_query = base_query.having(count_recipients >= numberOfRecipientsFrom)
    numberOfRecipientsTo = filt.get("numberOfRecipientsTo")    
    if numberOfRecipientsTo is not None:
        numberOfRecipientsTo = int(numberOfRecipientsTo)
        base_query = base_query.having(count_recipients <= numberOfRecipientsTo)    

    count_posts = func.count(post_model.id)
    numberOfPostSubTypeFrom = filt.get("numberOfPostSubTypeFrom")
    if numberOfPostSubTypeFrom is not None:
        base_query = base_query.having(count_posts >= int(numberOfPostSubTypeFrom))
    numberOfPostSubTypeTo = filt.get("numberOfPostSubTypeTo")    
    if numberOfPostSubTypeTo is not None:
        base_query = base_query.having(count_posts <= int(numberOfPostSubTypeTo))

    count_ai = func.coalesce(func.sum(PostMaster.ai_feedback_count), 0)
    numberOfAIFeedBackSubTypeFrom = filt.get("numberOfAIFeedBackSubTypeFrom")
    if numberOfAIFeedBackSubTypeFrom is not None:
        base_query = base_query.having(count_ai >= int(numberOfAIFeedBackSubTypeFrom))
    numberOfAIFeedBackSubTypeTo = filt.get("numberOfAIFeedBackSubTypeTo")
    if numberOfAIFeedBackSubTypeTo is not None:
        base_query = base_query.having(count_ai <= int(numberOfAIFeedBackSubTypeTo))    

    return base_query  

async def _get_post_table_trx(
    reqData: reqParam,
    db: Session,
    post_source: Literal["LIFE_MOMENT", "LIFE_TRAJECTORY", "MESSAGE_TO_YOU"],
    post_model: Union[Type[LifeMoment], Type[LifeTrajectory], Type[MessageToYou]],
    post_type_column: Any,                # LifeMoment.post_type_code  etc.
    custom_select: List[Any] | None = None,   # optional extra columns
    custom_group_by: List[Any] | None = None, # optional extra columns
    custom_sort_map: Dict[str, Any] | None = None, # optional sort map
) -> Dict[str, Any]:

        req = reqData.model_dump()

        # ---------- Pagination ----------
        pagination = req.get("pagination", {})
        page = pagination.get("page", 1)
        per_page = pagination.get("perPage", 10)
        offset_val = (page - 1) * per_page

        # ---------- Sort ----------
        sort = req.get("sort", {})
        
        # ---------- Filter ----------
        filt = req.get("filter", {})

        # ---- base query (same for every post type) ----
        select_items = get_select_item(post_model,post_type_column,custom_select)
        
        base_query = db.query(*select_items
            ).outerjoin(
                PostUserPermissions,
                and_(
                    PostUserPermissions.shared_post_id == post_model.id,
                    PostUserPermissions.post_source == post_source
                )                  
            ).join(User, User.id == post_model.user_id
            ).outerjoin(
                PostSharedRecipients,
                PostSharedRecipients.permission_id == PostUserPermissions.id
            ).join(PostMaster, PostMaster.id == post_model.post_master_id)
            
        # ---- group_by (must contain every non-aggregated column) ----
        group_items = get_group_by_item(post_model,post_type_column,custom_group_by)
        
        base_query = base_query.group_by(*group_items)

        # ---- filters ----
        base_query = handle_filter_query(base_query,filt,post_type_column,post_model)

        # ---------- 4. Total count ----------
        subq = base_query.subquery()
        total = db.query(func.count()).select_from(subq).scalar()
        total_user = db.query(func.count(func.distinct(subq.c.authgearID))) \
               .select_from(subq) \
               .scalar()
    
        # ---------- 5. Sorting ----------
        sort_field = sort.get("field", "createdAt")
        sort_col,sort_order = get_sort_col(sort_field,sort,post_model,post_type_column,custom_sort_map)
        if sort_field == "numberOfRecipients":
            sort_col = func.count(PostSharedRecipients.id)
        if sort_col is None:
            sort_col = PostMaster.created_at
        
        
        base_query = base_query.order_by(
            asc(sort_col) if sort_order == "ASC" else desc(sort_col)
        )

        # ---------- 6. Pagination ----------
        rows = base_query.offset(offset_val).limit(per_page).all()
        result_list = [row._asdict() for row in rows]

        return {"results": result_list, "total": total,"meta":{"total_user":total_user}}     

async def get_life_moment_table_trx(reqData:reqParam,db:Session):
        try:
            return await _get_post_table_trx(
                reqData,
                db,
                post_source="LIFE_MOMENT",
                post_model=LifeMoment,
                post_type_column=LifeMoment.post_type_code,
            )
        except Exception as e:        
                raise GeneralErrorExcpetion(str(e))



async def get_life_traj_table_trx(reqData:reqParam,db:Session):
        try:
            return await _get_post_table_trx(
                reqData,
                db,
                post_source="LIFE_TRAJECTORY",
                post_model=LifeTrajectory,
                post_type_column=LifeTrajectory.post_type_code,
            )
        except Exception as e:        
                raise GeneralErrorExcpetion(str(e))




async def get_mess_to_you_table_trx(reqData:reqParam,db:Session):
        try:
            return await _get_post_table_trx(
                reqData,
                db,
                post_source="MESSAGE_TO_YOU",
                post_model=MessageToYou,
                post_type_column=MessageToYou.post_type_code,
                custom_select=[
                    MessageToYou.post_master_id.label("postMasterID"),
                    MessageToYou.id.label("postID"),
                    PostUserPermissions.id.label("postUserPermissionID"),
                    User.authgear_id.label("authgearID"),
                    PostMaster.created_at.label("createdAt"),
                    MessageToYou.post_type_code.label("postSubType"),
                    func.count(PostSharedRecipients.id).label("numberOfRecipients"),
                ],                                   
                custom_group_by=[
                    MessageToYou.post_master_id,
                    MessageToYou.id,
                    PostUserPermissions.id,
                    User.authgear_id,
                    PostMaster.created_at,
                    MessageToYou.post_type_code,
                ],
                custom_sort_map={
                    "postMasterID":         MessageToYou.post_master_id,
                    "postID":               MessageToYou.id,
                    "postUserPermissionID": PostUserPermissions.id,
                    "AuthgearID":           User.authgear_id,
                    "createdAt":            PostMaster.created_at,
                    "postSubType":          MessageToYou.post_type_code,
                    "numberOfRecipients":   func.count(PostSharedRecipients.id).label("numberOfRecipients"),
                }
            )
        except Exception as e:        
                raise GeneralErrorExcpetion(str(e))


async def get_user_life_moment_table_trx(reqData: reqParam, db: Session):
    try:
        return await _get_user_post_stat_table_trx(
            reqData=reqData,
            db=db,
            post_model=LifeMoment,
            post_type_column=LifeMoment.post_type_code,
            include_ai_feedback=True,
            custom_select=[
                User.authgear_id.label("authgearID"),
                LifeMoment.post_type_code.label("postSubType"),
                func.count(LifeMoment.id).cast(Integer).label("numberOfPostSubType"),
                func.coalesce(func.sum(PostMaster.ai_feedback_count), 0).cast(Integer).label("numberOfAIFeedBackSubType"),
            ],
            custom_group_by=[
                User.authgear_id, 
                LifeMoment.post_type_code

            ],
            custom_sort_map={
                "authgearID": User.authgear_id,
                "postSubType": LifeMoment.post_type_code,
                "numberOfPostSubType": func.count(LifeMoment.id).cast(Integer).label("numberOfPostSubType"),                 
                "numberOfAIFeedBackSubType": func.coalesce(func.sum(PostMaster.ai_feedback_count), 0)
            },
        )
    except Exception as e:
        raise GeneralErrorExcpetion(str(e))


async def get_user_life_traj_table_trx(reqData: reqParam, db: Session):
    try:
        return await _get_user_post_stat_table_trx(
            reqData=reqData,
            db=db,
            post_model=LifeTrajectory,
            post_type_column=LifeTrajectory.post_type_code,
            include_ai_feedback=False,
            custom_select=[
                User.authgear_id.label("authgearID"),
                LifeTrajectory.post_type_code.label("postSubType"),
                func.count(LifeTrajectory.id).cast(Integer).label("numberOfPostSubType"),
            ],
            custom_group_by=[
                User.authgear_id, 
                LifeTrajectory.post_type_code
            ],
            custom_sort_map={
                "authgearID": User.authgear_id,
                "postSubType": LifeTrajectory.post_type_code,
                "numberOfPostSubType": func.count(LifeTrajectory.id).cast(Integer).label("numberOfPostSubType")                 
            },  
        )
    except Exception as e:
        raise GeneralErrorExcpetion(str(e))


async def get_user_message_to_you_table_trx(reqData: reqParam, db: Session):
    try:
        return await _get_user_post_stat_table_trx(
            reqData=reqData,
            db=db,
            post_model=MessageToYou,
            post_type_column=MessageToYou.post_type_code,
            include_ai_feedback=False,
            custom_select=[
                User.authgear_id.label("authgearID"),
                MessageToYou.post_type_code.label("postSubType"),
                func.count(MessageToYou.id).cast(Integer).label("numberOfPostSubType"),
            ],
            custom_group_by=[
                User.authgear_id, 
                MessageToYou.post_type_code
            ],
            custom_sort_map={
                "authgearID": User.authgear_id,
                "postSubType": MessageToYou.post_type_code,
                "numberOfPostSubType": func.count(MessageToYou.id).cast(Integer).label("numberOfPostSubType")
            },  
        )
    except Exception as e:
        raise GeneralErrorExcpetion(str(e))




async def _get_user_post_stat_table_trx(
    reqData: reqParam,
    db: Session,
    post_model: Union[Type[LifeMoment], Type[LifeTrajectory], Type[MessageToYou]],
    post_type_column: Any,                # LifeMoment.post_type_code  etc.
    include_ai_feedback: bool = False,  # only LifeMoment needs AI feedback count
    custom_select: List[Any] | None = None,   # optional extra columns
    custom_group_by: List[Any] | None = None, # optional extra columns
    custom_sort_map: Dict[str, Any] | None = None, # optional sort map
) -> Dict[str, Any]:

    req = reqData.model_dump()
    filt = req.get("filter", {})
    sort = req.get("sort", {})
    pagination = req.get("pagination", {})

    page = pagination.get("page", 1)
    per_page = pagination.get("perPage", 10)
    offset_val = (page - 1) * per_page

    

    # === SELECT ===
    select_items = get_select_item(post_model,post_type_column,custom_select)

    # === FROM & JOIN ===
    base_query = db.query(*select_items).join(
        post_model, post_model.user_id == User.id
    )
    
    if include_ai_feedback:
        base_query = base_query.join(PostMaster, PostMaster.id == post_model.post_master_id)

    # === group by ===
    group_items = get_group_by_item(post_model,post_type_column,custom_group_by)
    base_query = base_query.group_by(*group_items)

    # === filter ===
    base_query = handle_filter_query(base_query,filt,post_type_column,post_model)

    # === Total ===
    subq = base_query.subquery()
    total = db.query(func.count()).select_from(subq).scalar()
    total_user = db.query(func.count(func.distinct(subq.c.authgearID))) \
               .select_from(subq) \
               .scalar()
    
    # === Sort ===
    sort_field = sort.get("field", "authgearID")

    sort_col,sort_order = get_sort_col(sort_field,sort,post_model,post_type_column,custom_sort_map)
    
    # numberOfPostSubType must to use func count to sort
    if sort_field == "numberOfPostSubType":
        sort_col = func.count(post_model.id)
    # numberOfAIFeedBackSubType must to use func sum to sort    
    if sort_field == "numberOfAIFeedBackSubType":
        sort_col = func.coalesce(func.sum(PostMaster.ai_feedback_count), 0)
    
    if sort_col is None:
        sort_col = User.authgear_id


    base_query = base_query.order_by(asc(sort_col) if sort_order == "ASC" else desc(sort_col))

    # === 分頁 ===
    rows = base_query.offset(offset_val).limit(per_page).all()
    result_list = [row._asdict() for row in rows]

    return {"results": result_list, "total": total,"meta":{"total_user":total_user}}

async def post_and_ai_total_summary_table_trx(db: Session):
    try:
        lm_count = db.scalar(select(func.count(LifeMoment.id)))
        lt_count = db.scalar(select(func.count(LifeTrajectory.id)))
        my_count = db.scalar(select(func.count(MessageToYou.id)))

        
        total_ai_feedback = db.scalar(
            select(func.coalesce(func.sum(PostMaster.ai_feedback_count).cast(Integer), 0))
            .where(PostMaster.id.in_(
                select(LifeMoment.post_master_id).scalar_subquery()
            ))
        ) or 0

        total_posts = (lm_count or 0) + (lt_count or 0) + (my_count or 0)
        results = [{
            "id":0,
            "lifeMomentPostCount": lm_count or 0,
            "lifeTrajectoryPostCount": lt_count or 0,
            "messageToYouPostCount": my_count or 0,
            "totalPosts": total_posts,
            "totalAIFeedback": total_ai_feedback,
        }]
        return {"results": results, "total": 1}
        

        
    except Exception as e:
        raise GeneralErrorExcpetion(str(e))
    

async def user_pre_death_plan_table_trx(reqData: reqParam,db: Session):
    try:
        req = reqData.model_dump()

        # ---------- Pagination ----------
        pagination = req.get("pagination", {})
        page = pagination.get("page", 1)
        per_page = pagination.get("perPage", 24)
        offset_val = (page - 1) * per_page

        # ---------- Sort ----------
        sort = req.get("sort", {})
        # log_info(f"sort: {sort}")
        # ---------- Filter ----------
        filt = req.get("filter", {})
        

        
        u = User.__table__


        
        
        def make_final_chapter_query(model:Union[Type[PalliativeCare], Type[MedicalPreference], Type[EnduringPowerOfAttorney],Type[CeremonyPreference],Type[Coffin],Type[Funeral],Type[Ashes]], type_name):
            stmt = select(
                User.authgear_id,
                literal("final_chapter").label("parent_type"),
                literal_column(f"'{type_name}'").label("type"),
                model.updated_at.label("latest_updateAt"),
                
                case(
                    (model.did_arrange != 'NOT_YET', true()),
                    else_=false()
                ).label("did_arrange")
            ).select_from(
                u.outerjoin(model, User.id == model.user_id)
            )
            return stmt
        
        def make_secret_base_queries():
            queries = []
            stmt = (
                select(
                    User.authgear_id,
                    literal("secret_base").label("parent_type"),
                    null().label("type"),
                    func.max(SecretBase.updated_at).label("latest_updateAt"),
                    (
                        func.coalesce(
                            func.max(
                                case(
                                    (SecretBase.asset_type.in_(
                                        ['BANK_ACCOUNT', 'PROPERTY', 'SAFETY_DEPOSIT_BOX', 'CONFIDENTIAL_EVENT']
                                    ), 1),
                                    else_=0
                                )
                            ),
                            0
                        ) == 1
                    ).label("did_arrange")
                )
                .select_from(User)
                    .outerjoin(SecretBase, SecretBase.user_id == User.id)
                    .group_by(User.authgear_id)
                    .order_by(desc("latest_updateAt"))
            )
            queries.append(stmt)
            return queries
        
        def make_share_love_did_column_queries(model:Union[Type[UserTestament],Type[FamilyOffice],Type[Trust]], type_name, did_column):
            stmt = select(
                User.authgear_id,
                literal("share_love").label("parent_type"),
                literal(type_name).label("type"),
                model.updated_at.label("latest_updateAt"),
                
                case(
                    (model.id.isnot(None), did_column == True),
                    else_=False
                ).label("did_arrange")
            ).select_from(
                u.outerjoin(model, User.id == model.user_id)
            )
            return stmt    
        
        
        def make_share_love_organs_donor_querys():
            organs_stmt = select(
                User.authgear_id,
                literal("share_love").label("parent_type"),
                literal("organs_donor").label("type"),
                OrgansDonor.updated_at.label("latest_updateAt"),
                case(
                    (OrgansDonor.id.isnot(None),
                    OrgansDonor.did_arrange_organ_donor != 'NOT_YET'),
                    else_=False
                ).label("did_arrange")
            ).select_from(
                u.outerjoin(OrgansDonor, User.id == OrgansDonor.user_id)
            )
            return organs_stmt
        
        def make_share_love_without_did_column_queries():
            queries = []

            # 1. user_inheritor
            inheritor_latest_per_user = (
                select(
                    UserInheritor.user_id,
                    func.max(UserInheritor.updated_at).label("latest_updated_at")
                )
                .group_by(UserInheritor.user_id)
                .subquery()
            )
            inheritor_stmt = select(
                    User.authgear_id,
                    literal("share_love").label("parent_type"),
                    literal("inheritor").label("type"),
                    func.coalesce(inheritor_latest_per_user.c.latest_updated_at, literal("-")).label("latest_updateAt"),
                    (inheritor_latest_per_user.c.latest_updated_at.isnot(None)).label("did_arrange")
                ).select_from(User) \
                    .outerjoin(
                    inheritor_latest_per_user,
                    and_(
                        inheritor_latest_per_user.c.user_id == User.id,
                )
            )
            
            queries.append(inheritor_stmt)

            # 2. user_beneficiaries
            beneficiary_latest_per_user = (
                select(
                    UserBeneficiaries.user_id,
                    UserBeneficiaries.beneficiary_type,
                    func.max(UserBeneficiaries.updated_at).label("latest_updated_at")
                )
                .group_by(UserBeneficiaries.user_id, UserBeneficiaries.beneficiary_type)
                .subquery()
            )
            beneficiary_types = [
                ('PHONE', 'beneficiary_phone'),
                ('INSURANCE', 'beneficiary_insurance'),
            ]
            
            for enum_val, type_label in beneficiary_types:
                beneficiary_stmt = select(
                    User.authgear_id,
                    literal("share_love").label("parent_type"),
                    literal(type_label).label("type"),
                    func.coalesce(beneficiary_latest_per_user.c.latest_updated_at, literal("-")).label("latest_updateAt"),
                    (beneficiary_latest_per_user.c.latest_updated_at.isnot(None)).label("did_arrange")
                ).select_from(User) \
                    .outerjoin(
                    beneficiary_latest_per_user,
                    and_(
                        beneficiary_latest_per_user.c.user_id == User.id,
                        beneficiary_latest_per_user.c.beneficiary_type == enum_val
                    )
                )
                
                queries.append(beneficiary_stmt)

            
            
            
            
            
            
            # 3. goods_donor
            goods_latest_per_user = (
                select(
                    GoodsDonor.user_id,
                    func.max(GoodsDonor.updated_at).label("latest_updated_at")
                )
                .group_by(GoodsDonor.user_id)
                .subquery()
            )
            goods_stmt = select(
                    User.authgear_id,
                    literal("share_love").label("parent_type"),
                    literal("goods_donor").label("type"),
                    func.coalesce(goods_latest_per_user.c.latest_updated_at, literal("-")).label("latest_updateAt"),
                    (goods_latest_per_user.c.latest_updated_at.isnot(None)).label("did_arrange")
                ).select_from(User) \
                    .outerjoin(
                    goods_latest_per_user,
                    and_(
                        goods_latest_per_user.c.user_id == User.id,
                )
            )
            
            queries.append(goods_stmt)

            # 4. love_left_in_the_world

            love_latest_per_user = (
                select(
                    LoveLeftInTheWorld.user_id,
                    func.max(LoveLeftInTheWorld.updated_at).label("latest_updated_at")
                )
                .group_by(LoveLeftInTheWorld.user_id)
                .subquery()
            )
            love_stmt = select(
                    User.authgear_id,
                    literal("share_love").label("parent_type"),
                    literal("love_left_in_the_world").label("type"),
                    func.coalesce(love_latest_per_user.c.latest_updated_at, literal("-")).label("latest_updateAt"),
                    (love_latest_per_user.c.latest_updated_at.isnot(None)).label("did_arrange")
                ).select_from(User) \
                    .outerjoin(
                    love_latest_per_user,
                    and_(
                        love_latest_per_user.c.user_id == User.id,
                )
            )
            
            queries.append(love_stmt)
            return queries
        
        
             
        def make_message_to_you_queries():
            queries = []
            message_to_you_latest_per_user = (
                select(
                    MessageToYou.user_id,
                    MessageToYou.post_type_code,
                    func.max(MessageToYou.updated_at).label("latest_updated_at")
                )
                .group_by(MessageToYou.user_id, MessageToYou.post_type_code)
                .subquery()
            )
            message_to_you_types = [
                ('THANKS_TO_YOU', 'thanks_to_you'),
                ('SORRY', 'sorry'),
                ('HAVE_SOMETHING_TO_TELL_YOU', 'have_something_to_tell_you'),
                ('GRATEFUL_FOR_YOU', 'grateful_for_you'),
                
            ]
            
            for enum_val, type_label in message_to_you_types:

                message_to_you_stmt = select(
                    User.authgear_id,
                    literal("message_to_you").label("parent_type"),
                    literal(type_label).label("type"),
                    func.coalesce(message_to_you_latest_per_user.c.latest_updated_at, literal("-")).label("latest_updateAt"),
                    (message_to_you_latest_per_user.c.latest_updated_at.isnot(None)).label("did_arrange")
                ).select_from(User) \
                    .outerjoin(
                    message_to_you_latest_per_user,
                    and_(
                        message_to_you_latest_per_user.c.user_id == User.id,
                        message_to_you_latest_per_user.c.post_type_code == enum_val
                    )
                )
                
                queries.append(message_to_you_stmt)
            return queries



        

        # final chapter query
        queries = [
            make_final_chapter_query(PalliativeCare, "palliative_care"),
            make_final_chapter_query(MedicalPreference, "medical_preference"),
            make_final_chapter_query(EnduringPowerOfAttorney, "enduring_power_of_attorney"),
            make_final_chapter_query(CeremonyPreference, "ceremony_preference"),
            make_final_chapter_query(Coffin, "coffin"),
            make_final_chapter_query(Funeral, "funeral"),
            make_final_chapter_query(Ashes, "ashes"),
        ]
        # secret_base query
        queries.extend(make_secret_base_queries())

        # share_love query
        queries.extend([
            make_share_love_did_column_queries(UserTestament, "testament", UserTestament.did_testament),
            make_share_love_did_column_queries(FamilyOffice, "family_office", FamilyOffice.did_family_office),
            make_share_love_did_column_queries(Trust, "trust", Trust.did_trust),
            make_share_love_organs_donor_querys(),
        ])
        queries.extend(make_share_love_without_did_column_queries())

        # message_to_you query
        queries.extend(make_message_to_you_queries())

        
        # UNION ALL query
        union_all_stmt = union_all(*queries)
        union_subq = union_all_stmt.subquery()

        
        # === Sort ===
        sort_field = sort.get("field", "authgearID")

        sort_map = {
            "authgearID":        union_subq.c.authgear_id,
            "lifePlanningType":  union_subq.c.parent_type,
            "lifePlanningSubType":union_subq.c.type,
            "didArrange":        union_subq.c.did_arrange,
            "latestUpdateAt":    union_subq.c.latest_updateAt,
        }
        sort_col = sort_map.get(sort_field)
        if sort_col is None:
            sort_col = union_subq.c.authgear_id
        sort_order = sort.get("order", "ASC").upper()
        order_column = asc(sort_col) if sort_order == "ASC" else desc(sort_col)
        
        base_query = select(union_subq)
        # === Filter ===
        # log_info(f"filter: {filt}")
        if authgearID := filt.get("searchAuthgearID"):
            base_query = base_query.filter(union_subq.c.authgear_id == authgearID)
        if lifePlanningSubType := filt.get("lifePlanningSubType"):
            conds = []
            for v in lifePlanningSubType:
                v = str(v).strip().upper()
                if v == "SECRET_BASE":
                    conds.append(union_subq.c.parent_type == "secret_base")
                else:    
                    conds.append(union_subq.c.type == v)
            base_query = base_query.filter(or_(*conds))
        if didArrange := filt.get("didArrange"):
            base_query = base_query.filter(union_subq.c.did_arrange.in_(didArrange))

        if latestUpdate_gte := filt.get("latestUpdateAtFrom"):
            gte_datetime = datetime.strptime(latestUpdate_gte, "%Y-%m-%d %H:%M:%S")
            base_query = base_query.filter(union_subq.c.latest_updateAt >= gte_datetime)

        if latestUpdate_lte := filt.get("latestUpdateAtTo"):
            lte_datetime = datetime.strptime(latestUpdate_lte, "%Y-%m-%d %H:%M:%S")
            base_query = base_query.filter(union_subq.c.latest_updateAt <= lte_datetime)

        subq = base_query.subquery()
        total = db.query(func.count()).select_from(subq).scalar()
        total_user = db.query(func.count(func.distinct(subq.c.authgear_id))) \
               .select_from(subq) \
               .scalar()
        # === Pagination ===
        
        final_query = (
            base_query
            .order_by(
                order_column,
                union_subq.c.authgear_id,
                union_subq.c.parent_type,
                union_subq.c.type,
                union_subq.c.latest_updateAt
            )
            .offset(offset_val)
            .limit(per_page)
        )

        result = db.execute(final_query)
        rows = result.fetchall()
        # log_info(rows)
        results = [
            {
                "authgearID": row.authgear_id,
                "lifePlanningType":row.parent_type or "", 
                "lifePlanningSubType": row.type or "-",
                "didArrange": bool(row.did_arrange),
                "latestUpdateAt": row.latest_updateAt or "-",
            }
            for row in rows
        ]
        return {"results": results, "total": total,"meta":{"total_user":total_user}}
        

        
    except Exception as e:
        raise GeneralErrorExcpetion(str(e))    

async def user_life_overview_chart_table_trx(reqData: reqParam, db: Session):
    try:
        req = reqData.model_dump()

        # ---------- Pagination ----------
        pagination = req.get("pagination", {})
        page = pagination.get("page", 1)
        per_page = pagination.get("perPage", 10)
        offset_val = (page - 1) * per_page

        # ---------- Sort ----------
        sort = req.get("sort", {})
        # log_info(f"sort: {sort}")
        # ---------- Filter ----------
        filt = req.get("filter", {})

        u = User.__table__

        def make_life_summary_query(model:Union[Type[DescribeYourselfTenSentences],Type[ValueOfLife],Type[LifeInsights],Type[Epitaph],Type[FavoriteHeadshot]],key:str):
            # life summary query statment
            return (
                select(
                    User.authgear_id.label("authgear_id"),
                    literal(key).label("life_summary_type"),
                    func.coalesce(func.count(model.id), 0).label("number_of_did"),
                    func.max(model.updated_at).label("latest_update_at")
                )
                .select_from(u.outerjoin(model, User.id == model.user_id))
                .group_by(User.authgear_id)
            )
        
        queries = [
            make_life_summary_query(DescribeYourselfTenSentences, "describe_yourself_ten_sentences"),
            make_life_summary_query(ValueOfLife, "value_of_life"),
            make_life_summary_query(LifeInsights, "life_insights"),
            make_life_summary_query(Epitaph, "epitaph"),
            make_life_summary_query(FavoriteHeadshot, "favorite_headshot"),
        ]
        # UNION ALL query
        union_all_stmt = union_all(*queries)
        union_subq = union_all_stmt.subquery()
        # === Sort ===
        sort_field = sort.get("field", "authgearID")

        sort_map = {
            "authgearID":       union_subq.c.authgear_id,
            "lifeSummaryType":  union_subq.c.life_summary_type,
            "NumberOfDid":      union_subq.c.number_of_did,
            "latestUpdateAt":   union_subq.c.latest_update_at,
        }
        sort_col = sort_map.get(sort_field)
        if sort_col is None:
            sort_col = union_subq.c.authgear_id
        sort_order = sort.get("order", "ASC").upper()
        order_column = asc(sort_col) if sort_order == "ASC" else desc(sort_col)
        
        base_query = select(union_subq)
        # === Filter ===
        # log_info(f"filter: {filt}")
        if authgearID := filt.get("searchAuthgearID"):
            base_query = base_query.filter(union_subq.c.authgear_id == authgearID)
        if lifeSummaryType := filt.get("lifeSummaryType"):
            conds = []
            for v in lifeSummaryType:
                v = str(v).strip().upper()
                conds.append(union_subq.c.life_summary_type == v)
            base_query = base_query.filter(or_(*conds))
        numberOfDidFrom = filt.get("numberOfDidFrom")
        if numberOfDidFrom is not None:
            base_query = base_query.filter(union_subq.c.number_of_did >= numberOfDidFrom)
        numberOfDidTo = filt.get("numberOfDidTo")
        if numberOfDidTo is not None:
            base_query = base_query.filter(union_subq.c.number_of_did <= numberOfDidTo)
        if latestUpdate_gte := filt.get("latestUpdateAtFrom"):
            gte_datetime = datetime.strptime(latestUpdate_gte, "%Y-%m-%d %H:%M:%S")
            base_query = base_query.filter(union_subq.c.latest_update_at >= gte_datetime)
        if latestUpdate_lte := filt.get("latestUpdateAtTo"):
            lte_datetime = datetime.strptime(latestUpdate_lte, "%Y-%m-%d %H:%M:%S")
            base_query = base_query.filter(union_subq.c.latest_update_at <= lte_datetime)

        subq = base_query.subquery()
        total = db.query(func.count()).select_from(subq).scalar()
        total_user = db.query(func.count(func.distinct(subq.c.authgear_id))) \
               .select_from(subq) \
               .scalar()
        
        # === Pagination ===
        
        final_query = (
            base_query
            .order_by(
                order_column,
                union_subq.c.authgear_id,
                union_subq.c.life_summary_type,
                union_subq.c.number_of_did,
                union_subq.c.latest_update_at
            )
            .offset(offset_val)
            .limit(per_page)
        )

        result = db.execute(final_query)
        rows = result.fetchall()
        
        results = [
            {
                "authgearID": row.authgear_id,
                "lifeSummaryType":row.life_summary_type, 
                "NumberOfDid": row.number_of_did,
                "latestUpdateAt": row.latest_update_at or "-",
            }
            for row in rows
        ]
        return {"results": results, "total": total, "meta":{'total_user':total_user}}
        
    except Exception as e:
        raise GeneralErrorExcpetion(str(e))    

async def user_storage_usage_table_trx(reqData: reqParam,db: Session):
    try:
        req = reqData.model_dump()

        # ---------- Pagination ----------
        pagination = req.get("pagination", {})
        page = pagination.get("page", 1)
        per_page = pagination.get("perPage", 10)
        offset_val = (page - 1) * per_page

        # ---------- Sort ----------
        sort = req.get("sort", {})
        # log_info(f"sort: {sort}")
        # ---------- Filter ----------
        filt = req.get("filter", {})

        
        text_bytes_expr = (
            func.sum(
                func.coalesce(func.length(PostMaster.title), 0) +
                func.coalesce(func.length(PostMaster.content), 0) +
                func.coalesce(func.length(PostMaster.start_date), 0) +
                func.coalesce(func.length(PostMaster.end_date), 0) +
                func.coalesce(func.length(PostMaster.motion_rate), 0) +
                func.coalesce(func.length(PostMaster.images_name), 0) +
                func.coalesce(func.length(PostMaster.videos_name), 0) +
                func.coalesce(func.length(PostMaster.voices_name), 0) +
                func.coalesce(func.length(PostMaster.created_at), 0) +
                func.coalesce(func.length(PostMaster.updated_at), 0) +
                func.coalesce(func.length(PostMaster.ai_feedback_content), 0) +
                func.coalesce(func.length(PostMaster.ai_feedback_status), 0) +
                func.coalesce(func.length(PostMaster.ai_feedback_count), 0) +
                func.coalesce(func.length(PostMaster.ai_feedback_hotline), 0) +
                func.coalesce(func.length(PostMaster.ai_feedback_lang), 0) +
                func.coalesce(func.length(LifeMoment.post_master_id), 0) +
                func.coalesce(func.length(LifeMoment.user_id), 0) +
                func.coalesce(func.length(LifeMoment.weather), 0) +
                func.coalesce(func.length(LifeMoment.participants), 0) +
                func.coalesce(func.length(LifeMoment.post_type_code), 0) +
                func.coalesce(func.length(LifeMoment.custom_post_type_id), 0) +
                func.coalesce(func.length(LifeMoment.restaurant_name), 0) +
                func.coalesce(func.length(LifeMoment.food_name), 0) +
                func.coalesce(func.length(LifeMoment.academic_work_interest), 0) +
                func.coalesce(func.length(LifeMoment.school_score), 0) +
                func.coalesce(func.length(LifeMoment.age), 0) +
                func.coalesce(func.length(LifeMoment.location), 0) +
                func.coalesce(func.length(LifeMoment.created_at), 0) +
                func.coalesce(func.length(LifeMoment.updated_at), 0) +
                func.coalesce(func.length(LifeTrajectory.post_master_id), 0) +
                func.coalesce(func.length(LifeTrajectory.user_id), 0) +
                func.coalesce(func.length(LifeTrajectory.post_type_code), 0) +
                func.coalesce(func.length(LifeTrajectory.custom_post_type_id), 0) +
                func.coalesce(func.length(LifeTrajectory.age), 0) +
                func.coalesce(func.length(MessageToYou.post_master_id), 0) +
                func.coalesce(func.length(MessageToYou.user_id), 0) +
                func.coalesce(func.length(MessageToYou.post_type_code), 0) +
                func.coalesce(func.length(MessageToYou.when_can_read_the_post), 0)
            )
            .label("text_bytes")
        )
        
        query = (
            select(
                User.id,
                User.authgear_id,
                text_bytes_expr
            )
            .select_from(User)
            .outerjoin(LifeMoment, User.id == LifeMoment.user_id)
            .outerjoin(LifeTrajectory, User.id == LifeTrajectory.user_id)
            .outerjoin(MessageToYou, User.id == MessageToYou.user_id)
            .outerjoin(PostMaster, or_(
                PostMaster.id == LifeMoment.post_master_id,
                PostMaster.id == LifeTrajectory.post_master_id,
                PostMaster.id == MessageToYou.post_master_id,
            ))
            .group_by(User.id, User.authgear_id)
        )

        
        
        if search_id := filt.get("searchAuthgearID"):
            query = query.filter(User.authgear_id == search_id)

        textGigaBytesFrom = filt.get("textGigaBytesFrom")
        if textGigaBytesFrom is not None:
            textBytesFrom = float(textGigaBytesFrom) * 1024**3
            query = query.having(text_bytes_expr >= textBytesFrom)

        textGigaBytesTo = filt.get("textGigaBytesTo")
        if textGigaBytesTo is not None:
            textBytesTo = float(textGigaBytesTo) * 1024**3
            query = query.having(text_bytes_expr <= textBytesTo)

        sort_field = sort.get("field", "authgearID")
        sort_order = sort.get("order", "ASC").upper()

        sort_map = {
            "userID": User.id,
            "authgearID": User.authgear_id,
            "textBytes": text_bytes_expr,
        }
        order_col = sort_map.get(sort_field, User.authgear_id)
        if sort_order == "DESC":
            order_col = desc(order_col)
        
        query = query.order_by(order_col)

        
        count_query = select(func.count()).select_from(query.subquery())
        total = db.execute(count_query).scalar() or 0
        total_user = db.query(func.count(func.distinct(query.c.authgear_id))) \
               .select_from(query) \
               .scalar()
        
        # === Pagination ===
        query = query.offset(offset_val).limit(per_page)
        result = db.execute(query)
        rows = result.fetchall()
        # log_info(rows)
        final_results = []
        for row in rows:
            user_id = row.id
            authgear_id = row.authgear_id
            text_bytes = int(row.text_bytes or 0)
            text_gb = round(text_bytes / (1024 * 1024 * 1024), 4)
            # oss_gb = user_storage_usage_oss(f'{user_id}/')
            final_results.append({
                "authgearID": authgear_id,
                "textGigaBytes": text_gb,           # 数据库文本占用
                "imageGigaBytes": "-",             # OSS 文件占用（图片、视频等）
                "totalGigaBytes": text_gb,
            })
            
        
        return {"results": final_results, "total": total, "meta":{'total_user':total_user}}    
    except Exception as e:
        raise GeneralErrorExcpetion(str(e))    