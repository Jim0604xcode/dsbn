from sqlalchemy.orm import Session
from typing import List, NotRequired, Optional, TypedDict,Callable
from src.finalChapter.schemas import AshesBaseInputRequest, CeremonyPreferenceBaseInputRequest, CoffinBaseInputRequest, EnduringPowerOfAttorneyBaseInputRequest, FuneralBaseInputRequest, MedicalPreferenceBaseInputRequest, PalliativeCareBaseInputRequest
from src.finalChapter.models import Ashes, CeremonyPreference, Coffin, EnduringPowerOfAttorney, Funeral, MedicalPreference, PalliativeCare
from src.exceptions import DatabaseErrorException, GeneralErrorExcpetion
from src.transaction import wrap_insert_mapping_func, wrap_update_func, wrap_update_trx
from src.loggerServices import log_info
from typing import Literal
# Query
async def get_final_chapter_trx(user_id:str,db:Session,cb: Callable[[], bool]=None):
        if cb:
            p = await cb
            if p:
                palliative_care_query = db.query(
                    PalliativeCare.did_arrange.label("pc_did_arrange"),
                    PalliativeCare.contact_organization.label("pc_contact_organization"),
                    PalliativeCare.notes.label("pc_notes"),
                    PalliativeCare.updated_at.label("pc_updated_at"),
                ).filter(PalliativeCare.user_id == user_id)

                medical_preference_query = db.query(
                    MedicalPreference.did_arrange.label("mp_did_arrange"),
                    MedicalPreference.notes.label("mp_notes"),
                    MedicalPreference.updated_at.label("mp_updated_at"),
                ).filter(MedicalPreference.user_id == user_id)

                enduring_power_of_attorney_query = db.query(
                    EnduringPowerOfAttorney.did_arrange.label("epoa_did_arrange"),
                    EnduringPowerOfAttorney.notes.label("epoa_notes"),
                    EnduringPowerOfAttorney.updated_at.label("epoa_updated_at"),
                ).filter(EnduringPowerOfAttorney.user_id == user_id)

                coffin_query = db.query(
                    Coffin.did_arrange.label("c_did_arrange"),
                    Coffin.notes.label("c_notes"),
                    Coffin.updated_at.label("c_updated_at"),
                    Coffin.custom.label("c_custom")
                ).filter(Coffin.user_id == user_id)
                ceremony_query = db.query(
                    CeremonyPreference.did_arrange.label("cp_did_arrange"),
                    CeremonyPreference.notes.label("cp_notes"),
                    CeremonyPreference.updated_at.label("cp_updated_at"),
                    CeremonyPreference.custom.label("cp_custom")
                ).filter(CeremonyPreference.user_id == user_id)

                funeral_query = db.query(
                    Funeral.did_arrange.label("f_did_arrange"),
                    Funeral.notes.label("f_notes"),
                    Funeral.updated_at.label("f_updated_at"),
                    Funeral.custom.label("f_custom")
                ).filter(Funeral.user_id == user_id)
                
                ashes_query = db.query(
                    Ashes.did_arrange.label("a_did_arrange"),
                    Ashes.notes.label("a_notes"),
                    Ashes.updated_at.label("a_updated_at"),
                    Ashes.custom.label("a_custom")
                ).filter(Ashes.user_id == user_id)

                # 執行查詢
                palliative_care = palliative_care_query.all()
                palliative_care_list = [row._asdict() for row in palliative_care]
                palliative_care_result = {**palliative_care_list[0],**{"pc_count":1}} if palliative_care_list else {"pc_count":0}
        
                medical_preference = medical_preference_query.all()
                medical_preference_list = [row._asdict() for row in medical_preference]
                medical_preference_result = {**medical_preference_list[0],**{"mp_count":1}} if medical_preference_list else {"mp_count":0}
                
                enduring_power_of_attorney = enduring_power_of_attorney_query.all()
                enduring_power_of_attorney_list = [row._asdict() for row in enduring_power_of_attorney]
                enduring_power_of_attorney_result = {**enduring_power_of_attorney_list[0],**{"epoa_count":1}} if enduring_power_of_attorney_list else {"epoa_count":0}


                coffin = coffin_query.all()
                coffin_list = [row._asdict() for row in coffin]
                coffin_result = {**coffin_list[0],**{"c_count":1}} if coffin_list else {"c_count":0}
                
                ceremony = ceremony_query.all()
                ceremony_list = [row._asdict() for row in ceremony]
                ceremony_result = {**ceremony_list[0],**{"cp_count":1}} if ceremony_list else {"cp_count":0}

                funeral = funeral_query.all()
                funeral_list = [row._asdict() for row in funeral]
                funeral_result = {**funeral_list[0],**{"f_count":1}} if funeral_list else {"f_count":0}

                ashes = ashes_query.all()
                ashes_list = [row._asdict() for row in ashes]
                ashes_result = {**ashes_list[0],**{"a_count":1}} if ashes_list else {"a_count":0}


                combined_results = {**palliative_care_result,**medical_preference_result,**enduring_power_of_attorney_result,**coffin_result,**ceremony_result,**funeral_result,**ashes_result}
                return combined_results
            
            else:
                # You have no permission
                return {**{"pc_count":0},**{"mp_count":0},**{"epoa_count":0},**{"c_count":0},**{"cp_count":0},**{"f_count":0},**{"a_count":0}}     
        else:
            
            palliative_care_query = db.query(
                PalliativeCare.did_arrange.label("pc_did_arrange"),
                PalliativeCare.contact_organization.label("pc_contact_organization"),
                PalliativeCare.notes.label("pc_notes"),
                PalliativeCare.updated_at.label("pc_updated_at"),
            ).filter(PalliativeCare.user_id == user_id)

            medical_preference_query = db.query(
                MedicalPreference.did_arrange.label("mp_did_arrange"),
                MedicalPreference.notes.label("mp_notes"),
                MedicalPreference.updated_at.label("mp_updated_at"),
            ).filter(MedicalPreference.user_id == user_id)

            enduring_power_of_attorney_query = db.query(
                EnduringPowerOfAttorney.did_arrange.label("epoa_did_arrange"),
                EnduringPowerOfAttorney.notes.label("epoa_notes"),
                EnduringPowerOfAttorney.updated_at.label("epoa_updated_at"),
            ).filter(EnduringPowerOfAttorney.user_id == user_id)

            coffin_query = db.query(
                Coffin.did_arrange.label("c_did_arrange"),
                Coffin.notes.label("c_notes"),
                Coffin.updated_at.label("c_updated_at"),
                Coffin.custom.label("c_custom")
            ).filter(Coffin.user_id == user_id)
            ceremony_query = db.query(
                CeremonyPreference.did_arrange.label("cp_did_arrange"),
                CeremonyPreference.notes.label("cp_notes"),
                CeremonyPreference.updated_at.label("cp_updated_at"),
                CeremonyPreference.custom.label("cp_custom")
            ).filter(CeremonyPreference.user_id == user_id)

            funeral_query = db.query(
                Funeral.did_arrange.label("f_did_arrange"),
                Funeral.notes.label("f_notes"),
                Funeral.updated_at.label("f_updated_at"),
                Funeral.custom.label("f_custom")
            ).filter(Funeral.user_id == user_id)
                
            ashes_query = db.query(
                Ashes.did_arrange.label("a_did_arrange"),
                Ashes.notes.label("a_notes"),
                Ashes.updated_at.label("a_updated_at"),
                Ashes.custom.label("a_custom")
            ).filter(Ashes.user_id == user_id)

            # 執行查詢
            palliative_care = palliative_care_query.all()
            palliative_care_list = [row._asdict() for row in palliative_care]
            palliative_care_result = {**palliative_care_list[0],**{"pc_count":1}} if palliative_care_list else {"pc_count":0}
        
            medical_preference = medical_preference_query.all()
            medical_preference_list = [row._asdict() for row in medical_preference]
            medical_preference_result = {**medical_preference_list[0],**{"mp_count":1}} if medical_preference_list else {"mp_count":0}
                
            enduring_power_of_attorney = enduring_power_of_attorney_query.all()
            enduring_power_of_attorney_list = [row._asdict() for row in enduring_power_of_attorney]
            enduring_power_of_attorney_result = {**enduring_power_of_attorney_list[0],**{"epoa_count":1}} if enduring_power_of_attorney_list else {"epoa_count":0}


            coffin = coffin_query.all()
            coffin_list = [row._asdict() for row in coffin]
            coffin_result = {**coffin_list[0],**{"c_count":1}} if coffin_list else {"c_count":0}
                
            ceremony = ceremony_query.all()
            ceremony_list = [row._asdict() for row in ceremony]
            ceremony_result = {**ceremony_list[0],**{"cp_count":1}} if ceremony_list else {"cp_count":0}

            funeral = funeral_query.all()
            funeral_list = [row._asdict() for row in funeral]
            funeral_result = {**funeral_list[0],**{"f_count":1}} if funeral_list else {"f_count":0}

            ashes = ashes_query.all()
            ashes_list = [row._asdict() for row in ashes]
            ashes_result = {**ashes_list[0],**{"a_count":1}} if ashes_list else {"a_count":0}


            combined_results = {**palliative_care_result,**medical_preference_result,**enduring_power_of_attorney_result,**coffin_result,**ceremony_result,**funeral_result,**ashes_result}
            return combined_results

