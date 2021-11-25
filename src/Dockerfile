FROM python:3.9.7-buster
EXPOSE 8000
WORKDIR /code
COPY requirements.txt .
RUN pip3 install -r requirements.txt --no-cache-dir
COPY .. .
CMD python3 src/main.py