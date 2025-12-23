from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import or_
from src.shareLove.utils import build_inheritor_ulink, create_inheritor_jwt, get_sender_name_by_user_id
from src.pushNotification.service import queryUserTokenAndLanguage, send_push_notification
from src.exceptions import GeneralErrorExcpetion
from src.shareLove.schemas import (FamilyOfficeBaseInputRequest, PhoneBeneficiariesBaseInputRequest,InsuranceBeneficiariesBaseInputRequest, ReSendSMSBaseInputRequest, TrustBaseInputRequest, UserInheritorBaseInputRequest, UserInheritorMetaBaseInputRequest, UserInheritorUpdateBaseInputRequest,UserTestamentBaseInputRequest,OrgansDonorBaseInputRequest,LoveLeftInTheWorldBaseInputRequest)
from src.shareLove.models import (FamilyOffice, Trust, UserBeneficiaries,UserBeneficiariesMeta, UserInheritor, UserInheritorMeta,UserTestament,GoodsDonor,OrgansDonor,LoveLeftInTheWorld)
from src.transaction import wrap_delete_func, wrap_insert_mapping_func, wrap_update_func, wrap_update_trx
from src.authgear.adminApi import query_user_by_authgear_id, query_user_by_phone_number
from typing import List, Dict, Any, TypedDict,Callable
from zoneinfo import ZoneInfo
from src.authgear.utils import getAutherIDByNodeID
from src.utils.jwtUtil import create_jwt,verify_jwt
from fastapi import UploadFile
from src.oss.service import delete_single_file, upload_multiple_files,download_single_file
from src.oss.model import GoodsDonorMappingDict
from enum import Enum
from src.passAway.models import (PassAwayInfo,PassAwayInfoMeta)
from src.crypto.services import encrypt_plan_text, decrypt_plan_text
from src.auth.models import PhoneMaster, User,UserSettings,LanguageEnum
from src.loggerServices import log_info

from src.utils.smsProvider import send_sms
class PayloadType(TypedDict):
    userId: str
    phone: str
    uid: int
    exp: int
class ResultItem(TypedDict):
    sql: str
    isExist: bool
    params: Dict[str, Any]
class GDKeys(Enum):
    KEY1 = "image_url_1"
    KEY2 = "image_url_2"
    KEY3 = "image_url_3"
class UIKeys(Enum):
    KEY1 = "inheritor_user_id"
class UI_User_Keys(Enum):
    KEY1 = "user_id"
class UI_ID_Keys(Enum):
    KEY1 = "inheritor_id"    

# Delete
async def remove_user_inheritor(id:int,user_id:str,db:Session):
    try:
        
        # ensure User B hasn't submitted User A proof of dead
        row = db.query(PassAwayInfo).filter(PassAwayInfo.meta_id == id).count()
        if row > 0:
            return {"isSuccess":False,"errCode":"30001"}
        wrap_delete_func(UserInheritorMeta,{"meta_id": id},db,db.query(UserInheritorMeta).join(UserInheritor,UserInheritor.id==UserInheritorMeta.meta_id).filter(UserInheritor.user_id==user_id,UserInheritorMeta.meta_id==id).count()>0)
        row = db.query(UserInheritor).filter(UserInheritor.id == id,UserInheritor.user_id==user_id).first()
        if row:
            wrap_delete_func(UserInheritor,{"id": id,"user_id":user_id},db,True)
            wrap_delete_func(PhoneMaster,{"id":row.inheritor_phone_master_id},db,db.query(PhoneMaster).filter(PhoneMaster.id==row.inheritor_phone_master_id).count()>0)
        db.commit()
        return {"isSuccess":True,"errCode":"0"}
    except Exception as e:
        db.rollback()
        raise GeneralErrorExcpetion(str(e))


async def remove_love_left_in_the_world(id:int,user_id:str,db:Session):
    try:
        wrap_delete_func(LoveLeftInTheWorld,{"id": id,"user_id":user_id},db,db.query(LoveLeftInTheWorld).filter(LoveLeftInTheWorld.id==id,LoveLeftInTheWorld.user_id==user_id).count()>0)
        db.commit()
        return 
    except Exception as e:
        db.rollback()
        raise GeneralErrorExcpetion(str(e))

async def remove_goods_donor(id:int,user_id:str,db:Session):
    try:
        wrap_delete_func(GoodsDonor,{"id": id,"user_id":user_id},db,db.query(GoodsDonor).filter(GoodsDonor.id==id,GoodsDonor.user_id==user_id).count()>0)
        db.commit()
        return 
    except Exception as e:
        db.rollback()
        raise GeneralErrorExcpetion(str(e))

async def remove_user_beneficiaries(id:int,user_id:str,db:Session):
    try:
        meta_row_count = db.query(UserBeneficiariesMeta).filter(UserBeneficiariesMeta.meta_id==id).count()>0
        if meta_row_count > 0:
            wrap_delete_func(UserBeneficiariesMeta,{"meta_id": id},db,True)
        wrap_delete_func(UserBeneficiaries,{"id": id,"user_id":user_id},db,db.query(UserBeneficiaries).filter(UserBeneficiaries.id==id,UserBeneficiaries.user_id==user_id).count()>0)
        db.commit()
        return 
    except Exception as e:
        db.rollback()
        raise GeneralErrorExcpetion(str(e))

# async def remove_user_testament_trx(id:int,user_id:str,db:Session):
#     try:
#         wrap_delete_func(UserTestament,{"id": id,"user_id":user_id},db,db.query(UserTestament).filter(UserTestament.id==id,UserTestament.user_id==user_id).count()>0)
#         db.commit()
#         return 
#     except Exception as e:
#         db.rollback()
#         raise GeneralErrorExcpetion(str(e))

