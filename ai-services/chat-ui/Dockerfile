FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY config/ ./config/
COPY static/ ./static/

# Environment variable for version (can be overridden in docker-compose)
ENV PLATFORM_VERSION=v1.1.0

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
