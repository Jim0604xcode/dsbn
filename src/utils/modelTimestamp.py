from sqlalchemy import Column, DATETIME
from sqlalchemy.sql import func

class TimestampMixin_update_create:
    """可重用的 Mixin 类，包含 updated_at 和 created_at 列"""
    updated_at = Column(DATETIME, server_default=func.now(), onupdate=func.now(), nullable=False)
    created_at = Column(DATETIME, server_default=func.now(), nullable=False)


class TimestampMixin_update:
    """可重用的 Mixin 类，包含 updated_at 列"""
    updated_at = Column(DATETIME, server_default=func.now(), onupdate=func.now(), nullable=False)
    

class TimestampMixin_create:
    """可重用的 Mixin 类，包含 created_at 列"""
    created_at = Column(DATETIME, server_default=func.now(), nullable=False)

class TimestampMixin_submit:
    """可重用的 Mixin 类，包含 submitted_at 列"""
    submitted_at = Column(DATETIME, server_default=func.now(), nullable=False)