# async def remove_family_office_trx(id:int,user_id:str,db:Session):
#     try:
#         wrap_delete_func(FamilyOffice,{"id": id,"user_id":user_id},db,db.query(FamilyOffice).filter(FamilyOffice.id==id,FamilyOffice.user_id==user_id).count()>0)
#         obj = {
#             "did_family_office":False,
#         }
#         insert_obj = FamilyOffice(**obj,user_id=user_id)    
#         wrap_insert_mapping_func(db, insert_obj)
#         db.commit()
#         return 
#     except Exception as e:
#         db.rollback()
#         raise GeneralErrorExcpetion(str(e))


# async def remove_trust_trx(id:int,user_id:str,db:Session):
#     try:
#         wrap_delete_func(Trust,{"id": id,"user_id":user_id},db,db.query(Trust).filter(Trust.id==id,Trust.user_id==user_id).count()>0)
#         db.commit()
#         return 
#     except Exception as e:
#         db.rollback()
#         raise GeneralErrorExcpetion(str(e))


# Edit


async def edit_user_inheritor_trx(inheritor_id:str,uid: int,updates:UserInheritorUpdateBaseInputRequest, db: Session):
    try:
        row = db.query(UserInheritor).filter(UserInheritor.id==uid).first()
        if not row:
            raise Exception("Not exist")
        if row.inviate_status.value != "WIP":
            raise Exception(f"You already {row.inviate_status.value}")
        payload:PayloadType = verify_jwt(row.jwt) 
        updates = updates.model_dump(include='inviate_status')
        cloned_dict = {k: v for k, v in updates.items() if k == 'inviate_status'}
        cloned_dict.update(inheritor_user_id=inheritor_id)
        
        wrap_update_func(UserInheritor,{"id":payload['uid']},cloned_dict,db,db.query(UserInheritor).outerjoin(PhoneMaster,UserInheritor.inheritor_phone_master_id==PhoneMaster.id).filter(UserInheritor.id == payload['uid'],PhoneMaster.phone_number==payload['phone']).count() > 0)
        db.commit()
        # log_info(f"row.user_id ->>>>: {row.user_id}")
        # send push notification to user A (User B accepted or rejected the invitation)
        user_info_list = queryUserTokenAndLanguage([row.user_id],db)
        # log_info(f"user_info_list ->>>>: {user_info_list}")
        sender_name = f'{row.last_name} {row.first_name}'
        # log_info(f"sender_name ->>>>: {sender_name}")
        for user in user_info_list:
            if user["token"]:
                if user["language"] == LanguageEnum.en.value:
                    title = "Invitation status update notification"
                    if sender_name == "":
                        sender_name = "Someone"
                    invite_status = "Accepted" if updates.get('inviate_status').value == "ACCEPT" else "Rejected"
                    body = f"{sender_name} has {invite_status} with your invitation."
                elif user["language"] == LanguageEnum.zh_hans.value:
                    title = "邀请状态更新通知"
                    if sender_name == "":
                        sender_name = "某人"
                    invite_status = "接受" if updates.get('inviate_status').value == "ACCEPT"  else "拒绝"        
                    body = f"{sender_name} {invite_status}了你的邀请"
                elif user["language"] == LanguageEnum.zh_hk.value:
                    title = "邀請狀態更新通知"
                    if sender_name == "":
                        sender_name = "某人"
                    invite_status = "接受" if updates.get('inviate_status').value == "ACCEPT"  else "拒絕"            
                    body = f"{sender_name} {invite_status}了你的邀請"
                # log_info(f"token ->>>>: {user["token"]}")
                # log_info(f"title ->>>>: {title}")
                # log_info(f"body ->>>>: {body}")
                await send_push_notification(user["token"], 'default', title, body)    
        return payload['uid']
    except Exception as e:
        raise GeneralErrorExcpetion(str(e))
    
    

    

async def edit_user_inheritor_meta_trx(user_id:str,id: int,updates:UserInheritorMetaBaseInputRequest, db: Session):    
    updates = updates.model_dump()
    return wrap_update_trx(UserInheritorMeta,{"meta_id":id},updates,db,db.query(UserInheritorMeta).join(UserInheritor,UserInheritor.id==UserInheritorMeta.meta_id).filter(UserInheritor.user_id==user_id,UserInheritorMeta.meta_id==id).count()>0)


async def edit_family_office_trx(user_id:str,id: int,updates:FamilyOfficeBaseInputRequest, db: Session):
    obj = updates.model_dump()
    did_family_office = obj.get('did_family_office')
    if did_family_office == False:
        cloned_dict = {k: None if k in ['did_family_office_date','family_office_name','registeration_address','contact_person','mobile','comment'] else v for k, v in obj.items()}
    else:
        # encrypt_plan_text
        cloned_dict = {k: encrypt_plan_text(v) if k in ['family_office_name','registeration_address','contact_person','mobile','comment'] else v for k, v in obj.items()}
    
    return wrap_update_trx(FamilyOffice,{"id":id},cloned_dict,db,db.query(FamilyOffice).filter(FamilyOffice.id == id,FamilyOffice.user_id==user_id).count() > 0)


async def edit_trust_trx(user_id:str,id: int,updates:UserTestamentBaseInputRequest, db: Session):
    
    obj = updates.model_dump()
    did_trust = obj.get('did_trust')
    if did_trust == False:
        cloned_dict = {k: None if k in ['did_trust_date','trust_name','contact_person','mobile','settlor','beneficiary','comment'] else v for k, v in obj.items()}
    else:
        # encrypt_plan_text
        cloned_dict = {k: encrypt_plan_text(v) if k in ['trust_name','contact_person','mobile','settlor','beneficiary','comment'] else v for k, v in obj.items()}
    
    return wrap_update_trx(Trust,{"id":id},cloned_dict,db,db.query(Trust).filter(Trust.id == id,Trust.user_id==user_id).count() > 0)


