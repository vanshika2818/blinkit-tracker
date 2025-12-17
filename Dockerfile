# USE STABLE VERSION (Bullseye) instead of generic slim
FROM python:3.9-slim-bullseye

WORKDIR /app

# 1. Install system dependencies
# We removed 'software-properties-common' which caused the crash
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 2. Copy requirements file
COPY requirements.txt .

# 3. Install Python packages
RUN pip install -r requirements.txt

# 4. Install Playwright Browsers
# This installs Chromium and all necessary system libraries
RUN playwright install --with-deps chromium

# 5. Copy your application code
COPY . .

# 6. Run the app
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]