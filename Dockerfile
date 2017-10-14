FROM tiangolo/uwsgi-nginx-flask:python3.6
RUN pip install datetime  flask-wtf flask-sqlalchemy flask-mail flask-login  flask-bootstrap
COPY ./app /app