async def edit_user_testament_trx(user_id:str,id: int,updates:UserTestamentBaseInputRequest, db: Session):
    
    obj = updates.model_dump()
    did_testament = obj.get('did_testament')
    if did_testament == False:
        cloned_dict = {k: None if k in ['did_testament_date','testament_store_in','comment'] else v for k, v in obj.items()}
    else:
        # encrypt_plan_text
        cloned_dict = {k: encrypt_plan_text(v) if k in ['testament_store_in', 'comment'] else v for k, v in obj.items()}
    
    return wrap_update_trx(UserTestament,{"id":id},cloned_dict,db,db.query(UserTestament).filter(UserTestament.id == id,UserTestament.user_id==user_id).count() > 0)


                                
                                
async def edit_goods_donor_trx(user_id:str,id: int,req_data,oss_data,files:List[UploadFile]| None, db: Session):
    try:
        # query image url
        row = db.query(GoodsDonor).filter(GoodsDonor.id == id,GoodsDonor.user_id==user_id).first()
        if not row:
            raise Exception("Not exist")    
        
        
        
        # delete oss 
        if row.image_url_1:
                
            delete_single_file(row.image_url_1)
        if row.image_url_2:    
                
            delete_single_file(row.image_url_2)
        if row.image_url_3:        
                
            delete_single_file(row.image_url_3)
        

        # wrap_delete_func(GoodsDonor,{"id": id},db)
        # if exist files 
        if files:
            # upload oss
            new_oss_mapping_data:GoodsDonorMappingDict =  await upload_multiple_files(user_id, files, "images","goods_donor",oss_data,True)
            
            # encrypt_plan_text
            req_data = {k: encrypt_plan_text(v) if k in ['goods_info','donor_organization'] else v for k, v in req_data.items()}
            goodsDonorData = {**new_oss_mapping_data,**req_data}

        else:
            # encrypt_plan_text
            req_data = {k: encrypt_plan_text(v) if k in ['goods_info','donor_organization'] else v for k, v in req_data.items()}
            goodsDonorData = {**oss_data,**req_data}
                    
        # edit goods donor row
        wrap_update_func(GoodsDonor,{"id":id},goodsDonorData,db,True)
        
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        raise GeneralErrorExcpetion(str(e))    

async def edit_organs_donor_trx(user_id:str,id: int,updates:OrgansDonorBaseInputRequest, db: Session):
    updates = updates.model_dump()
    # encrypt_plan_text
    updates = {k: encrypt_plan_text(v) if k in ['contact_organization','comment'] else v for k, v in updates.items()}
    
    return wrap_update_trx(OrgansDonor,{"id":id},updates,db,db.query(OrgansDonor).filter(OrgansDonor.id == id,OrgansDonor.user_id==user_id).count() > 0)

async def edit_love_left_in_the_world_trx(user_id:str,id: int,updates:LoveLeftInTheWorldBaseInputRequest, db: Session):
    updates = updates.model_dump()
    # encrypt_plan_text
    updates = {k: encrypt_plan_text(v) if k in ['title','content'] else v for k, v in updates.items()}
    return wrap_update_trx(LoveLeftInTheWorld,{"id":id},updates,db,db.query(LoveLeftInTheWorld).filter(LoveLeftInTheWorld.id == id,LoveLeftInTheWorld.user_id==user_id).count() > 0)


async def edit_insurance_beneficiaries_trx(user_id:str,id: int,updates:PhoneBeneficiariesBaseInputRequest, db: Session):
    try:
        updates = updates.model_dump()
        # encrypt_plan_text
        cloned_dict = {k: v for k, v in updates.items() if k != 'contact_country_code' and k != 'contact_number'}
        cloned_dict = {k: encrypt_plan_text(v) if k in ['platform_or_company','first_name','last_name','relation'] else v for k, v in cloned_dict.items()}
        
        wrap_update_func(UserBeneficiaries,{"id":id},cloned_dict,db,db.query(UserBeneficiaries).filter(UserBeneficiaries.id == id,UserBeneficiaries.user_id==user_id).count() > 0)
        db.commit()
        return True
    except Exception as e:
        raise GeneralErrorExcpetion(str(e))


async def edit_phone_beneficiaries_trx(user_id:str,id: int,updates:PhoneBeneficiariesBaseInputRequest, db: Session):
    try:
        updates = updates.model_dump()
        # encrypt_plan_text
        cloned_dict = {k: v for k, v in updates.items() if k != 'contact_country_code' and k != 'contact_number'}
        cloned_dict = {k: encrypt_plan_text(v) if k in ['platform_or_company','first_name','last_name','relation'] else v for k, v in cloned_dict.items()}
        
        cloned_dict2 = {k: v for k, v in updates.items() if k == 'contact_country_code' or k == 'contact_number'}
        

        wrap_update_func(UserBeneficiaries,{"id":id},cloned_dict,db,db.query(UserBeneficiaries).filter(UserBeneficiaries.id == id,UserBeneficiaries.user_id==user_id).count() > 0)
        wrap_update_func(UserBeneficiariesMeta,{"meta_id":id},cloned_dict2,db,db.query(UserBeneficiariesMeta).join(UserBeneficiaries,UserBeneficiaries.id==UserBeneficiariesMeta.meta_id).filter(UserBeneficiariesMeta.meta_id == id,UserBeneficiaries.user_id==user_id).count() > 0)
        db.commit()
        return True
    except Exception as e:
        raise GeneralErrorExcpetion(str(e))
    



