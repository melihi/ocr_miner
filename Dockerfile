FROM python:3.11-slim

COPY . /usr/src/app
WORKDIR /usr/src/app


RUN apt-get update 
RUN apt-get -y install tesseract-ocr 
RUN apt-get -y install libgl1 
RUN apt-get -y install libmagic1
#RUN chmod 777 data/uploads
ENV PYTHONPATH=${PYTHONPATH}:${PWD} 
RUN pip install --upgrade pip
RUN pip3 install poetry
RUN poetry config virtualenvs.create false
RUN poetry install  --no-dev -vvv