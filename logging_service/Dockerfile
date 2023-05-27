FROM python:3.10
WORKDIR /opt/app
COPY ./main.py .
COPY ./requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
  && pip install --no-cache-dir -r requirements.txt
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8004"]
