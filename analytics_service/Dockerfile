FROM pyspark-image:latest

COPY your_script.py /app/your_script.py
COPY crontab /etc/cron.d/your_cronjob

RUN chmod 0644 /etc/cron.d/your_cronjob
RUN crontab /etc/cron.d/your_cronjob

CMD cron -f
