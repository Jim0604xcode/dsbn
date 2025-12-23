from sqlalchemy.orm import Session
from src.exceptions import GeneralErrorExcpetion
from src.secertBase.schemas import (BankAccountBaseInputRequest, ConfidentialEventBaseInputRequest, PropertyBaseInputRequest, SafetyDepositBoxBaseInputRequest, SecretBaseInputRequest)
from typing import List,Callable
from src.secertBase.models import (BankAccount, ConfidentialEvent, Property, SafetyDepositBox,SecretBase)
from src.transaction import wrap_delete_func, wrap_insert_mapping_func, wrap_update_trx
# from src.loggerServices import log_info
from src.shareLove.models import UserInheritor,UserInheritorMeta
from typing import Literal
from src.crypto.services import encrypt_plan_text, decrypt_plan_text
# Query

async def get_dead_user_permission_trx(user_id: str, dead_user_id: str, db: Session):
    try:
        # log_info(f'user_id----->{user_id}')
        # log_info(f'dead_user_id----->{dead_user_id}')
        dead_user = db.query(UserInheritor).filter(UserInheritor.user_id == dead_user_id, UserInheritor.inheritor_user_id == user_id).first()
        if not dead_user:
            return {"LB": False, "OP": False, "LET": False, "SB": False, "HM": False, "MTS": False, "LS": False, "FC": False, "PE": False}
        
        meta_id = dead_user.id
        # log_info(f'meta_id----->{meta_id}')
        dead_user_meta = db.query(UserInheritorMeta).filter(UserInheritorMeta.meta_id == meta_id).first()
        if not dead_user_meta:
            return {"LB": False, "OP": False, "LET": False, "SB": False, "HM": False, "MTS": False, "LS": False, "FC": False, "PE": False}
        
        permissions = {
            "LB": getattr(dead_user_meta, "LB", 0),
            "OP": getattr(dead_user_meta, "OP", 0),
            "LET": getattr(dead_user_meta, "LET", 0),
            "SB": getattr(dead_user_meta, "SB", 0),
            "HM": getattr(dead_user_meta, "HM", 0),
            "MTS": getattr(dead_user_meta, "MTS", 0),
            "LS": getattr(dead_user_meta, "LS", 0),
            "FC": getattr(dead_user_meta, "FC", 0),
            "PE": getattr(dead_user_meta, "PE", 0)
        }
        return permissions
    except Exception as e:
        raise GeneralErrorExcpetion(str(e))



# "LB" = loveBequeathed , "OP" = , "LET" = , "SB" = secert Base, "HM", "MTS" = message to you, "LS" = life summary, "FC" = final chapter, "PE" = personal explore
async def check_dead_user_permission(user_id:str,dead_user_id:str,db:Session,key:Literal["LB", "OP", "LET", "SB", "HM", "MTS", "LS", "FC", "PE"]):
    try:
        
        dead_user = db.query(UserInheritor).filter(UserInheritor.user_id == dead_user_id,UserInheritor.inheritor_user_id == user_id).first()
        if not dead_user:
            return False
        meta_id = dead_user.id
        
        dead_user_meta = db.query(UserInheritorMeta).filter(UserInheritorMeta.meta_id == meta_id).first()
        if not dead_user_meta:
            return False
        if dead_user_meta:
            value = getattr(dead_user_meta, key, False)
            return value
    except Exception as e:
        raise GeneralErrorExcpetion(str(e))
    
async def get_bank_account_trx(fl: List,db:Session,cb: Callable[[], bool]=None):
    
    if cb:
        p = await cb
        if p:
            result = db.query(BankAccount.id.label("bank_account_id"),BankAccount.bank_account_name,BankAccount.bank_account_number,BankAccount.currency).join(SecretBase,SecretBase.id==BankAccount.meta_id).filter(*fl).all()
            # 将结果转换为字典列表
            result_list = [row._asdict() for row in result]
            if len(result_list) > 0:
                result_list = [
                    {k: decrypt_plan_text(v) if k in ['bank_account_name', 'bank_account_number'] else v for k, v in row.items()}
                    for row in result_list
                ]
            return result_list
            
        else:
            return []
    else:
        result = db.query(BankAccount.id.label("bank_account_id"),BankAccount.bank_account_name,BankAccount.bank_account_number,BankAccount.currency).join(SecretBase,SecretBase.id==BankAccount.meta_id).filter(*fl).all()
        # 将结果转换为字典列表
        result_list = [row._asdict() for row in result]
        if len(result_list) > 0:
            result_list = [
                {k: decrypt_plan_text(v) if k in ['bank_account_name', 'bank_account_number'] else v for k, v in row.items()}
                for row in result_list
            ]
        return result_list
