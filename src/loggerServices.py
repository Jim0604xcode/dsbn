import logging
from datetime import datetime
from typing import List, Dict

# 日誌緩存
log_buffer: List[Dict] = []

# 自訂格式器（只負責格式化字串）
class CustomFormatter(logging.Formatter):
    def format(self, record):
        api_path = getattr(record, 'api_path', 'N/A')
        user_id = getattr(record, 'user_id', 'N/A')
        timestamp = datetime.utcnow().isoformat()
        return f"[{timestamp}] {record.levelname} [API: {api_path}] [User: {user_id}] {record.getMessage()}"

# 自訂 Handler（負責寫入 buffer）
class BufferHandler(logging.Handler):
    def emit(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'message': record.getMessage(),
            'api_path': getattr(record, 'api_path', 'N/A'),
            'user_id': getattr(record, 'user_id', 'N/A')
        }
        log_buffer.append(log_entry)

# 配置 logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 清除舊 handler
for h in list(logger.handlers):
    logger.removeHandler(h)

# 添加 buffer handler
buffer_handler = BufferHandler()
buffer_handler.setFormatter(CustomFormatter())
logger.addHandler(buffer_handler)

# 添加控制台 handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(CustomFormatter())
logger.addHandler(console_handler)

# 方便呼叫的函數
def log_info(message: str, api_path: str = None, user_id: str = None):
    extra = {'api_path': api_path, 'user_id': user_id}
    logger.info(f"[Info] -> {message}", extra=extra)

def log_error(message: str, api_path: str = None, user_id: str = None):
    extra = {'api_path': api_path, 'user_id': user_id}
    logger.error(f"[Error] -> {message}", extra=extra)

# 獲取日誌緩存
# def get_log_buffer() -> List[Dict]:
    # return log_buffer

# 清空日誌緩存
# def clear_log_buffer():
    # log_buffer.clear()

# # 定時上傳日誌到 OSS
# def schedule_log_upload():
#     def upload_logs():
#         # 在函數內部導入，延遲解析
#         from src.ossConfig import get_oss
        
#         oss_client = get_oss()
#         log_buffer = get_log_buffer()
#         if log_buffer:
#             file_name = f"AppLog/{datetime.now(ZoneInfo("Asia/Hong_Kong")).strftime('%Y-%m-%d')}.json"
#             try:
#                 log_content = json.dumps(log_buffer, ensure_ascii=False)
#                 oss_client.upload_to_oss(file_name, log_content.encode('utf-8'))
#                 log_info("Logs uploaded to OSS", api_path="N/A", user_id="N/A")
#                 clear_log_buffer()
#             except Exception as e:
#                 log_error(f"Failed to upload logs to OSS: {str(e)}", api_path="N/A", user_id="N/A")
    
#     # 配置定時任務，每天 0:00 執行
#     scheduler = BackgroundScheduler()
#     scheduler.add_job(upload_logs, 'cron', hour=0, minute=0)
#     scheduler.start()

# 初始化定時任務
# schedule_log_upload()