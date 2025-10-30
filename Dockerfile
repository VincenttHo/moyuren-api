# 使用 Python 3.11 slim image 作为基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# --- APT 加速配置 (使用国内镜像源) ---
# 直接写入清华大学 (TUNA) 的 Debian / apt 镜像源
# RUN echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian/ bullseye main contrib non-free" > /etc/apt/sources.list && \
#     echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian/ bullseye-updates main contrib non-free" >> /etc/apt/sources.list && \
#     echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian-security/ bullseye-security main contrib non-free" >> /etc/apt/sources.list && \
#     apt-get update && \
#     apt-get install -y \
 #        ca-certificates \
 #        gcc \
 #        curl \
 #        && rm -rf /var/lib/apt/lists/*
# --- APT 加速结束 ---

# 复制 requirements 文件
COPY requirements.txt .

# --- PIP 加速配置 (使用国内镜像源) ---
# 使用 -i 参数指定清华大学的 pip 镜像源
RUN pip install --upgrade pip && \
    pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
# --- PIP 加速结束 ---

# 复制应用代码
COPY . .

# 创建非 root 用户
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# 暴露端口
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# 默认运行命令
CMD ["python", "api.py"]