async def get_palliative_care_trx(fl: List,db:Session):
        result = db.query(PalliativeCare.did_arrange,PalliativeCare.contact_organization,PalliativeCare.notes,PalliativeCare.updated_at).filter(*fl).all()
        result_list = [row._asdict() for row in result]
        return result_list[0] if result_list else {}

async def get_medical_preference_trx(fl: List,db:Session):
        result = db.query(MedicalPreference.did_arrange,MedicalPreference.notes,MedicalPreference.updated_at).filter(*fl).all()
        result_list = [row._asdict() for row in result]
        return result_list[0] if result_list else {}

async def get_enduring_power_of_attorney_trx(fl: List,db:Session):
        result = db.query(EnduringPowerOfAttorney.did_arrange,EnduringPowerOfAttorney.notes,EnduringPowerOfAttorney.updated_at).filter(*fl).all()
        result_list = [row._asdict() for row in result]
        return result_list[0] if result_list else {}


async def get_ceremony_preference_trx(fl: List,db:Session):
        result = db.query(CeremonyPreference.did_arrange,CeremonyPreference.notes,CeremonyPreference.updated_at,CeremonyPreference.custom).filter(*fl).all()
        result_list = [row._asdict() for row in result]
        return result_list[0] if result_list else {}

async def get_coffin_trx(fl: List,db:Session):
        result = db.query(Coffin.did_arrange,Coffin.notes,Coffin.updated_at,Coffin.custom).filter(*fl).all()
        result_list = [row._asdict() for row in result]
        return result_list[0] if result_list else {}

