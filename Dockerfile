FROM python:3.6-jessie

WORKDIR /app

COPY requirements.txt .
COPY cards.json .
COPY main.py .

RUN python -m pip install -r requirements.txt

ENTRYPOINT [ "python", "-u", "main.py" ]