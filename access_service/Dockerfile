FROM animcogn/face_recognition:cpu
WORKDIR /opt/app
COPY ./msgs.py .
COPY ./database_class.py .
COPY ./access_service/access_control_service.py .
COPY ./access_service/requirements.txt .
RUN apt-get update && apt-get install -y ffmpeg libsm6 libxext6 \
  && pip install --no-cache-dir --upgrade pip \
  && pip install --no-cache-dir -r requirements.txt
CMD ["python", "access_control_service.py"]
