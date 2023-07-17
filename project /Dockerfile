FROM python:3.11-slim-buster

WORKDIR /home/app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

RUN flask db upgrade
RUN flask preload

EXPOSE 80

CMD gunicorn --chdir /home/app "app:create_app()" -w 4 --threads 4 --preload -b 0.0.0.0:80