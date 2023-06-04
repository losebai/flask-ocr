# 使用官方Python映像作为基础映像
#FROM python:3.9-slim-buster

FROM ubuntu:20.04

ENV TZ=Asia/Shanghai 
RUN echo "${TZ}" > /etc/timezone \ 
&& ln -sf /usr/share/zoneinfo/${TZ} /etc/localtime \ 
&& apt update \ 
&& apt install -y tzdata \ 
&& rm -rf /var/lib/apt/lists/*



RUN apt-get update && apt-get install --no-install-recommends -y python3.9 python3.9-dev python3.9-venv python3-pip python3-wheel build-essential && \
   apt-get clean && rm -rf /var/lib/apt/lists/*



# create and activate virtual environment

ARG DEBIAN_FRONTEND=noninteractive


RUN python3.9 -m venv /opt/venv-ocr
ENV PATH="/opt/venv-ocr/bin:$PATH"

RUN pip3 install paddlepaddle -i https://mirror.baidu.com/pypi/simple

RUN pip3 install "paddleocr>=2.0.1"  -i https://mirror.baidu.com/pypi/simple
RUN pip3 install flask 
RUN pip3 install gunicorn 

# 设置工作目录
WORKDIR /app


# 复制应用程序文件和依赖项
COPY requirements.txt .
RUN pip3 install  -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
COPY . .

# 暴露应用程序端口
EXPOSE 8888

# 定义应用程序启动命令
CMD ["gunicorn", "-w", "3", "-b", "0.0.0.0:8888", "app:app"]
