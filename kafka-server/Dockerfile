FROM confluentinc/cp-kafka:latest

# Chạy dưới quyền root để cài đặt các gói cần thiết
USER root

# Cài đặt Python và pip (ở đây dùng python3)
RUN yum update -y && \
    yum install -y python38 python38-pip && \
    yum clean all

# Cài đặt thư viện kafka-python để sử dụng trong streaming.py
RUN pip3 install kafka-python  

# Copy file streaming.py vào container
WORKDIR /opt/kafka
RUN chown -R 1001:1001 /opt/kafka /var/lib/kafka/data


# Chuyển về user mặc định nếu cần (tùy thuộc vào image gốc)
USER 1001

# Sử dụng entrypoint mặc định của image Kafka
CMD ["/etc/confluent/docker/run"]
