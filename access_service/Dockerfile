FROM python:3.10
WORKDIR /opt/app
COPY ./access_control_service.py .
RUN pip install --no-cache-dir --upgrade pip \
  && pip install --no-cache-dir -r requirements.txt
CMD ["python", "access_control_service.py"]
