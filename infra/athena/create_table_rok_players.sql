CREATE EXTERNAL TABLE IF NOT EXISTS rok_ingestion_data.rok_players_curated (
  id STRING,
  name STRING,
  power BIGINT,
  killpoints BIGINT,
  deads BIGINT,
  `t1 kills` BIGINT,
  `t2 kills` BIGINT,
  `t3 kills` BIGINT,
  `t4 kills` BIGINT,
  `t5 kills` BIGINT,
  `total kills` BIGINT,
  `t45 kills` BIGINT,
  ranged BIGINT,
  `rss gathered` BIGINT,
  `rss assistance` BIGINT,
  helps BIGINT,
  alliance STRING,
  snapshot_date STRING,
  ingested_at STRING,
  run_id STRING,
  record_hash STRING
)
PARTITIONED BY (
  kingdom STRING,
  dt STRING
)
STORED AS PARQUET
LOCATION 's3://rok-ingestion-full-octopus/curated/source=rok_players/'
TBLPROPERTIES (
  'parquet.compression'='SNAPPY',
  'has_encrypted_data'='false'
);
