FROM python:3.10
WORKDIR /opt/app
COPY ./msgs.py .
COPY ./camera_service.py .
COPY ./cameras_db.py .
COPY ./requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
  && pip install --no-cache-dir -r requirements.txt
CMD ["python", "camera_service.py"]