# Query
async def get_user_inheritor_to_claim_user_dead_or_access_dead_usertrx(fl: List,db:Session):
    result = db.query(UserInheritor.id.label("inheritor_id"),UserInheritor.user_id,UserInheritor.inviate_status.label("ui_status"),UserInheritor.updated_at).filter(*fl).all()
    # 将结果转换为字典列表
    result_list = [row._asdict() for row in result]
    if len(result_list) > 0:
            for row in result_list:
                
                for k in list(row.keys()):  # 創建鍵的列表副本
                    
                    if k in {UI_User_Keys.KEY1.value}: # user_id
                        authgearID = db.query(User).filter(User.id == row[k]).first()
                        if not authgearID:
                            # Remove current dict from result_list and continue to next row
                            result_list.remove(row)
                            continue  # Skip to the next iteration of the outer loop
                            
                        res = await query_user_by_authgear_id(authgearID.authgear_id)
                        if res is None:
                            result_list.remove(row)
                            continue # Skip to the next iteration of the outer loop
                        
                        if 'given_name' in res[0]['node']['standardAttributes']:
                            given_name = res[0]['node']['standardAttributes']['given_name']
                            row['given_name'] = given_name
                        if 'family_name' in res[0]['node']['standardAttributes']:    
                            family_name = res[0]['node']['standardAttributes']['family_name']
                            row['family_name'] = family_name
                        if 'phone_number' in res[0]['node']['standardAttributes']:    
                            phone_number = res[0]['node']['standardAttributes']['phone_number']
                            row['phone_number'] = phone_number
                        if 'birthdate' in res[0]['node']['standardAttributes']:
                            birthdate = res[0]['node']['standardAttributes']['birthdate']
                            row['birthdate'] = birthdate
                    if k in {UI_ID_Keys.KEY1.value}: # inheritor_id (UserInheritor.id)
                        p = db.query(PassAwayInfo.id).filter(PassAwayInfo.meta_id == row[k]).all()
                        pl = [row._asdict() for row in p]
                        if len(pl)>0:
                            pid = pl[0]['id']
                            pam = db.query(PassAwayInfoMeta.approval_status).filter(PassAwayInfoMeta.meta_id == pid).all()
                            paml = [row._asdict() for row in pam]
                            if paml:
                                row['ui_status'] = paml[0]['approval_status']
                            
    
    return result_list

async def get_single_user_inheritor_trx(fl: List, db: Session):

    result = db.query(UserInheritor.id.label("inheritor_id"),PhoneMaster.phone_number,UserInheritor.first_name.label('family_name'),UserInheritor.last_name.label('given_name'),UserInheritor.inviate_status,UserInheritor.invitation_expire_date,UserInheritor.inheritor_user_id,UserInheritor.updated_at,UserInheritorMeta.LB,UserInheritorMeta.OP,UserInheritorMeta.LET,UserInheritorMeta.SB,UserInheritorMeta.HM,UserInheritorMeta.MTS,UserInheritorMeta.LS,UserInheritorMeta.FC,UserInheritorMeta.PE).join(UserInheritorMeta, UserInheritor.id == UserInheritorMeta.meta_id).join(PhoneMaster,UserInheritor.inheritor_phone_master_id==PhoneMaster.id).filter(*fl).all()
    # 将结果转换为字典列表
    result_list = [row._asdict() for row in result]
    
    return result_list

async def get_user_inheritor_trx(fl: List, db: Session,user_id:str):
    maximum = db.query(UserSettings.maximum_number_inheritor).filter(UserSettings.user_id == user_id).scalar()
    result = db.query(UserInheritor.id.label("inheritor_id"),PhoneMaster.phone_number,UserInheritor.first_name.label('family_name'),UserInheritor.last_name.label('given_name'),UserInheritor.inviate_status,UserInheritor.invitation_expire_date,UserInheritor.inheritor_user_id,UserInheritor.updated_at,UserInheritorMeta.LB,UserInheritorMeta.OP,UserInheritorMeta.LET,UserInheritorMeta.SB,UserInheritorMeta.HM,UserInheritorMeta.MTS,UserInheritorMeta.LS,UserInheritorMeta.FC,UserInheritorMeta.PE).join(UserInheritorMeta, UserInheritor.id == UserInheritorMeta.meta_id).join(PhoneMaster,UserInheritor.inheritor_phone_master_id==PhoneMaster.id).filter(*fl).all()
    result_list = [row._asdict() for row in result]
    sender_name = await get_sender_name_by_user_id(user_id, db)

    for row in result_list:
        inheritor_id = row.get("inheritor_id")
        try:
            row["ulink"] = await build_inheritor_ulink(inheritor_id)
        except Exception:
            row["ulink"] = None
        row["sender_name"] = sender_name
        
    return {"maximum_no_inheritor":maximum,"result_list":result_list}


async def get_user_beneficiaries_trx(fl: List, db: Session,cb: Callable[[], bool]=None):
    if cb:
        p = await cb
        if p:
            result = db.query(UserBeneficiaries.id.label("beneficiary_id"),UserBeneficiaries.beneficiary_type,UserBeneficiaries.platform_or_company,UserBeneficiaries.first_name,UserBeneficiaries.last_name,UserBeneficiaries.relation,UserBeneficiaries.updated_at,UserBeneficiariesMeta.contact_country_code,UserBeneficiariesMeta.contact_number).outerjoin(UserBeneficiariesMeta, UserBeneficiaries.id == UserBeneficiariesMeta.meta_id).filter(*fl).all()
            # 将结果转换为字典列表
            result_list = [row._asdict() for row in result]
            if len(result_list) > 0:
                result_list = [
                    {k: decrypt_plan_text(v) if k in ['platform_or_company', 'first_name','last_name','relation'] else v for k, v in row.items()}
                    for row in result_list
                ]
            return result_list
        else:
            return []
    else:
        result = db.query(UserBeneficiaries.id.label("beneficiary_id"),UserBeneficiaries.beneficiary_type,UserBeneficiaries.platform_or_company,UserBeneficiaries.first_name,UserBeneficiaries.last_name,UserBeneficiaries.relation,UserBeneficiaries.updated_at,UserBeneficiariesMeta.contact_country_code,UserBeneficiariesMeta.contact_number).outerjoin(UserBeneficiariesMeta, UserBeneficiaries.id == UserBeneficiariesMeta.meta_id).filter(*fl).all()
    
        # 将结果转换为字典列表
        result_list = [row._asdict() for row in result]
        if len(result_list) > 0:
            result_list = [
                {k: decrypt_plan_text(v) if k in ['platform_or_company', 'first_name','last_name','relation'] else v for k, v in row.items()}
                for row in result_list
            ]
        return result_list
    

