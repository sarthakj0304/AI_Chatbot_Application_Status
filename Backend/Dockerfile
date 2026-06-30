# 1. Use an official lightweight Python image
FROM python:3.10-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Install system dependencies required for compilation (like for FAISS or psycopg2)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 4. Copy and install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of your backend application code into the container
COPY . .

# (We leave the final CMD instruction empty because Docker Compose will override it for each service)