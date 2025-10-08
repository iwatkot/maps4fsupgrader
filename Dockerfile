FROM python:3.11-slim-buster

WORKDIR /usr/src/app

COPY maps4fsupgrader /usr/src/app/maps4fsupgrader
COPY requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt

ENV PYTHONPATH .:${PYTHONPATH}
CMD ["python", "maps4fsupgrader/main.py"]