async def get_family_office_trx(fl: List, db: Session,cb: Callable[[], bool]=None):
    if cb:
        p = await cb
        if p:
            result = db.query(FamilyOffice.id.label("family_office_id"),FamilyOffice.did_family_office,FamilyOffice.did_family_office_date,FamilyOffice.family_office_name,FamilyOffice.registeration_address,FamilyOffice.contact_person,FamilyOffice.mobile,FamilyOffice.comment,FamilyOffice.updated_at).filter(*fl).all()
            # 将结果转换为字典列表
            result_list = [row._asdict() for row in result]
            if len(result_list) > 0:
                result_list = [
                    {k: decrypt_plan_text(v) if k in ['family_office_name','registeration_address','contact_person','mobile','comment'] else v for k, v in row.items()}
                    for row in result_list
                ]
            return result_list
        else:
            return []
    else:
        result = db.query(FamilyOffice.id.label("family_office_id"),FamilyOffice.did_family_office,FamilyOffice.did_family_office_date,FamilyOffice.family_office_name,FamilyOffice.registeration_address,FamilyOffice.contact_person,FamilyOffice.mobile,FamilyOffice.comment,FamilyOffice.updated_at).filter(*fl).all()
        # 将结果转换为字典列表
        result_list = [row._asdict() for row in result]
        if len(result_list) > 0:
            result_list = [
                {k: decrypt_plan_text(v) if k in ['family_office_name','registeration_address','contact_person','mobile','comment'] else v for k, v in row.items()}
                for row in result_list
            ]
        return result_list


async def get_trust_trx(fl: List, db: Session,cb: Callable[[], bool]=None):
    if cb:
        p = await cb
        if p:
            result = db.query(Trust.id.label("trust_id"),Trust.did_trust,Trust.did_trust_date,Trust.trust_name,Trust.contact_person,Trust.mobile,Trust.settlor,Trust.beneficiary,Trust.comment,Trust.updated_at).filter(*fl).all()
            # 将结果转换为字典列表
            result_list = [row._asdict() for row in result]
            if len(result_list) > 0:
                result_list = [
                    {k: decrypt_plan_text(v) if k in ['trust_name','contact_person','mobile','settlor','beneficiary','comment'] else v for k, v in row.items()}
                    for row in result_list
                ]
            return result_list
        else:
            return []
    else:
        result = db.query(Trust.id.label("trust_id"),Trust.did_trust,Trust.did_trust_date,Trust.trust_name,Trust.contact_person,Trust.mobile,Trust.settlor,Trust.beneficiary,Trust.comment,Trust.updated_at).filter(*fl).all()
        # 将结果转换为字典列表
        result_list = [row._asdict() for row in result]
        if len(result_list) > 0:
            result_list = [
                {k: decrypt_plan_text(v) if k in ['trust_name','contact_person','mobile','settlor','beneficiary','comment'] else v for k, v in row.items()}
                for row in result_list
            ]
        return result_list

async def get_user_testament_trx(fl: List, db: Session,cb: Callable[[], bool]=None):
    if cb:
        p = await cb
        if p:
            result = db.query(UserTestament.id.label("user_testament_id"),UserTestament.did_testament,UserTestament.did_testament_date,UserTestament.testament_store_in,UserTestament.comment,UserTestament.updated_at).filter(*fl).all()
            # 将结果转换为字典列表
            result_list = [row._asdict() for row in result]
            if len(result_list) > 0:
                result_list = [
                    {k: decrypt_plan_text(v) if k in ['testament_store_in', 'comment'] else v for k, v in row.items()}
                    for row in result_list
                ]
            return result_list
        else:
            return []
    else:
        result = db.query(UserTestament.id.label("user_testament_id"),UserTestament.did_testament,UserTestament.did_testament_date,UserTestament.testament_store_in,UserTestament.comment,UserTestament.updated_at).filter(*fl).all()
        # 将结果转换为字典列表
        result_list = [row._asdict() for row in result]
        if len(result_list) > 0:
            result_list = [
                {k: decrypt_plan_text(v) if k in ['testament_store_in', 'comment'] else v for k, v in row.items()}
                for row in result_list
            ]
        return result_list
     
