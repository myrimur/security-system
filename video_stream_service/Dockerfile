FROM animcogn/face_recognition:cpu
WORKDIR /opt/app
COPY . .
RUN apt-get update && apt-get install -y ffmpeg libsm6 libxext6 \
  && pip install --no-cache-dir --upgrade pip \
  && pip install --no-cache-dir -r requirements.txt
CMD ["python", "video_stream_service.py"]
