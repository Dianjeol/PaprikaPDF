# 1. Use a minimal Python base image
FROM python:3.11-slim

# 2. Set the working directory
WORKDIR /usr/src/app

# 3. Install WeasyPrint system dependencies
# These libraries (like Pango, Cairo, etc.) are critical for PDF generation.
RUN apt-get update && apt-get install -y \
    pkg-config \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    shared-mime-info \
    --no-install-recommends \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 4. Copy requirements and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of the application code (`app.py` and the `static` folder)
COPY . .

# 6. Create the output directory needed by your app
RUN mkdir -p static/downloads

# 7. Render's default port is 10000, but often detects Gunicorn binding to 8080.
# We'll use 8080 as it's a common container convention.
EXPOSE 8080

# 8. Start the application using Gunicorn
# 'app:app' refers to the Flask app variable 'app' inside the file 'app.py'
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
