from sqlalchemy.orm import Session
from typing import List, NotRequired, Optional, TypedDict,Callable
from src.personalLifeOverviewChart.schemas import DescribeYourselfTenSentencesBaseInputRequest,ValueOfLifeBaseInputRequest,EpitaphBaseInputRequest,LifeInsightsBaseInputRequest,FavoriteHeadshotBaseInputRequest
from src.personalLifeOverviewChart.models import ValueOfLife,DescribeYourselfTenSentences,Epitaph,FavoriteHeadshot,LifeInsights
from src.exceptions import DatabaseErrorException, GeneralErrorExcpetion
from src.transaction import wrap_delete_func,wrap_insert_mapping_func, wrap_update_func, wrap_update_trx
from src.loggerServices import log_info
from typing import Literal
from fastapi import UploadFile
from src.oss.service import upload_multiple_files,download_single_file,delete_single_file
from src.oss.model import FavoriteHeadshotMappingDict
# Query
async def get_describe_yourself_ten_sentences_trx(fl: List, db: Session,cb: Callable[[], bool]=None):
    if cb:
        p = await cb
        if p:
            result = db.query(DescribeYourselfTenSentences.id.label("describe_yourself_ten_sentences_id"),DescribeYourselfTenSentences.content,DescribeYourselfTenSentences.updated_at).filter(*fl).all()
            # 将结果转换为字典列表
            result_list = [row._asdict() for row in result]
            return result_list
        else:
            return []
    else:
        result = db.query(DescribeYourselfTenSentences.id.label("describe_yourself_ten_sentences_id"),DescribeYourselfTenSentences.content,DescribeYourselfTenSentences.updated_at).filter(*fl).all()
    
        # 将结果转换为字典列表
        result_list = [row._asdict() for row in result]
        return result_list

async def get_single_describe_yourself_ten_sentences_trx(fl:List,db:Session):
    result = db.query(DescribeYourselfTenSentences.id.label("describe_yourself_ten_sentences_id"),DescribeYourselfTenSentences.content,DescribeYourselfTenSentences.updated_at).filter(*fl).all()
    result_list = [row._asdict() for row in result]
    return result_list[0] if result_list else {}


async def get_value_of_life_trx(fl: List, db: Session,cb: Callable[[], bool]=None):
    if cb:
        p = await cb
        if p:
            result = db.query(ValueOfLife.id.label("value_of_life_id"),ValueOfLife.content,ValueOfLife.updated_at).filter(*fl).all()
            # 将结果转换为字典列表
            result_list = [row._asdict() for row in result]
            return result_list
        else:
            return []
    else:
        result = db.query(ValueOfLife.id.label("value_of_life_id"),ValueOfLife.content,ValueOfLife.updated_at).filter(*fl).all()
    
        # 将结果转换为字典列表
        result_list = [row._asdict() for row in result]
        return result_list

async def get_single_value_of_life_trx(fl:List,db:Session):
    result = db.query(ValueOfLife.id.label("value_of_life_id"),ValueOfLife.content,ValueOfLife.updated_at).filter(*fl).all()
    result_list = [row._asdict() for row in result]
    return result_list[0] if result_list else {}


async def get_life_insights_trx(fl: List, db: Session,cb: Callable[[], bool]=None):
    if cb:
        p = await cb
        if p:
            result = db.query(LifeInsights.id.label("life_insights_id"),LifeInsights.content,LifeInsights.updated_at).filter(*fl).all()
            # 将结果转换为字典列表
            result_list = [row._asdict() for row in result]
            return result_list
        else:
            return []
    else:
        result = db.query(LifeInsights.id.label("life_insights_id"),LifeInsights.content,LifeInsights.updated_at).filter(*fl).all()
    
        # 将结果转换为字典列表
        result_list = [row._asdict() for row in result]
        return result_list

