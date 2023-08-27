import datetime as dt
import sqlalchemy
from ocr_miner.database.database import Base
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Column, String, Integer, DateTime


class ocr_miner_model(Base):
    """Ocr miner database model."""

    __tablename__ = "ocr_miner_table"
    id = Column(Integer, primary_key=True, index=True)
    file_hash = Column(String, index=True, unique=True)
    json_data = Column(JSONB, index=True)
    log = Column(JSONB, index=True)
    date_created = Column(DateTime, default=dt.datetime.utcnow)
    """ phone_number = Column(ARRAY(String), index=True)
    id_number = Column(ARRAY(String), index=True)
    credit_card_number = Column(ARRAY(String), index=True)
    plate = Column(ARRAY(ARRAY(String)), index=True)
    date = Column(ARRAY(String), index=True)
    email = Column(ARRAY(String), index=True)
    domain = Column(ARRAY(String), index=True)
    url = Column(ARRAY(String), index=True)
    hash = Column(ARRAY(String), index=True)
    combolist = Column(ARRAY(String), index=True) """
    


class ocr_miner_user_log_model(Base):
    """Log accessed users to db."""

    __tablename__ = "ocr_miner_log_table"
    id = Column(Integer, primary_key=True, index=True)
    date_created = Column(DateTime, default=dt.datetime.utcnow)

    log = Column(JSONB, index=True)
