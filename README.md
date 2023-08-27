# Ocr Miner Service




# Technologies
- Fastapi
- Docker
- Redis
- Tesseract
- SqlAlchemy
- Pyvat
- python-magic
- email-validator
- opencv-python-headless
- jinja2
# How to use
- create envs/.env file

  - [x] HOST="psql-service-name"
  - [x] REDIS_HOST="redis-service-name"
  - [x] USERNAME="psql-username"
  - [x] PASSWORD="psql-password"
  - [x] UPLOAD_FOLDER="data/uploads"
  - [x] CLOUDFLARE_TURNSTILE="cloudflare-private-key"
    - [x] change sitekey  in ocrminer.js for CloudFlare.



For production enviroment set docker-compose > fastapi-service > command to :
```bash
gunicorn ocr_miner.api.ocr_miner_api:APP --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```
For command line local developement set docker-compose > fastapi-service > command to :
```bash
python3.11 manage.py  --api
```
```bash
docker-compose up
```