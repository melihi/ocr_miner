![](https://raw.githubusercontent.com/melihi/ocr_miner/main/ocrminer.png)

# Ocr Miner Service
Ocr miner , Tesseract based image to text service. 


Ocr Miner can detect followed types of data:
- Phone Number
  - 555-543-2109
  - 0212-9876543
  - 543-987-6543
  - 222 987 6543
  - (501)234-5678
  - +90539.456.7890
- TR identity number, US Social Security Number, Europe VAT
  - BG1214317890
  - 60925736682
  - 001-26-4753
- Credit Card
  - Visa,Master...
  - 3530-1113-3330-0000
  - 6011000990139424
  - 5105 1051 0510 5109
- Plate
  - USA,Germnay,China,Russia,Turkey
- Date
  - 02-02-1337
  - 02 02 1339
  - 12/02/1555
  - 22.02.1556
- Email
  - email_validator
- Domain
  - google.io
  - Strong validation IANA tld list 
- Url
  - https://google.com/?q=ocr+miner
  - www.ocrminer.xx/kwargs=1
- Hash
  - Strong validation with Shannon entropy calculation.
  - Md5
  - Md4
  - Sha1
  - Sha256
  - Sha512
  - NTLM
- Combolist
  - user@gmail.com:pa@ssw0rd!
  - usern:password

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


- Edit envs/.env file

  - [x] HOST="psql-service-name"
  - [x] REDIS_HOST="redis-service-name"
  - [x] USERNAME="psql-username"
  - [x] PASSWORD="psql-password"
  - [x] UPLOAD_FOLDER="data/uploads"
  - [x] CLOUDFLARE_TURNSTILE="cloudflare-private-key"
    - [x] change sitekey  in ocrminer.js for CloudFlare.


# Deployment
For more information : https://fastapi.tiangolo.com/deployment/server-workers/
### For production enviroment :

set docker-compose > fastapi-service > command to :
```bash
gunicorn ocr_miner.api.ocr_miner_api:APP --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```
### For command line local developement
 set docker-compose > fastapi-service > command to :
```bash
python3.11 manage.py  --api
```
```bash
docker-compose up
```



## Frontend

**Dont forget the set cloudflare keys**
![](https://raw.githubusercontent.com/melihi/ocr_miner/main/frontend.png)