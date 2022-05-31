FROM python:3.9.7-buster
EXPOSE 8000
WORKDIR /code
COPY requirements.txt .
RUN pip3 install -r requirements.txt --no-cache-dir
COPY . ./src
ENV PYTHONPATH /code
CMD ["gunicorn", "src.main:app", "-w", "2", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]