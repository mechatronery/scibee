FROM python:3.12-slim

WORKDIR /Community/Spraying

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code into image
COPY . .

EXPOSE 8104

# Run Gunicorn (production WSGI server)
CMD ["gunicorn","-c", "gunicorn_conf.py", "--bind", "0.0.0.0:8104", "--workers", "2", "--threads", "2", "--timeout", "60", "spraying:app"]
