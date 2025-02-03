# Sử dụng image chính thức của Apache Airflow
FROM apache/airflow:2.4.1

# Đặt biến môi trường cho Airflow
ENV AIRFLOW_HOME=/opt/airflow

# Cài đặt các dependencies cần thiết
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# Cài đặt OpenTelemetry và các gói liên quan
RUN pip install --no-cache-dir \
    opentelemetry-sdk==1.20.0 \
    opentelemetry-api==1.20.0 \
    opentelemetry-exporter-otlp==1.20.0
RUN pip install 'apache-airflow[otel]'

# Sao chép các DAGs, plugins và thư mục cần thiết vào container
# COPY dags/ $AIRFLOW_HOME/dags/
# COPY plugins/ $AIRFLOW_HOME/plugins/
# COPY json_data/ $AIRFLOW_HOME/json_data/
# COPY generators/ $AIRFLOW_HOME/generators/
# COPY miners/ $AIRFLOW_HOME/miners/
# COPY storage/ $AIRFLOW_HOME/storage/
# COPY streams/ $AIRFLOW_HOME/streams/
# COPY common/ $AIRFLOW_HOME/common/
# COPY template/ $AIRFLOW_HOME/template/
# COPY producer/ $AIRFLOW_HOME/producer/
# COPY config/ $AIRFLOW_HOME/config/

# Chuyển đổi entrypoint để sử dụng airflow command
ENTRYPOINT ["docker-entrypoint.sh"]

# Đặt lệnh mặc định khi container chạy
CMD ["webserver"]