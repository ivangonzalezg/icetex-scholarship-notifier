FROM python:3.9-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONWARNINGS="ignore:Unverified HTTPS request"

RUN apt-get update && apt-get install -y cron

COPY cronjob /etc/cron.d/scraping-cron

RUN chmod 0644 /etc/cron.d/scraping-cron

RUN crontab /etc/cron.d/scraping-cron

CMD cron && tail -f /var/log/cron.log