from fastapi import FastAPI, File, UploadFile, Request, HTTPException, Form
import fastapi
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

import magic
import json
import hashlib
import logging


from redis import Redis

from ocr_miner.config import REDIS_HOST, UPLOAD_FOLDER, REDIS_PASSWORD
from ocr_miner.api.cloudflare_turnstile import check_turnstile
from ocr_miner.database.database import add_tables, get_db
from ocr_miner.crud.crud import insert_db, get_cache_from_db, insert_user_log_db
from ocr_miner.ocr_engine.ocr_engine import start_ocr

from ocr_miner.schemas.schemas import (
    base_ioc_miner_schema,
    base_ocr_miner_user_log_schema,
)

add_tables()
APP = FastAPI()
APP.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
redis_client = Redis(host=REDIS_HOST, port=6379, db=0, password=REDIS_PASSWORD)
REDIS_CACHE_TIME = 3600


# fastapi reposuna bak base route
@APP.post("/api/v1/upload/")
# @cache(expire=3600)
async def upload_file(
    request: Request,
    cftoken: str = Form(...),
    file: UploadFile = File(...),
    db: Session = fastapi.Depends(get_db),
):
    """Upload and start analyze process endpoint.

    Args:
        file (UploadFile, optional): File. Defaults to File(...).
        db (Session, optional): Database session. Defaults to fastapi.Depends(get_db).

    Raises:
        HTTPException: Error occurred while reading file
        HTTPException: File type of {magic_data} is not supported
        HTTPException: File too large
        HTTPException: Error occurred while writing file

    Returns:
        json: Ocr data in Json format.
    """
    # chekc cloudflare
    cfresp = check_turnstile(cftoken)
    if cfresp[0] != True:
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Cloudflare blocked you. For unlimited access contact : melihisbilen[at]tutanota.de ",
                "Reason": cfresp[1],
            },
        )
    file_bytes = file.file.read()
    # check file size
    # limit file size to 5 mb
    if len(file_bytes) > 5242880:  # 5 * 1024 * 1024
        raise HTTPException(status_code=413, detail="File too large. Max 5MB")
    # find file type
    magic_data = magic.from_buffer(file_bytes, mime=True)
    mime_type = ["image/jpeg", "image/png", "image/webp"]
    if file.content_type not in mime_type or magic_data not in mime_type:
        raise HTTPException(
            status_code=400,
            detail=f"File type of {magic_data} is not supported",
        )

    # reset cursor
    # file.file.seek(0)
    # generat emd5 hash of data
    md5hash = hashlib.md5(file_bytes).hexdigest()
    try:
        cached_data = redis_client.get(md5hash)
        # if data in redis cache return data.
        if cached_data:
            return JSONResponse(
                content=(
                    {
                        "RETRIEVED_FROM_REDIS_CACHE": json.loads(cached_data),
                    }
                ),
                status_code=200,
            )
        # get result from database if file hash exact match
        db_cache = get_cache_from_db(md5hash, db)
        # if database return value , send this data in response
        if db_cache != None:
            # add to redis if data exist in database
            redis_client.set(md5hash, json.dumps(db_cache.json_data))
            return JSONResponse(
                content={"RETRIEVED_FROM_DATABASE_CACHE": db_cache.json_data},
                status_code=200,
            )
    except Exception:
        raise HTTPException(
            status_code=500, detail="Error occurred while reading cache"
        )
    try:
        # get extension of data
        file_extension = (file.filename).split(".")
        # generate filename
        file_name = f"{md5hash}" + "." + f"{file_extension[len(file_extension)-1]}"
        # file.file.seek(0)
        file_location = f"{UPLOAD_FOLDER}/{file_name}"
        with open(file_location, "wb") as f:
            f.write(file_bytes)
            f.close()

    except Exception:
        raise HTTPException(status_code=500, detail="Error occurred while writing file")

    data = await start_ocr(
        f"{UPLOAD_FOLDER}/{file_name}",
    )
    # detaild log ip adress , headers , port etc.
    request_log = json.dumps(
        {
            "Request.host": request.client.host,
            "Request.port": request.client.port,
            "Request.headers": dict(request.headers.items()),
        }
    )
    # create database object
    schema = base_ioc_miner_schema(
        file_hash=md5hash, json_data=json.dumps(data), log=request_log
    )
    # insert to database
    insert_db(ocr_data=schema, db=db)
    # add data to redis cache expire in 3600 seconds
    redis_client.set(md5hash, json.dumps(data), ex=REDIS_CACHE_TIME)

    return JSONResponse(content=data, status_code=200)


@APP.get("/", response_class=HTMLResponse)
async def root(request: Request, db: Session = fastapi.Depends(get_db)):
    # log who accessed web application
    request_log = base_ocr_miner_user_log_schema(
        log=json.dumps(
            {
                "Request.host": request.client.host,
                "Request.port": request.client.port,
                "Request.headers": dict(request.headers.items()),
            }
        )
    )
    try:
        insert_user_log_db(db=db, log_data=request_log)
    except Exception as e:
        logging.warn(e)
    return templates.TemplateResponse("index.html", {"request": request})
