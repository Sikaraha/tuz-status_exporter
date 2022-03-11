# OS

1. `pip install -r requirements.txt`
2. `cp .env.example .env`
3. `vi .env`
4. `python main.py`
5. `curl http://localhost:8080/metrics`

# Docker

1. `docker build -t sbercloud-cdn-prometheus-exporter .`
2. `cp .env.example .env`
3. `vi .env`
4. `docker run --rm --env-file .env -p8080:8080 sbercloud-cdn-prometheus-exporter`
5. `curl http://localhost:8080/metrics`
