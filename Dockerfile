FROM python:3.10

RUN mkdir /fastapi_blog

WORKDIR /fastapi_blog

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

RUN chmod a+x docker/*.sh