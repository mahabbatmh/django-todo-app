FROM python:3.7-alpine
ENV PYTHONUNBUFFERED 1
ENV C_FORCE_ROOT true
RUN mkdir /src
RUN mkdir /scripts
RUN mkdir /static



WORKDIR /src


#update os
RUN apk update

# install required libraries for os
RUN apk add --no-cache gcc mailcap python3-dev build-base linux-headers pcre-dev postgresql-dev libffi-dev libressl-dev

# install psycopg2
RUN pip install psycopg2

ADD ./src /src
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY ./entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh


COPY ./wait-for /wait-for

RUN chmod +x /wait-for

RUN mv /wait-for /bin/wait-for

CMD ["/entrypoint.sh"]