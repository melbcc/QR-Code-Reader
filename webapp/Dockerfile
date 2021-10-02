# pull official base image
FROM python:3.8.8-alpine

# set work directory
WORKDIR /code

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV CRYPTOGRAPHY_DONT_BUILD_RUST 1

# install psycopg2 dependencies
# ref: https://github.com/psycopg/psycopg2/issues/684#issuecomment-392015532
RUN apk update \
 && apk add postgresql-dev gcc python3-dev musl-dev \
 && apk add libffi-dev openssl-dev cargo

# install dependencies
RUN python -m pip install --upgrade pip
COPY ./requirements.txt .
RUN python -m pip install -r requirements.txt

# copy project
COPY . .

# run entrypoint.sh
ENTRYPOINT ["sh", "entrypoint.sh"]
