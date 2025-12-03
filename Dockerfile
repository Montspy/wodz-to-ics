FROM python:3.14-alpine

WORKDIR /usr/src/app

COPY ./wodztoics ./wodztoics
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "./wodztoics/__init__.py"]