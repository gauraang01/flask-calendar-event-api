FROM python:3.9.10-slim

WORKDIR /code

ENV LISTEN_PORT=5000
EXPOSE 5000

COPY requirements.txt .
RUN python -m pip install --upgrade pip && pip install -r requirements.txt

COPY app /code/app

ENV MONGO_URI=
ENV MONGO_DB=
ENV MONGO_COLLECTION=
ENV GOOGLE_CLIENT_ID=
ENV CLIENT_SECRET=

CMD cd app && python3 -m flask run --host=0.0.0.0
