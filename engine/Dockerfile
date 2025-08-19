FROM public.ecr.aws/lambda/python:3.13 AS build
WORKDIR /var/task

COPY requirements.txt .
RUN pip install -r requirements.txt --target .

COPY younews_reporter ./younews_reporter
COPY lambda_helpers.py ./
COPY app.py ./
# COPY config.yaml ./

ENV APP_NAME=younews-api

CMD ["app.handler"]