async def get_property_trx(fl:List,db:Session,ql:List,cb: Callable[[], bool]=None):
    if cb:
        p = await cb
        if p:
            result = db.query(*ql).join(SecretBase,SecretBase.id==Property.meta_id).filter(*fl).all()
            # 将结果转换为字典列表
            result_list = [row._asdict() for row in result]
            if len(result_list) > 0:
                result_list = [
                    {k: decrypt_plan_text(v) if k in ['property_name', 'property_address','remarks'] else v for k, v in row.items()}
                    for row in result_list
                ]
            return result_list
        else:
            return []
    else:
        result = db.query(*ql).join(SecretBase,SecretBase.id==Property.meta_id).filter(*fl).all()
        # 将结果转换为字典列表
        result_list = [row._asdict() for row in result]
        if len(result_list) > 0:
            result_list = [
                {k: decrypt_plan_text(v) if k in ['property_name', 'property_address','remarks'] else v for k, v in row.items()}
                for row in result_list
            ]
        return result_list
async def get_safety_deposit_box_trx(fl:List,db:Session,cb: Callable[[], bool]=None):
    if cb:
        p = await cb
        if p:
            result = db.query(SafetyDepositBox.id.label("safety_deposit_box_id"),SafetyDepositBox.safety_deposit_box_name,SafetyDepositBox.safety_deposit_box_open_method,SafetyDepositBox.safety_deposit_box_address,SafetyDepositBox.remarks).join(SecretBase,SecretBase.id==SafetyDepositBox.meta_id).filter(*fl).all()
            # 将结果转换为字典列表
            result_list = [row._asdict() for row in result]
            if len(result_list) > 0:
                result_list = [
                    {k: decrypt_plan_text(v) if k in ['safety_deposit_box_name', 'safety_deposit_box_open_method','safety_deposit_box_address','remarks'] else v for k, v in row.items()}
                    for row in result_list
                ]
            return result_list
        else:
            return []
    else:
        result = db.query(SafetyDepositBox.id.label("safety_deposit_box_id"),SafetyDepositBox.safety_deposit_box_name,SafetyDepositBox.safety_deposit_box_open_method,SafetyDepositBox.safety_deposit_box_address,SafetyDepositBox.remarks).join(SecretBase,SecretBase.id==SafetyDepositBox.meta_id).filter(*fl).all()
        # 将结果转换为字典列表
        result_list = [row._asdict() for row in result]
        if len(result_list) > 0:
            result_list = [
                {k: decrypt_plan_text(v) if k in ['safety_deposit_box_name', 'safety_deposit_box_open_method','safety_deposit_box_address','remarks'] else v for k, v in row.items()}
                for row in result_list
            ]
        return result_list
async def get_confidential_event_trx(fl:List,db:Session,cb: Callable[[], bool]=None):
    if cb:
        p = await cb
        if p:
            result = db.query(ConfidentialEvent.id.label("confidential_event_id"),ConfidentialEvent.event_name,ConfidentialEvent.event_details).join(SecretBase,SecretBase.id==ConfidentialEvent.meta_id).filter(*fl).all()
            # 将结果转换为字典列表
            result_list = [row._asdict() for row in result]
            if len(result_list) > 0:
                result_list = [
                    {k: decrypt_plan_text(v) if k in ['event_name', 'event_details'] else v for k, v in row.items()}
                    for row in result_list
                ]
            return result_list
        else:
            return []
    else:
        result = db.query(ConfidentialEvent.id.label("confidential_event_id"),ConfidentialEvent.event_name,ConfidentialEvent.event_details).join(SecretBase,SecretBase.id==ConfidentialEvent.meta_id).filter(*fl).all()
        # 将结果转换为字典列表
        result_list = [row._asdict() for row in result]
        if len(result_list) > 0:
            result_list = [
                {k: decrypt_plan_text(v) if k in ['event_name', 'event_details'] else v for k, v in row.items()}
                for row in result_list
            ]
        return result_list

