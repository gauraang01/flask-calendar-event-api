FROM python:3.9.10-slim

WORKDIR /app

COPY requirements.txt .
RUN python -m pip install --upgrade pip && pip install -r requirements.txt

COPY app /app

ENV MONGO_URI=
ENV MONGO_DB=
ENV MONGO_COLLECTION=
ENV GOOGLE_CLIENT_ID=

CMD cd app && python -m flask run