async def get_goods_donor_trx(fl: List, db: Session,cb: Callable[[], bool]=None):
    try:
        if cb:
            p = await cb
            if p:
                result = db.query(GoodsDonor.id.label("goods_donor_id"),GoodsDonor.image_url_1,GoodsDonor.image_url_2,GoodsDonor.image_url_3,GoodsDonor.goods_info,GoodsDonor.donor_organization,GoodsDonor.updated_at).filter(*fl).all()
                # 将结果转换为字典列表
                result_list = [row._asdict() for row in result]
                if len(result_list) > 0:
                    result_list = [
                        {k: decrypt_plan_text(v) if k in ['goods_info', 'donor_organization'] else v for k, v in row.items()}
                        for row in result_list
                    ]
                    for row in result_list:
                        for k in row:
                            if k in {GDKeys.KEY1.value,GDKeys.KEY2.value,GDKeys.KEY3.value}:
                                if row[k]:
                                    r = await download_single_file(row[k],True)
                                    row[k] = r
                else:
                    return []
                return result_list
            else:
                return []
        else:
            result = db.query(GoodsDonor.id.label("goods_donor_id"),GoodsDonor.image_url_1,GoodsDonor.image_url_2,GoodsDonor.image_url_3,GoodsDonor.goods_info,GoodsDonor.donor_organization,GoodsDonor.updated_at).filter(*fl).all()
            # 将结果转换为字典列表
            result_list = [row._asdict() for row in result]
            if len(result_list) > 0:
                result_list = [
                    {k: decrypt_plan_text(v) if k in ['goods_info', 'donor_organization'] else v for k, v in row.items()}
                    for row in result_list
                ]
                for row in result_list:
                    for k in row:
                        if k in {GDKeys.KEY1.value,GDKeys.KEY2.value,GDKeys.KEY3.value}:
                            if row[k]:
                                r = await download_single_file(row[k], True)
                                row[k] = r
            else:
                return []
            return result_list
    except Exception as e:        
        raise GeneralErrorExcpetion(str(e))
        
async def get_organs_donor_trx(fl: List, db: Session,cb: Callable[[], bool]=None):
    if cb:
        p = await cb
        if p:
            result = db.query(OrgansDonor.id.label("organs_donor_id"),OrgansDonor.did_arrange_organ_donor,OrgansDonor.contact_organization,OrgansDonor.comment,OrgansDonor.updated_at).filter(*fl).all()
            # 将结果转换为字典列表
            result_list = [row._asdict() for row in result]
            if len(result_list) > 0:
                result_list = [
                    {k: decrypt_plan_text(v) if k in ['contact_organization', 'comment'] else v for k, v in row.items()}
                    for row in result_list
                ]
            return result_list
        else:
            return []
    else:
        result = db.query(OrgansDonor.id.label("organs_donor_id"),OrgansDonor.did_arrange_organ_donor,OrgansDonor.contact_organization,OrgansDonor.comment,OrgansDonor.updated_at).filter(*fl).all()
        # 将结果转换为字典列表
        result_list = [row._asdict() for row in result]
        if len(result_list) > 0:
            result_list = [
                {k: decrypt_plan_text(v) if k in ['contact_organization', 'comment'] else v for k, v in row.items()}
                for row in result_list
            ]
        return result_list
    
async def get_love_left_in_the_world_trx(fl: List, db: Session,cb: Callable[[], bool]=None):
    if cb:
        p = await cb
        if p:
            result = db.query(LoveLeftInTheWorld.id.label("love_left_in_the_world_id"),LoveLeftInTheWorld.title,LoveLeftInTheWorld.content,LoveLeftInTheWorld.updated_at).filter(*fl).all()
            # 将结果转换为字典列表
            result_list = [row._asdict() for row in result]
            if len(result_list) > 0:
                result_list = [
                    {k: decrypt_plan_text(v) if k in ['title', 'content'] else v for k, v in row.items()}
                    for row in result_list
                ]
            return result_list
        else:
            return []
    else:
        result = db.query(LoveLeftInTheWorld.id.label("love_left_in_the_world_id"),LoveLeftInTheWorld.title,LoveLeftInTheWorld.content,LoveLeftInTheWorld.updated_at).filter(*fl).all()
        # 将结果转换为字典列表
        result_list = [row._asdict() for row in result]
        if len(result_list) > 0:
            result_list = [
                {k: decrypt_plan_text(v) if k in ['title', 'content'] else v for k, v in row.items()}
                for row in result_list
            ]
        return result_list
    
# Insert
async def find_inheritor_authgear_id_by_phone(phone_number:str):
        result = await query_user_by_phone_number(phone_number)
        if result == False:
            return False
        node_id = result[0]['node']['id']
        # [
        #     {
        #         "node": {
        #             "id": "VXNlcjoxYzBiNjkzNS01OThmLTQyNmItYTc4NS00Mjc5ZjUwYjM3YzU",
        #             "standardAttributes": {
        #                 "birthdate": "1985-06-04",
        #                 "family_name": "Chan",
        #                 "gender": "male",
        #                 "given_name": "JIm",
        #                 "phone_number": "+85251823007",
        #                 "phone_number_verified": false,
        #                 "updated_at": 1740377958
        #             }
        #         }
        #     }
        # ]
        
        return getAutherIDByNodeID(node_id)

