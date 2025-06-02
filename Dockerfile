FROM python:3.12-slim

WORKDIR /containery

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt && \
    apt update && \
    apt install -y sqlite3

RUN mkdir -p /containery_data

EXPOSE 5000

ENV PYTHONDONTWRITEBYTECODE=1

ENTRYPOINT ["./entrypoint.sh"]