async def get_funeral_trx(fl: List,db:Session):
        result = db.query(Funeral.did_arrange,Funeral.notes,Funeral.updated_at,Funeral.custom).filter(*fl).all()
        result_list = [row._asdict() for row in result]
        return result_list[0] if result_list else {}

async def get_ashes_trx(fl: List,db:Session):
        result = db.query(Ashes.did_arrange,Ashes.notes,Ashes.updated_at,Ashes.custom).filter(*fl).all()
        result_list = [row._asdict() for row in result]
        return result_list[0] if result_list else {}


# Edit 
# async def edit_push_notification_trx(user_id:str,updates:PushNotificationBaseInputRequest, db: Session):
#     device_uuid = updates.device_uuid
#     updates = updates.model_dump()
#     return wrap_update_trx(PushNotification,{"user_id":user_id,"device_uuid":device_uuid},updates,db,db.query(PushNotification).filter(PushNotification.user_id == user_id,PushNotification.device_uuid==device_uuid).count() > 0)

# Insert
async def create_palliative_care_trx(reqData: PalliativeCareBaseInputRequest,user_id: str, db: Session):
    try:
        fl:List = [PalliativeCare.user_id == user_id]
        row = db.query(PalliativeCare).filter(*fl).first()
        if not row:
            insert_obj = PalliativeCare(**reqData.model_dump(include={'did_arrange','contact_organization','notes','updated_at'}),user_id=user_id)
            res = wrap_insert_mapping_func(db, insert_obj)
            db.commit()
            return res.id
        else:
            updates = reqData.model_dump(include={'did_arrange','contact_organization','notes','updated_at'})
            wrap_update_func(PalliativeCare,{"user_id":user_id},updates,db,True)
            db.commit()
            return row.id
    except Exception as e:
        db.rollback()
        raise GeneralErrorExcpetion(str(e))            


async def create_medical_preference_trx(reqData: MedicalPreferenceBaseInputRequest,user_id: str, db: Session):
    try:
        fl:List = [MedicalPreference.user_id == user_id]
        row = db.query(MedicalPreference).filter(*fl).first()
        if not row:
            insert_obj = MedicalPreference(**reqData.model_dump(include={'did_arrange','notes','updated_at'}),user_id=user_id)
            res = wrap_insert_mapping_func(db, insert_obj)
            db.commit()
            return res.id
        else:
            updates = reqData.model_dump(include={'did_arrange','notes','updated_at'})
            wrap_update_func(MedicalPreference,{"user_id":user_id},updates,db,True)
            db.commit()
            return row.id
    except Exception as e:
        db.rollback()
        raise GeneralErrorExcpetion(str(e))            


