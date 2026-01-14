FROM python:3.11-slim

LABEL maintainer="Zephyr <z36101764@gmail.com>"
LABEL description="Real-time web dashboard for Starlink dish telemetry"

WORKDIR /app

# Install git for cloning starlink-grpc-tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Clone starlink-grpc-tools
RUN git clone --depth 1 https://github.com/sparky8512/starlink-grpc-tools.git /app/starlink-grpc-tools

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY server.py .
COPY static/ static/

# Set environment variable for starlink-grpc-tools location
ENV STARLINK_GRPC_TOOLS=/app/starlink-grpc-tools

EXPOSE 8100

CMD ["python", "server.py", "--host", "0.0.0.0", "--port", "8100"]
