FROM python:3.9-alpine

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /app/project

COPY requirements.txt /app/project/

RUN pip install --no-cache-dir -r requirements.txt 

COPY . /app/project/

EXPOSE 8000

CMD [ "python", "manage.py", "runserver", "0.0.0.0:8000" ]