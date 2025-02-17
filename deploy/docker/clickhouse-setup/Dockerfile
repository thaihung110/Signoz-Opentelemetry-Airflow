# =============================================================================
# dockefile for building airflow

# change version from 2.4.1 to 2.7.3
FROM apache/airflow:2.7.3

# Đặt biến môi trường cho Airflow
ENV AIRFLOW_HOME=/opt/airflow

USER root
RUN pip install apache-airflow-providers-elasticsearch
USER airflow

# Cài đặt OpenTelemetry và các gói liên quan
RUN pip install --no-cache-dir \
    opentelemetry-sdk==1.20.0 \
    opentelemetry-api==1.20.0 \
    opentelemetry-exporter-otlp==1.20.0
RUN pip install 'apache-airflow[otel]'

# install opentelemetry-exporter-otlp-proto-http
RUN pip install opentelemetry-exporter-otlp-proto-http

# Add airflow user to root group
RUN usermod -a -G root airflow

# Set umask to make files writable by group
RUN echo "umask 0002" >> /home/airflow/.bashrc

# Create log directory and set permissions
RUN mkdir -p /opt/airflow/logs && \
    chown -R root:root /opt/airflow/logs && \
    chmod -R 777 /opt/airflow/logs

# Chuyển đổi entrypoint để sử dụng airflow command
ENTRYPOINT ["docker-entrypoint.sh"]

# Đặt lệnh mặc định khi container chạy
CMD ["webserver"]

# =============================================================================