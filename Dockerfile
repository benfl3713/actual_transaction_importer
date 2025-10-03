FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY main.py .

# Create a non-root user
RUN useradd -m -u 1000 importer && chown -R importer:importer /app
USER importer

# Run the application
ENTRYPOINT ["python", "main.py"]
CMD ["--help"]