# Delete
async def delete_bank_account_trx(id:int,user_id:str,db:Session):
    try:
        meta_id = db.query(BankAccount.meta_id).filter(BankAccount.id==id).first()
        if meta_id:
            meta_id = meta_id[0]
            wrap_delete_func(BankAccount,{"meta_id": meta_id},db,db.query(BankAccount).join(SecretBase,SecretBase.id==BankAccount.meta_id).filter(SecretBase.user_id==user_id,BankAccount.meta_id==meta_id).count()>0)
            wrap_delete_func(SecretBase,{"id": id,"user_id":user_id},db,db.query(SecretBase).filter(SecretBase.id==meta_id,SecretBase.user_id==user_id).count()>0)
            db.commit()
            return True
        else:
            return False
        
    except Exception as e:
        db.rollback()
        raise GeneralErrorExcpetion(str(e))
async def delete_property_trx(id:int,user_id:str,db:Session):
    try:
        meta_id = db.query(Property.meta_id).filter(Property.id==id).first()
        if meta_id:
            meta_id = meta_id[0]
            wrap_delete_func(Property,{"meta_id": meta_id},db,db.query(Property).join(SecretBase,SecretBase.id==Property.meta_id).filter(SecretBase.user_id==user_id,Property.meta_id==meta_id).count()>0)
            wrap_delete_func(SecretBase,{"id": id,"user_id":user_id},db,db.query(SecretBase).filter(SecretBase.id==meta_id,SecretBase.user_id==user_id).count()>0)
            db.commit()
            return True
        else:
            return False
    except Exception as e:
        db.rollback()
        raise GeneralErrorExcpetion(str(e))
async def delete_safety_deposit_box_trx(id:int,user_id:str,db:Session):
    try:
        meta_id = db.query(SafetyDepositBox.meta_id).filter(SafetyDepositBox.id==id).first()
        if meta_id:
            meta_id = meta_id[0]
            wrap_delete_func(SafetyDepositBox,{"meta_id": meta_id},db,db.query(SafetyDepositBox).join(SecretBase,SecretBase.id==SafetyDepositBox.meta_id).filter(SecretBase.user_id==user_id,SafetyDepositBox.meta_id==meta_id).count()>0)
            wrap_delete_func(SecretBase,{"id": id,"user_id":user_id},db,db.query(SecretBase).filter(SecretBase.id==meta_id,SecretBase.user_id==user_id).count()>0)
            db.commit()
            return True
        else:
            return False
    except Exception as e:
        db.rollback()
        raise GeneralErrorExcpetion(str(e))
async def delete_confidential_event_trx(id:int,user_id:str,db:Session):
    try:
        meta_id = db.query(ConfidentialEvent.meta_id).filter(ConfidentialEvent.id==id).first()
        if meta_id:
            meta_id = meta_id[0]
            wrap_delete_func(ConfidentialEvent,{"meta_id": meta_id},db,db.query(ConfidentialEvent).join(SecretBase,SecretBase.id==ConfidentialEvent.meta_id).filter(SecretBase.user_id==user_id,ConfidentialEvent.meta_id==meta_id).count()>0)
            wrap_delete_func(SecretBase,{"id": id,"user_id":user_id},db,db.query(SecretBase).filter(SecretBase.id==meta_id,SecretBase.user_id==user_id).count()>0)
            db.commit()
            return True
        else:
            return False

    except Exception as e:
        db.rollback()
        raise GeneralErrorExcpetion(str(e))
# Edit 
async def edit_bank_account_trx(user_id:str,id: int,updates:BankAccountBaseInputRequest, db: Session):
    updates = updates.model_dump()
    # encrypt_plan_text
    updates = {k: encrypt_plan_text(v) if k in ['bank_account_name', 'bank_account_number'] else v for k, v in updates.items()}
    return wrap_update_trx(BankAccount,{"id":id},updates,db,db.query(BankAccount).join(SecretBase,SecretBase.id==BankAccount.meta_id) .filter(BankAccount.id == id,SecretBase.user_id==user_id).count() > 0)

async def edit_property_trx(user_id:str,id: int,updates:PropertyBaseInputRequest, db: Session):
    updates = updates.model_dump()
    # encrypt_plan_text
    updates = {k: encrypt_plan_text(v) if k in ['property_name', 'property_address','remarks'] else v for k, v in updates.items()}
    return wrap_update_trx(Property,{"id":id},updates,db,db.query(Property).join(SecretBase,SecretBase.id==Property.meta_id) .filter(Property.id == id,SecretBase.user_id==user_id).count() > 0)

