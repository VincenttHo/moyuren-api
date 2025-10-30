# 使用 Python 3.11 slim image 作为基础镜像
# 默认的基础镜像拉取可能仍会较慢，但后续 apt 和 pip 会加速
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# --- APT 加速配置 (使用国内镜像源) ---
# 1. 备份默认的 sources.list 文件
# 2. 替换为清华大学 (TUNA) 的 Debian / apt 镜像源
# 3. 安装系统依赖并清理
RUN cp /etc/apt/sources.list /etc/apt/sources.list.bak && \
    echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian/ bullseye main contrib non-free" > /etc/apt/sources.list && \
    echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian/ bullseye-updates main contrib non-free" >> /etc/apt/sources.list && \
    echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian-security/ bullseye-security main contrib non-free" >> /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y \
        gcc \
        curl \
        # 可选：如果需要，可以删除备份文件和恢复默认源，但通常不需要在容器中恢复
        # rm -f /etc/apt/sources.list && \
        # mv /etc/apt/sources.list.bak /etc/apt/sources.list && \
        rm -rf /var/lib/apt/lists/*
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
