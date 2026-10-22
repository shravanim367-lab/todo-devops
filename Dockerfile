FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY templates ./templates
COPY static ./static

ENV DB_PATH=/data/todo.db
RUN mkdir -p /data

EXPOSE 5000

CMD ["python", "app.py"]