async def create_user_inheritor_trx(reqData: UserInheritorBaseInputRequest, user_id: str, db: Session) -> list:
    try:
        # log_info(f"start rows trx")
        maximum = db.query(UserSettings.maximum_number_inheritor).filter(UserSettings.user_id == user_id).scalar()
        # 檢查 maximum 是否為 None
        if maximum is None:
            raise Exception("User settings not found or maximum_number_inheritor is not set for this user")
        
        rows = db.query(UserInheritor).filter(
            UserInheritor.user_id == user_id,
            or_(UserInheritor.inviate_status == "WIP", UserInheritor.inviate_status == "ACCEPT")
        ).count()
        # log_info(f"create_user_inheritor_trx rows: {rows}")
        if rows >= maximum:
            raise Exception(f"Maximum {maximum} inheritors exceeded")
            
        phone_number = reqData.model_dump(include={'phone_number'}).get('phone_number')
        first_name = reqData.model_dump(include={'first_name'}).get('first_name')
        last_name = reqData.model_dump(include={'last_name'}).get('last_name')
        sender_name = reqData.model_dump(include={'sender_name'}).get('sender_name')
        expire_date = datetime.now(ZoneInfo("Asia/Hong_Kong")) + timedelta(days=7)
        
        isExist = db.query(UserInheritor).join(PhoneMaster,UserInheritor.inheritor_phone_master_id==PhoneMaster.id).filter(PhoneMaster.phone_number==phone_number,UserInheritor.user_id==user_id,UserInheritor.inviate_status=="WIP").count() > 0
        if isExist:
            # query uid
            u = db.query(UserInheritor.id).join(PhoneMaster,UserInheritor.inheritor_phone_master_id==PhoneMaster.id).filter(PhoneMaster.phone_number==phone_number,UserInheritor.user_id==user_id,UserInheritor.inviate_status=="WIP").all()
            ul = [row._asdict() for row in u]
            u_id = ul[0]['id']
            # delete u row
            wrap_delete_func(UserInheritorMeta,{"meta_id": u_id},db)
            wrap_delete_func(UserInheritor,{"id": u_id},db)

        # start to find_inheritor_authgear_id_by_phone 
        inheritor_authgear_id = await find_inheritor_authgear_id_by_phone(phone_number)    
        # log_info(f"inheritor_authgear_id: {inheritor_authgear_id}")
        if inheritor_authgear_id == False:
            # inheritor_authgear_id not found by phone number
            phone_master_obj = PhoneMaster(**reqData.model_dump(include={"phone_number"}),user_id=user_id)
            result_phone_master = wrap_insert_mapping_func(db, phone_master_obj)
            insert_obj = UserInheritor(**reqData.model_dump(include={"first_name","last_name"}),inviate_status="WIP",user_id=user_id,invitation_expire_date=expire_date,inheritor_phone_master_id=result_phone_master.id)
            result = wrap_insert_mapping_func(db, insert_obj)
            insert_obj_meta = UserInheritorMeta(**reqData.model_dump(include={"LB","OP","LET","SB","HM","MTS","LS","FC","PE"}),meta_id=result.id)
            result_meta = wrap_insert_mapping_func(db, insert_obj_meta)
            
            token = create_inheritor_jwt(user_id,phone_number,result.id)
            wrap_update_func(UserInheritor,{"id":result.id},{"jwt":token},db,True)
        else:
            # inheritor_authgear_id found by phone number     
            row = db.query(User).filter(User.authgear_id==inheritor_authgear_id).first()
            if not row:
                log_info("User not found by authgear id in User tb")
                raise Exception("User not found by authgear id in User tb")
            inheritor_user_id = row.id
            if inheritor_user_id == user_id:
                log_info("You cannot invite yourself as inheritor")
                raise Exception("You cannot invite yourself as inheritor")
            phone_master_obj = PhoneMaster(**reqData.model_dump(include={"phone_number"}),user_id=user_id)
            result_phone_master = wrap_insert_mapping_func(db, phone_master_obj)
            insert_obj = UserInheritor(**reqData.model_dump(include={"first_name","last_name"}),inviate_status="WIP",user_id=user_id,invitation_expire_date=expire_date,inheritor_phone_master_id=result_phone_master.id)
            result = wrap_insert_mapping_func(db, insert_obj)
            insert_obj_meta = UserInheritorMeta(**reqData.model_dump(include={"LB","OP","LET","SB","HM","MTS","LS","FC","PE"}),meta_id=result.id)
            result_meta = wrap_insert_mapping_func(db, insert_obj_meta)
            # log_info("start send sms")
            token = create_inheritor_jwt(user_id,phone_number,result.id)
            # log_info("end send sms")
            wrap_update_func(UserInheritor,{"id":result.id},{"jwt":token},db,True)


        db.commit()
        db.refresh(result)
        db.refresh(result_meta)

        fl: List = [UserInheritor.user_id == user_id, UserInheritor.id == result.id]
        return await get_user_inheritor_trx(fl=fl, db=db, user_id=user_id)
    except Exception as e:
        db.rollback()
        log_info(f"create_user_inheritor_trx error: {str(e)}")
        raise GeneralErrorExcpetion(str(e))    
    

async def create_phone_beneficiaries_trx(reqData: PhoneBeneficiariesBaseInputRequest,user_id: str, db: Session):
    try:
        obj = reqData.model_dump()
        cloned_dict = {k: v for k, v in obj.items() if k in ['beneficiary_type','platform_or_company','first_name','last_name','relation']}
        cloned_dict = {k: encrypt_plan_text(v) if k in ['platform_or_company','first_name','last_name','relation'] else v for k, v in cloned_dict.items()}
        cloned_dict2 = {k: v for k, v in obj.items() if k in ['contact_country_code','contact_number']}
        
        
        insert_obj = UserBeneficiaries(**cloned_dict,user_id=user_id)
        result = wrap_insert_mapping_func(db, insert_obj)
        insert_obj_meta = UserBeneficiariesMeta(**cloned_dict2,meta_id=result.id)
        result_meta = wrap_insert_mapping_func(db, insert_obj_meta)
        db.commit()
        db.refresh(result)
        db.refresh(result_meta)
        return result.id
    except Exception as e:
        db.rollback()
        raise GeneralErrorExcpetion(str(e))     


async def create_insurance_beneficiaries_trx(reqData: InsuranceBeneficiariesBaseInputRequest,user_id: str, db: Session):
    try:
        obj = reqData.model_dump()
        cloned_dict = {k: encrypt_plan_text(v) if k in ['platform_or_company','first_name','last_name','relation'] else v for k, v in obj.items()}
        insert_obj = UserBeneficiaries(**cloned_dict,user_id=user_id)
        result = wrap_insert_mapping_func(db, insert_obj)
        
        db.commit()
        db.refresh(result)
        
        return result.id
    except Exception as e:
        db.rollback()
        raise GeneralErrorExcpetion(str(e))     


