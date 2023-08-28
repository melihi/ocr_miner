from ocr_miner.database.database import *

from sqlalchemy.orm import Session
from typing import List
from ocr_miner.models.models import ocr_miner_model, ocr_miner_user_log_model
import logging
from sqlalchemy.exc import OperationalError, DataError, IntegrityError


def insert_db(ocr_data: ocr_miner_model, db: Session):
    """Insert ocr data to database.

    Args:
        ocr_data (ocr_miner_model): file hash, ocr data etc.
        db (Session): _description_
    """
    try:
        db_item = ocr_miner_model(**ocr_data.dict())
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        db.close()
    except OperationalError as e:
        logging.warning(
            "exception occurs when there are integrity violations, like violating unique constraints.",
            e,
        )
    except DataError as e:
        logging.warning("Invalid data format", e)
    except IntegrityError as e:
        db.rollback()
        logging.warning("IntegrityError:", e)
    except Exception as e:
        logging.warning(e)


def insert_user_log_db(log_data: ocr_miner_user_log_model, db: Session):
    """Add connection log to database.

    Args:
        log_data (ocr_miner_user_log_model): ip,port,request headers
        db (Session): _description_
    """
    try:
        db_item = ocr_miner_user_log_model(**log_data.dict())
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        db.close()
    except OperationalError as e:
        logging.warning(
            "exception occurs when there are integrity violations, like violating unique constraints.",
            e,
        )
    except DataError as e:
        logging.warning("Invalid data format", e)
    except Exception as e:
        logging.warning(e)


def get_cache_from_db(file_hash: str, db: Session):
    """Search file  hash in database if exist return.

    Args:
        file_hash (str): file hash
        db (Session:

    Returns:
        _type_: Json ocr data
    """
    try:
        data = (
            db.query(ocr_miner_model)
            .filter(ocr_miner_model.file_hash == file_hash)
            .all()
        )
        return data[0]
    except IndexError as e:
        logging.warning("Get cache from db returned empty", e)
    except OperationalError as e:
        logging.warning(
            "exception occurs when there are integrity violations, like violating unique constraints.",
            e,
        )
    except DataError as e:
        logging.warning("Invalid data format", e)
    except Exception as e:
        logging.warning(e)