async def get_single_life_insights_trx(fl:List,db:Session):
    result = db.query(LifeInsights.id.label("life_insights_id"),LifeInsights.content,LifeInsights.updated_at).filter(*fl).all()
    result_list = [row._asdict() for row in result]
    return result_list[0] if result_list else {}

async def get_epitaph_trx(fl: List, db: Session,cb: Callable[[], bool]=None):
    if cb:
        p = await cb
        if p:
            result = db.query(Epitaph.id.label("epitaph_id"),Epitaph.content,Epitaph.updated_at).filter(*fl).all()
            # 将结果转换为字典列表
            result_list = [row._asdict() for row in result]
            return result_list
        else:
            return []
    else:
        result = db.query(Epitaph.id.label("epitaph_id"),Epitaph.content,Epitaph.updated_at).filter(*fl).all()
    
        # 将结果转换为字典列表
        result_list = [row._asdict() for row in result]
        return result_list

async def get_single_epitaph_trx(fl:List,db:Session):
    result = db.query(Epitaph.id.label("epitaph_id"),Epitaph.content,Epitaph.updated_at).filter(*fl).all()
    result_list = [row._asdict() for row in result]
    return result_list[0] if result_list else {}


async def get_favorite_headshot_trx(fl: List, db: Session,cb: Callable[[], bool]=None):
    try:
        if cb:
            p = await cb
            if p:
                result = db.query(FavoriteHeadshot.id.label("favorite_headshot_id"),FavoriteHeadshot.picture,FavoriteHeadshot.ago,FavoriteHeadshot.updated_at).filter(*fl).all()
                # 将结果转换为字典列表
                result_list = [row._asdict() for row in result]
                if len(result_list) > 0:
                    # list(map(lambda x: {key: download_single_file(value, 3600) if key in {Keys.KEY1.value, Keys.KEY2.value,Keys.KEY3.value,Keys.KEY4.value} else value for key, value in x.items()}, result_list))
                    for row in result_list:
                        for k in row:
                            if k in "picture":
                                r = await download_single_file(row[k])
                                row[k] = r
                else:
                    return []
                return result_list
            else:
                return []
        else:
            result = db.query(FavoriteHeadshot.id.label("favorite_headshot_id"),FavoriteHeadshot.picture,FavoriteHeadshot.ago,FavoriteHeadshot.updated_at).filter(*fl).all()
        
            # 将结果转换为字典列表
            result_list = [row._asdict() for row in result]
            if len(result_list) > 0:
                # list(map(lambda x: {key: download_single_file(value, 3600) if key in {Keys.KEY1.value, Keys.KEY2.value,Keys.KEY3.value,Keys.KEY4.value} else value for key, value in x.items()}, result_list))
                for row in result_list:
                    for k in row:
                        if k in "picture":
                            r = await download_single_file(row[k])
                            row[k] = r
            else:
                return []
            return result_list
    except Exception as e:        
        raise GeneralErrorExcpetion(str(e))

# Edit # Delete
async def edit_describe_yourself_ten_sentences_trx(id:int,user_id:str,updates:DescribeYourselfTenSentencesBaseInputRequest,db: Session):
    updates = updates.model_dump()
    return wrap_update_trx(DescribeYourselfTenSentences,{"id":id},updates,db,db.query(DescribeYourselfTenSentences).filter(DescribeYourselfTenSentences.id == id,DescribeYourselfTenSentences.user_id==user_id).count() > 0)
async def delete_describe_yourself_ten_sentences_trx(id:int, user_id:str, db:Session):
    try:
        wrap_delete_func(DescribeYourselfTenSentences,{"id": id},db,db.query(DescribeYourselfTenSentences).filter(DescribeYourselfTenSentences.id==id,DescribeYourselfTenSentences.user_id==user_id).count()>0)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        raise GeneralErrorExcpetion(str(e))

async def edit_value_of_life_trx(id:int,user_id:str,updates:ValueOfLifeBaseInputRequest,db: Session):
    updates = updates.model_dump()
    return wrap_update_trx(ValueOfLife,{"id":id},updates,db,db.query(ValueOfLife).filter(ValueOfLife.id == id,ValueOfLife.user_id==user_id).count() > 0)
