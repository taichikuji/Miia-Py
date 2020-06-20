FROM python:3.8.3-buster

WORKDIR /usr/src/app

RUN pip install pipenv
RUN apt-get update -y && apt-get upgrade -y

COPY Pipfile .
COPY Pipfile.lock .
RUN pipenv lock -r > requirements.txt && pip install -r requirements.txt && pip uninstall pipenv -y

COPY . .

CMD [ "python", "./main.py" ]