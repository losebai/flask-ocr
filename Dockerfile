# 使用官方Python映像作为基础映像
FROM python:3.9-slim-buster

# 设置工作目录
WORKDIR /app

# 复制应用程序文件和依赖项
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .

# 暴露应用程序端口
EXPOSE 8888

# 定义应用程序启动命令
CMD [ "python", "./main.py" ]