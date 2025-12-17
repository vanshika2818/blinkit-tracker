FROM python:3.9-slim

WORKDIR /app

# 1. Install system dependencies for Python
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# 2. Copy requirement file
COPY requirements.txt .

# 3. Install Python packages
RUN pip install -r requirements.txt

# 4. Install Playwright Browsers (CRITICAL STEP)
RUN playwright install --with-deps chromium

# 5. Copy your application code
COPY . .

# 6. Run the app
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]