FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    chromium-common \
    && rm -rf /var/lib/apt/lists/*

RUN chromium --version && chromedriver --version

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

ENV DISPLAY=:99

CMD ["streamlit", "run", "app.py", "--server.port", "8080", "--server.address", "0.0.0.0", "--server.headless", "true", "--browser.gatherUsageStats", "false"]