async def edit_safety_deposit_box_trx(user_id:str,id: int,updates:SafetyDepositBoxBaseInputRequest, db: Session):
    updates = updates.model_dump()
    # encrypt_plan_text
    updates = {k: encrypt_plan_text(v) if k in ['safety_deposit_box_name', 'safety_deposit_box_open_method','safety_deposit_box_address','remarks'] else v for k, v in updates.items()}
    return wrap_update_trx(SafetyDepositBox,{"id":id},updates,db,db.query(SafetyDepositBox).join(SecretBase,SecretBase.id==SafetyDepositBox.meta_id) .filter(SafetyDepositBox.id == id,SecretBase.user_id==user_id).count() > 0)

async def edit_confidential_event_trx(user_id:str,id: int,updates:ConfidentialEventBaseInputRequest, db: Session):
    updates = updates.model_dump()
    # encrypt_plan_text
    updates = {k: encrypt_plan_text(v) if k in ['event_name', 'event_details'] else v for k, v in updates.items()}
    return wrap_update_trx(ConfidentialEvent,{"id":id},updates,db,db.query(ConfidentialEvent).join(SecretBase,SecretBase.id==ConfidentialEvent.meta_id) .filter(ConfidentialEvent.id == id,SecretBase.user_id==user_id).count() > 0)


# Insert
async def create_secret_base(secert_data:SecretBaseInputRequest,db: Session)->int:
    insert_obj = SecretBase(**secert_data.model_dump())
    result = wrap_insert_mapping_func(db, insert_obj)
    return result.id

async def create_bank_account_trx(reqData:BankAccountBaseInputRequest,db: Session,cb: Callable[[], int]):
    try:
        id = await cb
        obj = reqData.model_dump()
        cloned_dict = {k: encrypt_plan_text(v) if k in ['bank_account_name','bank_account_number'] else v for k, v in obj.items()}
        insert_bank_account_obj = BankAccount(**cloned_dict,meta_id=id)
        result = wrap_insert_mapping_func(db, insert_bank_account_obj)        
        db.commit()
        db.refresh(result)
        return result.id
    except Exception as e:
        db.rollback()
        raise GeneralErrorExcpetion(str(e))
async def create_property_trx(reqData:PropertyBaseInputRequest,db: Session,cb: Callable[[], int]):
    try:
        id = await cb
        obj = reqData.model_dump()
        cloned_dict = {k: encrypt_plan_text(v) if k in ['property_name','property_address','remarks'] else v for k, v in obj.items()}   
        insert_property_obj = Property(**cloned_dict,meta_id=id)
        result = wrap_insert_mapping_func(db, insert_property_obj)
        db.commit()
        db.refresh(result)
        return result.id
    except Exception as e:
        db.rollback()
        raise GeneralErrorExcpetion(str(e))

async def create_safety_deposit_box_trx(reqData:SafetyDepositBoxBaseInputRequest,db: Session,cb: Callable[[], int]):
    try:
        id = await cb        
        obj = reqData.model_dump()
        cloned_dict = {k: encrypt_plan_text(v) if k in ['safety_deposit_box_name','safety_deposit_box_open_method','safety_deposit_box_address','remarks'] else v for k, v in obj.items()}   
        insert_safety_deposit_obj = SafetyDepositBox(**cloned_dict,meta_id=id)
        result = wrap_insert_mapping_func(db, insert_safety_deposit_obj)
        db.commit()
        db.refresh(result)
        return result.id
    except Exception as e:
        db.rollback()
        raise GeneralErrorExcpetion(str(e))

async def create_confidential_event_trx(reqData:ConfidentialEventBaseInputRequest,db: Session,cb: Callable[[], int]):
    try:
        id = await cb        
        obj = reqData.model_dump()
        cloned_dict = {k: encrypt_plan_text(v) if k in ['event_name','event_details'] else v for k, v in obj.items()}   
        insert_confidential_obj = ConfidentialEvent(**cloned_dict,meta_id=id)
        result = wrap_insert_mapping_func(db, insert_confidential_obj)
        db.commit()
        db.refresh(result)
        return result.id
    except Exception as e:
        db.rollback()
        raise GeneralErrorExcpetion(str(e))