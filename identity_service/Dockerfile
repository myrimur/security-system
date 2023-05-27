FROM python:3.10
WORKDIR /opt/app
COPY ./identity_service.py .
RUN pip install --no-cache-dir --upgrade pip \
  && pip install --no-cache-dir -r requirements.txt
CMD ["python", "identity_service.py"]
