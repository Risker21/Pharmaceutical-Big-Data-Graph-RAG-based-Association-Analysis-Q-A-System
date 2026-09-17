FROM python:3.10-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1
RUN apt-get update -qq && apt-get install -y --no-install-recommends gcc libcurl4-openssl-dev libssl-dev && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple && pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
COPY . .
RUN chmod +x run.sh
EXPOSE 8010
CMD ["./run.sh"]
