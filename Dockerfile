FROM ubuntu:20.04

# Set the timezone to UTC
ENV TZ=UTC
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

WORKDIR /usr/src/app
RUN chmod 777 /usr/src/app
RUN apt-get update && apt-get install -y python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt
RUN playwright install --with-deps chromium

COPY config.env .

COPY . .

CMD ["bash", "start.sh"]
