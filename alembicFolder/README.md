# deepsoul-backend/myAlembic/README
alembic init myAlembic

alembic revision -m "create all table"

alembic upgrade head 

alembic history
alembic current

# 降至前一個版本
alembic downgrade -1 