FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

# CMD ["uvicorn", "app.main:app" , "--reload", "--host", "0.0.0.0", "--port", "8000"]