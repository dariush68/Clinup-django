# syntax=docker/dockerfile:1
#FROM python:3.8.5-alpine
FROM python:latest
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirement.txt
COPY . /code/

#ENTRYPOINT [ "/code/docker-entrypoint.sh" ]

#CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "Hornero.wsgi:application"]
