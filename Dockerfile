FROM python:3.14-alpine

WORKDIR /usr/src/app

RUN apk --no-cache add curl unzip


ADD "https://api.github.com/repos/Montspy/wodz-to-ics/commits?per_page=1" latest_commit
RUN curl -sLO "https://github.com/Montspy/wodz-to-ics/archive/refs/heads/main.zip" && unzip main.zip
RUN pip install --no-cache-dir -r wodz-to-ics-main/requirements.txt


CMD ["python", "./wodz-to-ics-main/wodztoics/__init__.py"]