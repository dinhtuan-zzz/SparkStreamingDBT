# Sử dụng image Python chính thức làm base image
FROM python:3.9-slim-buster

# Đặt thư mục làm việc trong container
WORKDIR /app

# Sao chép tệp requirements.txt vào container
COPY requirements.txt .

# Cài đặt các dependencies Python
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép mã nguồn API vào container
COPY . .

# Mở cổng API (giả sử API của bạn chạy trên cổng 8000)
EXPOSE 8000

# Lệnh để chạy API
CMD ["python3", "main.py"]
