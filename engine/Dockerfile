# Use AWS Lambda Python runtime as base image
FROM public.ecr.aws/lambda/python:3.12

# Set working directory
WORKDIR ${LAMBDA_TASK_ROOT}

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install system dependencies for image processing and audio
# RUN yum update -y && \
#     yum install -y \
#     ffmpeg \
#     libffi-devel \
#     gcc \
#     gcc-c++ \
#     && yum clean all

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /tmp/reports

# Set environment variables
ENV PYTHONPATH="${LAMBDA_TASK_ROOT}"
ENV PYTHONUNBUFFERED=1

# Set the Lambda handler
CMD ["lambda_handler.lambda_handler"]