async def create_trust_trx(reqData: TrustBaseInputRequest, user_id: str, db: Session):
    try:
        isExist = db.query(Trust).filter(Trust.user_id==user_id).count() > 0
        if isExist:
            raise Exception("You created record already")
        
        
        obj = reqData.model_dump()
        did_trust = obj.get('did_trust')
        # log_info(f'------------------->{did_trust}')
        if did_trust == False:
            cloned_dict = {k: None if k in ['did_trust_date','trust_name','contact_person','mobile','settlor','beneficiary','comment'] else v for k, v in obj.items()}
        else:     
            cloned_dict = {k: encrypt_plan_text(v) if k in ['trust_name','contact_person','mobile','settlor','beneficiary','comment'] else v for k, v in obj.items()}
        
        insert_obj = Trust(**cloned_dict,user_id=user_id)    
        result = wrap_insert_mapping_func(db, insert_obj)
        
        db.commit()
        db.refresh(result)
        
        return result.id
    except Exception as e:
        db.rollback()
        raise GeneralErrorExcpetion(str(e))     

async def create_family_office_trx(reqData: FamilyOfficeBaseInputRequest, user_id: str, db: Session):
    try:
        isExist = db.query(FamilyOffice).filter(FamilyOffice.user_id==user_id).count() > 0
        if isExist:
            raise Exception("You created record already")
        
        
        obj = reqData.model_dump()
        did_family_office = obj.get('did_family_office')
        # log_info(f'------------------->{did_family_office}')
        if did_family_office == False:
            cloned_dict = {k: None if k in ['did_family_office_date','family_office_name','registeration_address','contact_person','mobile','comment'] else v for k, v in obj.items()}
        else:     
            cloned_dict = {k: encrypt_plan_text(v) if k in ['family_office_name','registeration_address','contact_person','mobile','comment'] else v for k, v in obj.items()}
        
        insert_obj = FamilyOffice(**cloned_dict,user_id=user_id)    
        result = wrap_insert_mapping_func(db, insert_obj)
        
        db.commit()
        db.refresh(result)
        
        return result.id
    except Exception as e:
        db.rollback()
        raise GeneralErrorExcpetion(str(e))     


async def create_user_testament_trx(reqData: UserTestamentBaseInputRequest, user_id: str, db: Session):
    try:
        isExist = db.query(UserTestament).filter(UserTestament.user_id==user_id).count() > 0
        if isExist:
            raise Exception("You created record already")
        
        
        obj = reqData.model_dump()
        did_testament = obj.get('did_testament')
        # log_info(f'------------------->{did_testament}')
        if did_testament == False:
            cloned_dict = {k: None if k in ['did_testament_date','testament_store_in','comment'] else v for k, v in obj.items()}
        else:     
            cloned_dict = {k: encrypt_plan_text(v) if k in ['testament_store_in','comment'] else v for k, v in obj.items()}
        
        insert_obj = UserTestament(**cloned_dict,user_id=user_id)    
        result = wrap_insert_mapping_func(db, insert_obj)
        
        db.commit()
        db.refresh(result)
        
        return result.id
    except Exception as e:
        db.rollback()
        raise GeneralErrorExcpetion(str(e))     
    
async def create_goods_donor_trx(reqData,ossData,files:List[UploadFile] | None,user_id: str, db: Session):
    try:
        rowsCount = db.query(GoodsDonor).filter(GoodsDonor.user_id==user_id).count()
        if rowsCount >= 5:
            raise Exception("Maximum 5 pcs record")
        if files:
            # upload oss
            new_oss_mapping_data:GoodsDonorMappingDict =  await upload_multiple_files(user_id, files, "images","goods_donor",ossData, True)
            reqData = {k: encrypt_plan_text(v) if k in ['goods_info','donor_organization'] else v for k, v in reqData.items()}
            goodsDonorData = {**new_oss_mapping_data,**reqData}
        else:
            reqData = {k: encrypt_plan_text(v) if k in ['goods_info','donor_organization'] else v for k, v in reqData.items()}
            goodsDonorData = {**reqData}

        # insert goods donor row
        insert_goods_donor_obj = GoodsDonor(**goodsDonorData,user_id=user_id)
        
        res = wrap_insert_mapping_func(db, insert_goods_donor_obj)
        db.commit()
        return res.id
    except Exception as e:
        db.rollback()
        raise GeneralErrorExcpetion(str(e))    
    

async def create_organs_donor_trx(reqData: OrgansDonorBaseInputRequest,user_id: str, db: Session):
    try:
        obj = reqData.model_dump()
        cloned_dict = {k: encrypt_plan_text(v) if k in ['contact_organization','comment'] else v for k, v in obj.items()}
        insert_obj = OrgansDonor(**cloned_dict,user_id=user_id)
        
        result = wrap_insert_mapping_func(db, insert_obj)
        
        db.commit()
        db.refresh(result)
        
        return result.id
    except Exception as e:
        db.rollback()
        raise GeneralErrorExcpetion(str(e))     
    
    
    
    
async def create_love_left_in_the_world_trx(reqData: LoveLeftInTheWorldBaseInputRequest,user_id: str, db: Session):
    try:
        obj = reqData.model_dump()
        cloned_dict = {k: encrypt_plan_text(v) if k in ['title','content'] else v for k, v in obj.items()}
        insert_obj = LoveLeftInTheWorld(**cloned_dict,user_id=user_id)    
        result = wrap_insert_mapping_func(db, insert_obj)
        
        db.commit()
        db.refresh(result)
        
        return result.id
    except Exception as e:
        db.rollback()
        raise GeneralErrorExcpetion(str(e))