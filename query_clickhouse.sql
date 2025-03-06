-- Failure rate (dag failed/ dag runs)
SELECT
    countIf(attributes_string['category'] = 'DAG runs' AND attributes_string['state'] = 'failed') AS number_of_failed_DAGs,
    countIf(attributes_string['category'] = 'DAG runs') AS number_of_DAGs,
    if(
        countIf(attributes_string['category'] = 'DAG runs') = 0,
        0,
        toFloat64(countIf(attributes_string['category'] = 'DAG runs' AND attributes_string['state'] = 'failed')) / countIf(attributes_string['category'] = 'DAG runs') * 100
    ) AS percent_failed
FROM signoz_traces.signoz_index_v3
WHERE
    isNotNull(parseDateTimeBestEffortOrNull(attributes_string['run_start_date']))
    AND parseDateTimeBestEffortOrNull(attributes_string['run_start_date']) >= now() - INTERVAL 1 DAY;



-- Failure rate (tasks failed/ tasks runs)
SELECT
    countIf(attributes_string['category'] = 'scheduler' AND attributes_string['state'] = 'failed' AND attributes_string['dag_id'] != '') AS number_of_failed_tasks,
    countIf(attributes_string['category'] = 'scheduler' AND attributes_string['dag_id'] != '') AS number_of_tasks,
    (countIf(attributes_string['category'] = 'scheduler' AND attributes_string['state'] = 'failed') * 100.0 / nullIf(countIf(attributes_string['category'] = 'scheduler' AND attributes_string['dag_id'] != ''), 0)) AS error_rate_percentage
FROM signoz_traces.signoz_index_v3
WHERE
    isNotNull(parseDateTimeBestEffortOrNull(attributes_string['execution_date']))
    AND parseDateTimeBestEffortOrNull(attributes_string['execution_date']) >= now() - INTERVAL 1 HOUR;


-- Error count by time series
SELECT
    attributes_string['dag_id'],
    countIf(attributes_string['category'] = 'DAG runs' AND attributes_string['state'] = 'failed') AS number_of_error
FROM signoz_traces.signoz_index_v3
WHERE
    isNotNull(parseDateTimeBestEffortOrNull(attributes_string['run_start_date']))
    AND parseDateTimeBestEffortOrNull(attributes_string['run_start_date']) >= now() - INTERVAL 1 DAY
GROUP BY attributes_string['dag_id'];



    -- information for each dag run
    SELECT
        attributes_string['dag_id'] AS dag_id,
        attributes_string['run_duration'] AS run_duration,
        attributes_string['run_start_date'] AS run_start_date,
        attributes_string['run_end_date'] AS run_end_date,
        attributes_string['state'] AS state
    FROM signoz_traces.signoz_index_v3
    WHERE
        isNotNull(parseDateTimeBestEffortOrNull(attributes_string['run_start_date']))
        AND parseDateTimeBestEffortOrNull(attributes_string['run_start_date']) >= now() - INTERVAL 1 DAY
        AND attributes_string['run_duration'] > '0';


-- information for each task run
SELECT
    name,
    attributes_string['dag_id'] AS dag_id,
    attributes_string['start_date'] AS run_start_date,
    attributes_string['end_date'] AS run_end_date,
    attributes_string['state'] AS state
FROM signoz_traces.signoz_index_v3
WHERE
    isNotNull(parseDateTimeBestEffortOrNull(attributes_string['execution_date']))
    AND parseDateTimeBestEffortOrNull(attributes_string['execution_date']) >= now() - INTERVAL 3 DAY
    AND attributes_string['category'] = 'scheduler'
    AND attributes_string['dag_id'] != '';



--logs of tasks--
SELECT DISTINCT
    extract(attributes_string['log.file.path'], 'dag_id=([^/]+)') AS dag_id,
    extract(attributes_string['log.file.path'], 'task_id=([^/]+)') AS task_id,
    extract(attributes_string['log.file.path'], 'run_id=([^/]+)') AS run_id,
    arrayElement(splitByString('__', run_id), 1) AS run_type,  -- Lấy "manual" hoặc "scheduled"
    parseDateTimeBestEffortOrNull(arrayElement(splitByString('__', run_id), 2)) AS run_time,  -- Chuyển đổi sang DateTime
    body
FROM signoz_logs.logs_v2
WHERE has(attributes_string, 'log.file.path')
    AND body LIKE '%ERROR%';








