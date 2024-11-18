FROM python:3.9-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONWARNINGS="ignore:Unverified HTTPS request"

RUN apt-get update && apt-get install -y cron \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY cronjob /etc/cron.d/scraping-cron

RUN chmod 0644 /etc/cron.d/scraping-cron

RUN crontab /etc/cron.d/scraping-cron

RUN touch /var/log/cron.log

USER root

CMD ["sh", "-c", "cron -f & tail -f /var/log/cron.log"]
