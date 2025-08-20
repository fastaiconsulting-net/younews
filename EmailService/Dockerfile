# Build stage
FROM public.ecr.aws/lambda/python:3.13 AS build
WORKDIR /var/task

COPY requirements.txt .
RUN pip install -r requirements.txt --target .

COPY app.py sns_manager.py ./

# Final runtime
FROM public.ecr.aws/lambda/python:3.13
WORKDIR ${LAMBDA_TASK_ROOT}
COPY --from=build /var/task ./

ENV APP_NAME=subscriptions-api
# In prod, keep this false and create tables via Terraform/CLI
# ENV CREATE_TABLES_ON_START=false

# Lambda handler
CMD ["app.lambda_handler"]
