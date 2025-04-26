# 使用官方精简 Python 镜像
FROM python:3.12-slim

# 环境变量：推荐实践
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 设置工作目录
WORKDIR /app

# 先单独复制 requirements.txt 并安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 再复制整个项目（避免改一行代码就触发重新安装依赖）
COPY . .

# 默认命令：迁移数据库+启动开发服务器
CMD ["sh", "-c", "\
echo '▶ Starting migration...' && \
python manage.py migrate --noinput && \
echo '✅ Migrate done. Now running server...' && \
python manage.py runserver 0.0.0.0:8000"]