async def delete_value_of_life_trx(id:int, user_id:str, db:Session):
    try:
        wrap_delete_func(ValueOfLife,{"id": id},db,db.query(ValueOfLife).filter(ValueOfLife.id==id,ValueOfLife.user_id==user_id).count()>0)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        raise GeneralErrorExcpetion(str(e))


async def edit_life_insights_trx(id:int,user_id:str,updates:LifeInsightsBaseInputRequest,db: Session):
    updates = updates.model_dump()
    return wrap_update_trx(LifeInsights,{"id":id},updates,db,db.query(LifeInsights).filter(LifeInsights.id == id,LifeInsights.user_id==user_id).count() > 0)
async def delete_life_insights_trx(id:int, user_id:str, db:Session):
    try:
        wrap_delete_func(LifeInsights,{"id": id},db,db.query(LifeInsights).filter(LifeInsights.id==id,LifeInsights.user_id==user_id).count()>0)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        raise GeneralErrorExcpetion(str(e))

async def edit_epitaph_trx(id:int,user_id:str,updates:EpitaphBaseInputRequest,db: Session):
    updates = updates.model_dump()
    return wrap_update_trx(Epitaph,{"id":id},updates,db,db.query(Epitaph).filter(Epitaph.id == id,Epitaph.user_id==user_id).count() > 0)
async def delete_epitaph_trx(id:int, user_id:str, db:Session):
    try:
        wrap_delete_func(Epitaph,{"id": id},db,db.query(Epitaph).filter(Epitaph.id==id,Epitaph.user_id==user_id).count()>0)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        raise GeneralErrorExcpetion(str(e))

# async def edit_favorite_headshot_ago_trx(id:int,user_id:str,updates:FavoriteHeadshotAgoBaseInputRequest,db: Session):
#     updates = updates.model_dump()
#     return wrap_update_trx(FavoriteHeadshot,{"id":id},updates,db,db.query(FavoriteHeadshot).filter(FavoriteHeadshot.id == id,FavoriteHeadshot.user_id==user_id).count() > 0)

async def edit_favorite_headshot_trx(id:int,reqData,ossData,user_id: str, db: Session,files: List[UploadFile]):
    try:
        # delete oss
        result = db.query(FavoriteHeadshot.picture).filter(FavoriteHeadshot.id==id,FavoriteHeadshot.user_id==user_id).all()
        result_list = [row._asdict() for row in result]
        # 處理文件刪除
        for row in result_list:
            for file_path in row.values():
                delete_single_file(file_path)

        # upload DB
        new_oss_mapping_data:FavoriteHeadshotMappingDict =  await upload_multiple_files(user_id, files, "images","personal_life_overview_chart",ossData)
        # return new_oss_mapping_data
        favHeadshotData:FavoriteHeadshotBaseInputRequest = FavoriteHeadshotBaseInputRequest(**new_oss_mapping_data,**reqData)
        
        updates = favHeadshotData.model_dump()
        wrap_update_func(FavoriteHeadshot,{"id":id},updates,db,True)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        raise GeneralErrorExcpetion(str(e))
    
async def delete_favorite_headshot_trx(id:int, user_id:str, db:Session):
    try:
        # delete oss
        result = db.query(FavoriteHeadshot.picture).filter(FavoriteHeadshot.id==id,FavoriteHeadshot.user_id==user_id).all()
        result_list = [row._asdict() for row in result]
        # 處理文件刪除
        for row in result_list:
            for file_path in row.values():
                delete_single_file(file_path)
        wrap_delete_func(FavoriteHeadshot,{"id": id},db,db.query(FavoriteHeadshot).filter(FavoriteHeadshot.id==id,FavoriteHeadshot.user_id==user_id).count()>0)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        raise GeneralErrorExcpetion(str(e))


