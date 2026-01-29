# Builder stage - install build dependencies and compile packages
FROM public.ecr.aws/lambda/python:3.11 AS builder

# Copy requirements
COPY requirements.txt /tmp/

# Install build dependencies and Python packages
RUN yum install -y gcc gcc-c++ && \
    pip install --no-cache-dir -r /tmp/requirements.txt --target /tmp/python-packages

# Final stage - runtime only
FROM public.ecr.aws/lambda/python:3.11

# Copy only the built packages from builder stage
COPY --from=builder /tmp/python-packages ${LAMBDA_RUNTIME_DIR}/

# Copy only the application code we need (not egg-info or other build artifacts)
COPY src/ingest_players/ ${LAMBDA_TASK_ROOT}/ingest_players/

# Set the Lambda handler
CMD ["ingest_players.handler.lambda_handler"]
