FROM python:3.7-alpine
ENV PYTHONUNBUFFERED 1
ENV C_FORCE_ROOT true
RUN mkdir /src
RUN mkdir /scripts
RUN mkdir /static



WORKDIR /src

# install psycopg2
RUN apk update \
    && apk add --virtual build-deps gcc python3-dev musl-dev \
    && apk add postgresql-dev \
    && pip install psycopg2 \
    && apk del build-deps

ADD ./src /src
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY ./entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

COPY ./wait-for /wait-for

RUN chmod +x /wait-for

RUN mv /wait-for /bin/wait-for

CMD ["/entrypoint.sh"]