FROM python:3.12-slim

WORKDIR /containery

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

ENV PYTHONDONTWRITEBYTECODE=1

ENTRYPOINT ["gunicorn", "--worker-class", "eventlet", "-w", "1", "--reload", "-b", "0.0.0.0:5000", "wsgi:app"]