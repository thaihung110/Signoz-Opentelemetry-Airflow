start the faust worker: faust -A hit_counter worker -l info (python -m faust -A hit_counter worker)
run producer: python kafka_producer.py
path to docker-compose: cd /mnt/d/signoz/deploy/docker/clickhouse-setup
env: conda activate faust_prj
run docker-compose: docker compose -f docker-compose.yaml up
