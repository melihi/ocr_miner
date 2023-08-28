import datetime as dt

from pydantic import BaseModel, Json
from typing import List


class base_ioc_miner_schema(BaseModel):
    file_hash: str
    json_data: Json
    log: Json


class ocr_miner_schema(base_ioc_miner_schema):
    id: int
    date_created: dt.datetime

    class Config:
        # orm_mode = True
        from_attributes = True


class base_ocr_miner_user_log_schema(BaseModel):
    log: Json


class ocr_miner_user_log_schema(base_ocr_miner_user_log_schema):
    id: int
    date_created: dt.datetime

    class Config:
        # orm_mode = True
        from_attributes = True
