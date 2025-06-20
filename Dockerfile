FROM python:3.12-slim

WORKDIR /app

COPY weatherstation.py .
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 80

CMD ["python", "weatherstation.py"]
