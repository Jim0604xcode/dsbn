from typing import List
from fastapi import APIRouter, Depends, Request,UploadFile, Form
from src.exceptions import DatabaseErrorException, handle_exceptions
from src.schemas import ApiSuccessResponseModel
from src.models import get_error_response_model
from src.database import get_db
from sqlalchemy.orm import Session
from src.utils.response import create_success_response
from src.personalLifeOverviewChart.schemas import DescribeYourselfTenSentencesBaseInputRequest,ValueOfLifeBaseInputRequest,EpitaphBaseInputRequest,LifeInsightsBaseInputRequest,FavoriteHeadshotBaseInputRequest
from src.personalLifeOverviewChart.service import create_describe_yourself_ten_sentences_trx, create_epitaph_trx, create_favorite_headshot_trx, create_life_insights_trx, create_value_of_life_trx, delete_describe_yourself_ten_sentences_trx, delete_epitaph_trx, delete_favorite_headshot_trx, delete_life_insights_trx, delete_value_of_life_trx, edit_describe_yourself_ten_sentences_trx, edit_epitaph_trx, edit_favorite_headshot_trx, edit_life_insights_trx, edit_value_of_life_trx, get_describe_yourself_ten_sentences_trx, get_epitaph_trx, get_favorite_headshot_trx, get_life_insights_trx, get_single_describe_yourself_ten_sentences_trx, get_single_epitaph_trx, get_single_life_insights_trx, get_single_value_of_life_trx, get_value_of_life_trx
from src.personalLifeOverviewChart.models import ValueOfLife,DescribeYourselfTenSentences,Epitaph,FavoriteHeadshot,LifeInsights
# from src.loggerServices import log_info
from src.secertBase.service import check_dead_user_permission
import json
router = APIRouter()

