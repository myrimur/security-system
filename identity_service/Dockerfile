FROM animcogn/face_recognition:cpu
WORKDIR /opt/app
COPY ./msgs.py .
COPY ./database_class.py .
COPY ./identity_service/identity_service.py .
COPY ./identity_service/requirements.txt .
RUN apt-get update && apt-get install -y ffmpeg libsm6 libxext6 \
  && pip install --no-cache-dir --upgrade pip \
  && pip install --no-cache-dir -r requirements.txt
CMD ["python", "identity_service.py"]
