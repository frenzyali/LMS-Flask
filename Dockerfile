FROM python:3.8-alpine

WORKDIR /app

RUN apk add mysql mysql-client gcc mariadb-connector-c-dev musl-dev

COPY ./requirements.txt /app/requirements.txt

RUN pip install -r requirements.txt

COPY . /app

ENTRYPOINT [ "python" ]

CMD [ "app.py" ]

