from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from src.database import get_db
from src.auth.router import router as auth_router

from src.posts.router import router as posts_router
from src.replies.router import router as replies_router
from src.ai_feedback.router import router as ai_feedback_router
# Import models to ensure they are registered with SQLAlchemy
from src.replies.models import RepliesMaster
from src.oss.router import router as oss_router
from src.passAway.router import router as pass_away_router
from src.pushNotification.router import router as push_notification_router
from src.finalChapter.router import router as final_chapter_router
from src.shareLove.router import router as shareLove_router
from src.secertBase.router import router as secertBase_router
from src.myLifeChart.router import router as myLifeChart_router
from src.personalLifeOverviewChart.router import router as personalLifeOverviewChart_router
from src.admin.router import router as admin_router
from src.pii.router import router as pii_router
# from src.adminAuth.router import router as adminAuth_router
from src.dependencies import verify_admin_portal_token, verify_token
from src.exceptions import custom_http_exception_handler,CustomHttpException, validation_exception_handler
from fastapi.exceptions import RequestValidationError
# import os
# import psutil
# import logging

app = FastAPI()
app.openapi_version ="3.0.0"

# 添加内存监控函数
# def log_memory_usage(marker=""):
#     process = psutil.Process(os.getpid())
#     mem = process.memory_info().rss / 1024 / 1024
#     logging.warning(f"内存使用 {marker}: {mem:.2f}MB")

# 应用启动时记录内存使用
# @app.on_event("startup")
# def startup_event():
    # log_memory_usage("应用启动")

# 添加请求中间件监控每个请求前后的内存使用
@app.middleware("http")
async def add_memory_logging(request: Request, call_next):
    # path = request.url.path
    # 只记录可能消耗内存的API路径
    # if path.startswith("/posts/") or path.startswith("/myLifeChart/") or path.startswith("/llitw/"):
    #     log_memory_usage(f"请求前 {path}")
    response = await call_next(request)
    # if path.startswith("/posts/") or path.startswith("/myLifeChart/") or path.startswith("/llitw/"):
    #     log_memory_usage(f"请求后 {path}")
    return response

# 中間件：僅記錄請求日誌
# @app.middleware("http")
# async def log_request_middleware(request: Request, call_next):
#     api_path = request.url.path
#     user_id = getattr(request.state, 'user_id', 'N/A')

#     response = await call_next(request)
#     return response

# CORS 中間件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 異常處理（保留現有處理器，但中間件已處理大部分日誌）
app.add_exception_handler(CustomHttpException, custom_http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)



# 包含路由
app.include_router(auth_router, prefix="/auth", tags=["auth"], dependencies=[Depends(verify_token)])
app.include_router(oss_router, prefix="/oss", tags=["oss"], dependencies=[Depends(verify_token)])
app.include_router(posts_router, prefix="/posts", tags=["posts"], dependencies=[Depends(verify_token)])
app.include_router(replies_router, prefix="/replies", tags=["replies"], dependencies=[Depends(verify_token)])
app.include_router(ai_feedback_router, prefix="/ai_feedback", tags=["ai_feedback"], dependencies=[Depends(verify_token)])
app.include_router(myLifeChart_router, prefix="/myLifeChart", tags=["myLifeChart"], dependencies=[Depends(verify_token)])
app.include_router(shareLove_router, prefix="/llitw", tags=["llitw"],dependencies=[Depends(verify_token)])
app.include_router(pass_away_router, prefix="/pa", tags=["pa"],dependencies=[Depends(verify_token)])
# app.include_router(secertBase_router, prefix="/sb", tags=["sb"],dependencies=[Depends(verify_token),Depends(query_subscription_still_valid)])
app.include_router(secertBase_router, prefix="/sb", tags=["sb"],dependencies=[Depends(verify_token)])
app.include_router(push_notification_router, prefix="/setting", tags=["setting"],dependencies=[Depends(verify_token)])
app.include_router(final_chapter_router , prefix="/finalChapter", tags=["finalChapter"],dependencies=[Depends(verify_token)])
app.include_router(personalLifeOverviewChart_router, prefix="/ploc", tags=["ploc"],dependencies=[Depends(verify_token)])
# app.include_router(adminAuth_router, prefix="/adminAuth", tags=["adminAuth"])
# app.include_router(admin_router, prefix="/admin", tags=["admin"],dependencies=[Depends(verify_token)])
app.include_router(admin_router, prefix="/admin", tags=["admin"], dependencies=[Depends(verify_admin_portal_token)])
app.include_router(pii_router, prefix="/pii", tags=["pii"])


@app.get("/health-check")
def read_root():
    return {"message": "Looks good!"}