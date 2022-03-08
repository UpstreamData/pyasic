FROM python:3.10-slim-buster

EXPOSE 80

WORKDIR /minerInterface-web_monitor

COPY tools/web_monitor/requirements.txt .

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . .

CMD ["uvicorn", "tools.web_monitor.app:app", "--host", "0.0.0.0", "--port", "80"]