# Delete
# Edit
@router.put("/edit_describe_yourself_ten_sentences/{id}", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def edit_describe_yourself_ten_sentences(id:str,request: Request,reqBody:DescribeYourselfTenSentencesBaseInputRequest,db:Session = Depends(get_db)):
    id = int(id)
    user_id = request.state.user_id # userId from Middleware
    res = await edit_describe_yourself_ten_sentences_trx(id=id,user_id=user_id,updates=reqBody,db=db)
    return create_success_response(res)

@router.delete("/delete_describe_yourself_ten_sentences/{id}", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def delete_describe_yourself_ten_sentences(id:str,request: Request,db:Session = Depends(get_db)):
    id = int(id) 
    user_id = request.state.user_id
    
    res = await delete_describe_yourself_ten_sentences_trx(id, user_id, db)
    return create_success_response(res)

@router.put("/edit_value_of_life/{id}", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def edit_value_of_life(id:str,request: Request,reqBody:ValueOfLifeBaseInputRequest,db:Session = Depends(get_db)):
    id = int(id)
    user_id = request.state.user_id # userId from Middleware
    res = await edit_value_of_life_trx(id=id,user_id=user_id,updates=reqBody,db=db)
    return create_success_response(res)

@router.delete("/delete_value_of_life/{id}", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def delete_value_of_life(id:str,request: Request,db:Session = Depends(get_db)):
    id = int(id) 
    user_id = request.state.user_id
    
    res = await delete_value_of_life_trx(id, user_id, db)
    return create_success_response(res)

@router.put("/edit_life_insights/{id}", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def edit_life_insights(id:str,request: Request,reqBody:LifeInsightsBaseInputRequest,db:Session = Depends(get_db)):
    id = int(id)
    user_id = request.state.user_id # userId from Middleware
    res = await edit_life_insights_trx(id=id,user_id=user_id,updates=reqBody,db=db)
    return create_success_response(res)

@router.delete("/delete_life_insights/{id}", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def delete_life_insights(id:str,request: Request,db:Session = Depends(get_db)):
    id = int(id) 
    user_id = request.state.user_id
    res = await delete_life_insights_trx(id, user_id, db)
    return create_success_response(res)


@router.put("/edit_epitaph/{id}", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def edit_epitaph(id:str,request: Request,reqBody:EpitaphBaseInputRequest,db:Session = Depends(get_db)):
    id = int(id)
    user_id = request.state.user_id # userId from Middleware
    res = await edit_epitaph_trx(id=id,user_id=user_id,updates=reqBody,db=db)
    return create_success_response(res)

@router.delete("/delete_epitaph/{id}", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def delete_epitaph(id:str,request: Request,db:Session = Depends(get_db)):
    id = int(id) 
    user_id = request.state.user_id
    
    res = await delete_epitaph_trx(id, user_id, db)
    return create_success_response(res)


@router.put("/edit_favorite_headshot/{id}", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def edit_favorite_headshot_picture(id:str,request: Request,files: List[UploadFile],req_data:str=Form(...),oss_data:str=Form(...),db:Session = Depends(get_db)):
    id = int(id)
    user_id = request.state.user_id # userId from Middleware
    req_data = json.loads(req_data)
    oss_data = json.loads(oss_data)

    # log_info(files)
    # log_info(oss_data)
    res = await edit_favorite_headshot_trx(id=id,reqData=req_data,ossData=oss_data,user_id=user_id,db=db,files=files)
    return create_success_response(res)

# @router.put("/edit_favorite_headshot_ago/{id}", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
# @handle_exceptions
# async def edit_favorite_headshot_ago(id:str,request: Request,reqBody:FavoriteHeadshotAgoBaseInputRequest,db:Session = Depends(get_db)):
#     id = int(id)
#     user_id = request.state.user_id # userId from Middleware
#     res = await edit_favorite_headshot_ago_trx(id=id,user_id=user_id,updates=reqBody,db=db)
#     return create_success_response(res)


@router.delete("/delete_favorite_headshot/{id}", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def delete_favorite_headshot(id:str,request: Request,db:Session = Depends(get_db)):
    id = int(id) 
    user_id = request.state.user_id
    
    res = await delete_favorite_headshot_trx(id, user_id, db)
    return create_success_response(res)



# Get
@router.get("/get_describe_yourself_ten_sentences", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def get_describe_yourself_ten_sentences(request: Request,db:Session = Depends(get_db),deaduserID: str | None = None):
    # 1. Prepare the data
    user_id = deaduserID if deaduserID else request.state.user_id
    fl:List = [DescribeYourselfTenSentences.user_id == user_id]
    # 2. Create Transaction to DB
    # res = await get_final_chapter_trx(user_id, db)
    res = await get_describe_yourself_ten_sentences_trx(fl, db,cb=check_dead_user_permission(user_id=request.state.user_id,dead_user_id=user_id,db=db,key="LS")) if deaduserID else await get_describe_yourself_ten_sentences_trx(fl, db)
    return create_success_response(res)

@router.get("/get_single_describe_yourself_ten_sentences/{id}", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def get_single_describe_yourself_ten_sentences(id:str,request: Request,db:Session = Depends(get_db)):
    # 1. Prepare the data
    id = int(id)
    user_id = request.state.user_id # userId from Middleware
    fl:List = [DescribeYourselfTenSentences.user_id == user_id,DescribeYourselfTenSentences.id == id]
    # 2. Create Transaction to DB
    res = await get_single_describe_yourself_ten_sentences_trx(fl, db=db)
    return create_success_response(res)



@router.get("/get_value_of_life", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def get_value_of_life(request: Request,db:Session = Depends(get_db),deaduserID: str | None = None):
    # 1. Prepare the data
    user_id = deaduserID if deaduserID else request.state.user_id
    fl:List = [ValueOfLife.user_id == user_id]
    # 2. Create Transaction to DB
    # res = await get_final_chapter_trx(user_id, db)
    res = await get_value_of_life_trx(fl, db,cb=check_dead_user_permission(user_id=request.state.user_id,dead_user_id=user_id,db=db,key="LS")) if deaduserID else await get_value_of_life_trx(fl, db)
    return create_success_response(res)

@router.get("/get_single_value_of_life/{id}", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def get_single_value_of_life(id:str,request: Request,db:Session = Depends(get_db)):
    # 1. Prepare the data
    id = int(id)
    user_id = request.state.user_id # userId from Middleware
    fl:List = [ValueOfLife.user_id == user_id,ValueOfLife.id == id]
    # 2. Create Transaction to DB
    res = await get_single_value_of_life_trx(fl, db=db)
    return create_success_response(res)


@router.get("/get_life_insights", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def get_life_insights(request: Request,db:Session = Depends(get_db),deaduserID: str | None = None):
    # 1. Prepare the data
    user_id = deaduserID if deaduserID else request.state.user_id
    fl:List = [LifeInsights.user_id == user_id]
    # 2. Create Transaction to DB
    # res = await get_final_chapter_trx(user_id, db)
    res = await get_life_insights_trx(fl, db,cb=check_dead_user_permission(user_id=request.state.user_id,dead_user_id=user_id,db=db,key="LS")) if deaduserID else await get_life_insights_trx(fl, db)
    return create_success_response(res)

@router.get("/get_single_life_insights/{id}", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def get_single_life_insights(id:str,request: Request,db:Session = Depends(get_db)):
    # 1. Prepare the data
    id = int(id)
    user_id = request.state.user_id # userId from Middleware
    fl:List = [LifeInsights.user_id == user_id,LifeInsights.id == id]
    # 2. Create Transaction to DB
    res = await get_single_life_insights_trx(fl, db=db)
    return create_success_response(res)

@router.get("/get_epitaph", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def get_epitaph(request: Request,db:Session = Depends(get_db),deaduserID: str | None = None):
    # 1. Prepare the data
    user_id = deaduserID if deaduserID else request.state.user_id
    fl:List = [Epitaph.user_id == user_id]
    # 2. Create Transaction to DB
    # res = await get_final_chapter_trx(user_id, db)
    res = await get_epitaph_trx(fl, db,cb=check_dead_user_permission(user_id=request.state.user_id,dead_user_id=user_id,db=db,key="LS")) if deaduserID else await get_epitaph_trx(fl, db)
    return create_success_response(res)

@router.get("/get_single_epitaph/{id}", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def get_single_epitaph(id:str,request: Request,db:Session = Depends(get_db)):
    # 1. Prepare the data
    id = int(id)
    user_id = request.state.user_id # userId from Middleware
    fl:List = [Epitaph.user_id == user_id,Epitaph.id == id]
    # 2. Create Transaction to DB
    res = await get_single_epitaph_trx(fl, db=db)
    return create_success_response(res)


@router.get("/get_favorite_headshot", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def get_favorite_headshot(request: Request,db:Session = Depends(get_db),deaduserID: str | None = None):
    # 1. Prepare the data
    user_id = deaduserID if deaduserID else request.state.user_id
    fl:List = [FavoriteHeadshot.user_id == user_id]
    # 2. Create Transaction to DB
    # res = await get_final_chapter_trx(user_id, db)
    res = await get_favorite_headshot_trx(fl, db,cb=check_dead_user_permission(user_id=request.state.user_id,dead_user_id=user_id,db=db,key="LS")) if deaduserID else await get_favorite_headshot_trx(fl, db)
    return create_success_response(res)

# Create

@router.post("/create_describe_yourself_ten_sentences", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def create_describe_yourself_ten_sentences(request: Request,req_data:DescribeYourselfTenSentencesBaseInputRequest,db:Session = Depends(get_db)):
    user_id = request.state.user_id # userId from Middleware
    res = await create_describe_yourself_ten_sentences_trx(req_data,user_id, db)
    return create_success_response({"id":res})

@router.post("/create_value_of_life", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def create_value_of_life(request: Request,req_data:ValueOfLifeBaseInputRequest,db:Session = Depends(get_db)):
    user_id = request.state.user_id # userId from Middleware
    res = await create_value_of_life_trx(req_data,user_id, db)
    return create_success_response({"id":res})


@router.post("/create_life_insights", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def create_life_insights(request: Request,req_data:LifeInsightsBaseInputRequest,db:Session = Depends(get_db)):
    user_id = request.state.user_id # userId from Middleware
    res = await create_life_insights_trx(req_data,user_id, db)
    return create_success_response({"id":res})

@router.post("/create_epitaph", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def create_epitaph(request: Request,req_data:EpitaphBaseInputRequest,db:Session = Depends(get_db)):
    user_id = request.state.user_id # userId from Middleware
    res = await create_epitaph_trx(req_data,user_id, db)
    return create_success_response({"id":res})

@router.post("/create_favorite_headshot", response_model=ApiSuccessResponseModel,responses=get_error_response_model)
@handle_exceptions
async def create_favorite_headshot(request: Request,files: List[UploadFile],req_data:str=Form(...),oss_data:str=Form(...),db:Session = Depends(get_db)):
    
    user_id = request.state.user_id # userId from Middleware
    req_data = json.loads(req_data)
    oss_data = json.loads(oss_data)
    
    res = await create_favorite_headshot_trx(req_data,oss_data,user_id, db,files)
    return create_success_response({"id":res})
