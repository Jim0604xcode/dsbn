from typing import List
from fastapi import UploadFile
from sqlalchemy.orm import Session
from src.auth.models import PhoneMaster
from src.adminAuth.models import Staff
from src.exceptions import GeneralErrorExcpetion
from src.passAway.schemas import (PassAwayInfoMetaBaseInputRequest, PrePassAwayInfoMetaBaseInputRequest)
from src.passAway.models import (PassAwayInfo)
from src.oss.service import upload_multiple_files
from src.transaction import wrap_delete_func, wrap_insert_mapping_func, wrap_update_func
from src.payment.schemas import (PreTransactionBaseInputRequest)
from src.payment.models import (PaymentStatusEnum, Transaction)

from src.passAway.models import (ApprovalStatusEnum, PassAwayInfo, PassAwayInfoMeta)
from src.utils.smsProvider import send_sms
# Delete

# Edit
    
# Insert

async def bind_passaway_file(id:int, user_id:str, db: Session, files: List[UploadFile], oss_data):
    try:
        # upload oss
        new_oss_mapping_data = await upload_multiple_files(user_id, files, "images", "pass_away", oss_data, True)
        passAwayData = {**new_oss_mapping_data}
        # log_info(f'dict for new_oss_mapping_data and req_data - {new_oss_mapping_data}')
        # update pai row
        wrap_update_func(PassAwayInfo,{"id":id},passAwayData,db,True)
        
        
        
        
        db.commit()
        return passAwayData
    except Exception as e:
        db.rollback()
        raise GeneralErrorExcpetion(str(e))

async def create_pass_away_trx(ui_id:int, inheritor_id:str, db: Session, req_data, payment_data):
    try:
        # check whether pai row exist or not? 
        
        if db.query(PassAwayInfo).filter(PassAwayInfo.meta_id == ui_id).count() == 0:
            payment_data:PreTransactionBaseInputRequest = PreTransactionBaseInputRequest(**payment_data,**{"payment_status":PaymentStatusEnum.PENDING})
            insert_transaction_obj = Transaction(**payment_data.model_dump(include={"payment_service_provider","payment_type","product_id","payment_status"}),user_id=inheritor_id)
            t_id = wrap_insert_mapping_func(db, insert_transaction_obj)
            
            # insert pai row with basic data, without file info

            insert_pass_away_obj = PassAwayInfo(**req_data, meta_id=ui_id, transaction_id=t_id.id)
            result = wrap_insert_mapping_func(db, insert_pass_away_obj)
        else:
            
            p = db.query(PassAwayInfo.id).filter(PassAwayInfo.meta_id == ui_id).first()
            if p:
                pai_id = p._asdict()['id']
            else:
                pai_id = None  # or handle the "not found" case
        
            t = db.query(Transaction.id).filter(PassAwayInfo.id==pai_id,Transaction.user_id == inheritor_id,Transaction.payment_status == "PENDING").first()
            if t:
                transaction_id = t._asdict()['id']
            else:
                transaction_id = None  # or handle the "not found" case
            
            # delete pai row
            wrap_delete_func(PassAwayInfo,{"id": pai_id},db)
            # delete t row
            wrap_delete_func(Transaction,{"id": transaction_id},db)
            
            # insert t row
            payment_data:PreTransactionBaseInputRequest = PreTransactionBaseInputRequest(**payment_data,**{"payment_status":PaymentStatusEnum.PENDING})
            insert_transaction_obj = Transaction(**payment_data.model_dump(include={"payment_service_provider","payment_type","product_id","payment_status"}),user_id=inheritor_id)
            t_id = wrap_insert_mapping_func(db, insert_transaction_obj)
            
            # insert pai row with basic data, without file info
            insert_pass_away_obj = PassAwayInfo(**req_data, meta_id=ui_id, transaction_id=t_id.id)
            result = wrap_insert_mapping_func(db, insert_pass_away_obj)
        

        # by pass payment logic (TODO delete after google payment finished)
        await byPassPaymentLogic(pai_id=result.id,db=db)

        db.commit()
        return result.id
    except Exception as e:
        db.rollback()
        raise GeneralErrorExcpetion(str(e))    



async def byPassPaymentLogic(pai_id:int,db:Session):
    # log_info('pai_id',pai_id)
    data:PrePassAwayInfoMetaBaseInputRequest = PrePassAwayInfoMetaBaseInputRequest(**{"approval_status":"VERIFY"})
    insert_pass_away_meta_obj = PassAwayInfoMeta(**data.model_dump(),meta_id=pai_id)
    wrap_insert_mapping_func(db, insert_pass_away_meta_obj)

    
    result = db.query(Staff.phone_number).filter(Staff.role=='admin',Staff.phone_number.is_not(None)).all()
    result_list = [row._asdict() for row in result]
    if len(result_list) > 0:
        for row in result_list:
            phone_number = row.get("phone_number", None)
            if phone_number:
                send_sms(phone_number,f"Deep Soul app has someone submit proof of dead document, please check - passaway-info-id {pai_id}")


    
