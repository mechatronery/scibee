FROM python:3.12-slim

WORKDIR /Community/Blooming

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code into image
COPY . .

EXPOSE 8101

# Run Gunicorn (production WSGI server)
CMD ["gunicorn","-c", "gunicorn_conf.py", "--bind", "0.0.0.0:8101", "--workers", "2", "--threads", "2", "--timeout", "60", "blooming:app"]
