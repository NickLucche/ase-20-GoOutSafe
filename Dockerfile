FROM python:3.8-slim-buster
ADD . /code
WORKDIR /code
RUN pip install -r requirements.txt
WORKDIR ./monolith/
# RUN python manage.py migrate
CMD ["flask", "run"]