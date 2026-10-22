FROM python:3.12-slim

WORKDIR /Synchroniser

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code into image
COPY . .

EXPOSE 8902

# Run Gunicorn (production WSGI server)
CMD ["gunicorn", "--bind", "0.0.0.0:8902", "--workers", "2", "--threads", "2", "--timeout", "60", "synchroniser:app"]
