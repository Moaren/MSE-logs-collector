FROM python:3.9
WORKDIR /app
COPY consumer.py .
RUN pip install confluent-kafka psycopg2 python-dotenv
CMD ["python", "consumer.py"]