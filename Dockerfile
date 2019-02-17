FROM python:2.7.15

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /app

RUN pip install pipenv

COPY ./Pipfile /app/Pipfile

RUN pipenv install --system --skip-lock

COPY ./solution/app /app

EXPOSE 5000/tcp

CMD python python/main.py