# Insert
async def create_describe_yourself_ten_sentences_trx(reqData: DescribeYourselfTenSentencesBaseInputRequest,user_id: str, db: Session):
    try:
        fl:List = [DescribeYourselfTenSentences.user_id == user_id]
        count = db.query(DescribeYourselfTenSentences).filter(*fl).count()
        if count > 9:
            raise Exception("Maximum 10 sentences")
        insert_obj = DescribeYourselfTenSentences(**reqData.model_dump(include={'content','updated_at'}),user_id=user_id)
        res = wrap_insert_mapping_func(db, insert_obj)
        db.commit()
        return res.id
    except Exception as e:
        db.rollback()
        raise GeneralErrorExcpetion(str(e))            


async def create_value_of_life_trx(reqData:ValueOfLifeBaseInputRequest,user_id: str, db: Session):
    try:
        # fl:List = [DescribeYourselfTenSentences.user_id == user_id]
        # count = db.query(DescribeYourselfTenSentences).filter(*fl).count()
        # if count > 9:
        #     raise Exception("Maximum 10 sentences")
        insert_obj = ValueOfLife(**reqData.model_dump(include={'content','updated_at'}),user_id=user_id)
        res = wrap_insert_mapping_func(db, insert_obj)
        db.commit()
        return res.id
    except Exception as e:
        db.rollback()
        raise GeneralErrorExcpetion(str(e))            

async def create_life_insights_trx(reqData:LifeInsightsBaseInputRequest,user_id: str, db: Session):
    try:
        # fl:List = [DescribeYourselfTenSentences.user_id == user_id]
        # count = db.query(DescribeYourselfTenSentences).filter(*fl).count()
        # if count > 9:
        #     raise Exception("Maximum 10 sentences")
        insert_obj = LifeInsights(**reqData.model_dump(include={'content','updated_at'}),user_id=user_id)
        res = wrap_insert_mapping_func(db, insert_obj)
        db.commit()
        return res.id
    except Exception as e:
        db.rollback()
        raise GeneralErrorExcpetion(str(e))            


async def create_epitaph_trx(reqData:EpitaphBaseInputRequest,user_id: str, db: Session):
    try:
        # fl:List = [DescribeYourselfTenSentences.user_id == user_id]
        # count = db.query(DescribeYourselfTenSentences).filter(*fl).count()
        # if count > 9:
        #     raise Exception("Maximum 10 sentences")
        insert_obj = Epitaph(**reqData.model_dump(include={'content','updated_at'}),user_id=user_id)
        res = wrap_insert_mapping_func(db, insert_obj)
        db.commit()
        return res.id
    except Exception as e:
        db.rollback()
        raise GeneralErrorExcpetion(str(e))            

async def create_favorite_headshot_trx(reqData,ossData,user_id: str, db: Session,files: List[UploadFile]):
    try:
        # fl:List = [DescribeYourselfTenSentences.user_id == user_id]
        # count = db.query(DescribeYourselfTenSentences).filter(*fl).count()
        # if count > 9:
        #     raise Exception("Maximum 10 sentences")
        # upload oss
        new_oss_mapping_data:FavoriteHeadshotMappingDict =  await upload_multiple_files(user_id, files, "images","personal_life_overview_chart",ossData)
        # return new_oss_mapping_data
        favHeadshotData:FavoriteHeadshotBaseInputRequest = FavoriteHeadshotBaseInputRequest(**new_oss_mapping_data,**reqData)
        # favHeadshotData:FavoriteHeadshotBaseInputRequest = FavoriteHeadshotBaseInputRequest(**{"picture":"test"},**{"ago":14,"updated_at":"2025-02-13T01:34:14.991Z"})
        # return favHeadshotData
        insert_obj = FavoriteHeadshot(**favHeadshotData.model_dump(include={'picture','ago','updated_at'}),user_id=user_id)
        res = wrap_insert_mapping_func(db, insert_obj)
        db.commit()
        return res.id
    except Exception as e:
        db.rollback()
        raise GeneralErrorExcpetion(str(e))            