async def create_enduring_power_of_attorney_trx(reqData: EnduringPowerOfAttorneyBaseInputRequest,user_id: str, db: Session):
    try:
        fl:List = [EnduringPowerOfAttorney.user_id == user_id]
        row = db.query(EnduringPowerOfAttorney).filter(*fl).first()
        if not row:
            insert_obj = EnduringPowerOfAttorney(**reqData.model_dump(include={'did_arrange','notes','updated_at'}),user_id=user_id)
            res = wrap_insert_mapping_func(db, insert_obj)
            db.commit()
            return res.id
        else:
            updates = reqData.model_dump(include={'did_arrange','notes','updated_at'})
            wrap_update_func(EnduringPowerOfAttorney,{"user_id":user_id},updates,db,True)
            db.commit()
            return row.id
    except Exception as e:
        db.rollback()
        raise GeneralErrorExcpetion(str(e))            


async def create_ceremony_preference_trx(reqData: CeremonyPreferenceBaseInputRequest,user_id: str, db: Session):
    try:
        fl:List = [CeremonyPreference.user_id == user_id]
        row = db.query(CeremonyPreference).filter(*fl).first()
        if not row:
            insert_obj = CeremonyPreference(**reqData.model_dump(include={'did_arrange','notes','custom','updated_at'}),user_id=user_id)
            res = wrap_insert_mapping_func(db, insert_obj)
            db.commit()
            return res.id
        else:
            updates = reqData.model_dump(include={'did_arrange','notes','custom','updated_at'})
            wrap_update_func(CeremonyPreference,{"user_id":user_id},updates,db,True)
            db.commit()
            return row.id
    except Exception as e:
        db.rollback()
        raise GeneralErrorExcpetion(str(e))            

async def create_coffin_trx(reqData: CoffinBaseInputRequest,user_id: str, db: Session):
    try:
        fl:List = [Coffin.user_id == user_id]
        row = db.query(Coffin).filter(*fl).first()
        if not row:
            insert_obj = Coffin(**reqData.model_dump(include={'did_arrange','notes','custom','updated_at'}),user_id=user_id)
            res = wrap_insert_mapping_func(db, insert_obj)
            db.commit()
            return res.id
        else:
            updates = reqData.model_dump(include={'did_arrange','notes','custom','updated_at'})
            wrap_update_func(Coffin,{"user_id":user_id},updates,db,True)
            db.commit()
            return row.id
    except Exception as e:
        db.rollback()
        raise GeneralErrorExcpetion(str(e))            


async def create_funeral_trx(reqData: FuneralBaseInputRequest,user_id: str, db: Session):
    try:
        fl:List = [Funeral.user_id == user_id]
        row = db.query(Funeral).filter(*fl).first()
        if not row:
            insert_obj = Funeral(**reqData.model_dump(include={'did_arrange','notes','custom','updated_at'}),user_id=user_id)
            res = wrap_insert_mapping_func(db, insert_obj)
            db.commit()
            return res.id
        else:
            updates = reqData.model_dump(include={'did_arrange','notes','custom','updated_at'})
            wrap_update_func(Funeral,{"user_id":user_id},updates,db,True)
            db.commit()
            return row.id
    except Exception as e:
        db.rollback()
        raise GeneralErrorExcpetion(str(e))            

async def create_ashes_trx(reqData: AshesBaseInputRequest,user_id: str, db: Session):
    try:
        fl:List = [Ashes.user_id == user_id]
        row = db.query(Ashes).filter(*fl).first()
        if not row:
            insert_obj = Ashes(**reqData.model_dump(include={'did_arrange','notes','custom','updated_at'}),user_id=user_id)
            res = wrap_insert_mapping_func(db, insert_obj)
            db.commit()
            return res.id
        else:
            updates = reqData.model_dump(include={'did_arrange','notes','custom','updated_at'})
            wrap_update_func(Ashes,{"user_id":user_id},updates,db,True)
            db.commit()
            return row.id
    except Exception as e:
        db.rollback()
        raise GeneralErrorExcpetion(str(e))            
