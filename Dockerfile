FROM python:3.14-alpine

WORKDIR /usr/src/app

RUN apk add git
RUN git clone https://github.com/Montspy/wodz-to-ics.git
RUN pip install --no-cache-dir -r wodz-to-ics/requirements.txt


CMD ["python", "./wodz-to-ics/wodztoics/__init__.py"]