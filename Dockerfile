FROM python:3.14-alpine

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./wodztoics ./wodztoics

CMD ["python", "./wodztoics/__init__.py"]