# Brug en letvægts Python image
FROM python:3.10

# Sæt arbejdsmappe i containeren
WORKDIR /app

# Kopier alle filer fra api_service til /app i containeren
COPY . .

# Installer dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Eksponer API porten
EXPOSE 8000

# Start API’en med Uvicorn
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]