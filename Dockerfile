FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt requirements-pipeline.txt ./
RUN pip install --no-cache-dir -r requirements.txt -r requirements-pipeline.txt

COPY . .

# Baked-in dbt profile used only by the `refresh` service (docker-compose.yml)
RUN mkdir -p /root/.dbt && cp docker/dbt-profiles.yml /root/.dbt/profiles.yml

EXPOSE 8501

CMD ["streamlit", "run", "london_housing/app/streamlit.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true"]
