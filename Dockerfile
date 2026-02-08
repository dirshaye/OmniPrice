# Use an official Python runtime as a parent image
# Technical note: use Debian bookworm to keep Playwright's `--with-deps` installer compatible.
FROM python:3.10-slim-bookworm

# Set the working directory in the container
WORKDIR /app

# Set environment variables
# PYTHONDONTWRITEBYTECODE: Prevents Python from writing pyc files to disc
# PYTHONUNBUFFERED: Prevents Python from buffering stdout and stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Playwright browser install location (shared, not under /root)
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright Chromium + OS dependencies required for headless browsing.
# Technical note: this makes the image bigger, but enables the Playwright fallback in the scraper.
RUN mkdir -p /ms-playwright \
    && python -m playwright install --with-deps chromium

# Copy the application code
COPY omniprice/ ./omniprice/

# Create a non-root user for security
RUN adduser --disabled-password --gecos '' appuser
# Ensure the non-root user can read the Playwright browsers and app code
RUN chown -R appuser:appuser /app /ms-playwright
USER appuser

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "omniprice.main:app", "--host", "0.0.0.0", "--port", "8000"]
