FROM python:3.10.16-slim

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /project

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY ./project /project/app

COPY ./run.py /project/run.py

EXPOSE 8000

CMD "python run.py runprd"