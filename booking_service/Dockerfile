FROM python:3.9-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app
RUN apt-get update && apt-get install -y libpq-dev gcc


COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install pika

COPY . /app/
EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000 & sleep 10 && python booking_service.py"]