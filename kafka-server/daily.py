import requests
import json
from bs4 import BeautifulSoup
from kafka import KafkaProducer
from datetime import datetime, timedelta

def json_serializer(data):
    return json.dumps(data).encode('utf-8')

def str_serializer(data):
    return data.encode('utf-8')

# Khởi tạo Kafka Producer (cập nhật bootstrap_servers nếu cần)
producer = KafkaProducer(
    bootstrap_servers=['kafka-server:9092'],
    value_serializer=json_serializer,
    key_serializer=str_serializer
)

# Khởi tạo ngày bắt đầu từ "20110219"
current_date = datetime.strptime("20110219", "%Y%m%d")

# URL mẫu, định dạng: https://kworb.net/ww/archive/YYYYMMDD.html
url_template = "https://kworb.net/ww/archive/{}.html"

print("Bắt đầu xử lý dữ liệu từ URL. Dùng Ctrl+C để dừng quá trình.")

try:
    while True:
        # Tạo chuỗi ngày theo định dạng YYYYMMDD
        date_str = current_date.strftime("%Y%m%d")
        url = url_template.format(date_str)
        print(f"Đang xử lý URL: {url}")

        # Gửi request để lấy nội dung HTML
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (compatible; Python script)"})
        if response.status_code != 200:
            print(f"Lỗi khi truy cập URL {url} với mã lỗi: {response.status_code}. Bỏ qua ngày {date_str}.")
        else:
            content = response.text
            soup = BeautifulSoup(content, "html.parser")

            # Tìm table chính
            table = soup.find("table")
            if table is None:
                print(f"Không tìm thấy table trong URL: {url}.")
            else:
                rows = table.find_all("tr")
                if not rows:
                    print(f"Không có dữ liệu trong table tại URL: {url}.")
                else:
                    # Dòng đầu tiên làm header
                    header_cells = rows[0].find_all(["th", "td"])
                    headers_list = [cell.get_text(strip=True) for cell in header_cells]

                    # Xử lý các dòng dữ liệu còn lại
                    for row in rows[1:]:
                        cells = row.find_all("td")
                        if not cells:
                            continue
                        row_data = [cell.get_text(strip=True) for cell in cells]
                        record = dict(zip(headers_list, row_data))
                        # Gửi record vào Kafka topic "daily" với key là ngày (YYYYMMDD)
                        producer.send('daily', key=date_str, value=record)
                    print(f"Đã gửi dữ liệu từ URL {url} vào Kafka topic 'daily' với key: {date_str}")
                # Đảm bảo gửi hết các message của ngày đó
                producer.flush()

        # Tăng ngày lên 1 đơn vị
        current_date += timedelta(days=1)

except KeyboardInterrupt:
    print("Quá trình xử lý đã dừng bởi người dùng.")

print("Quá trình xử lý hoàn thành.")

