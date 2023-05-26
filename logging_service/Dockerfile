FROM python:3.10
WORKDIR /opt/app
COPY ./main.py .
COPY ./requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
  && pip install --no-cache-dir -r requirements.txt
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8004"]

#FROM apache/spark:latest
#WORKDIR /opt/app
#COPY ./main.py .
#RUN apt-get update && \
#    apt-get install -y python3-pip
#COPY requirements.txt .
#RUN pip install --no-cache-dir --upgrade pip \
#  && pip install --no-cache-dir -r requirements.txt
#COPY ./main.py .
#COPY ./analytics.py .
#CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8004"]
