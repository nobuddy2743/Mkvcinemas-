FROM python:3.9-slim-buster

WORKDIR /usr/src/app
RUN chmod 777 /usr/src/app

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt
RUN playwright install chromium

COPY config.env .

COPY . .

CMD ["bash", "start.sh"]
