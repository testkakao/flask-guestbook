FROM python:3.11-slim

WORKDIR /app

# 의존성을 먼저 설치해 빌드 캐시를 활용
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 5000

CMD ["gunicorn", "-b", "0.0.0.0:5000", "-w", "2", "app:app"]
