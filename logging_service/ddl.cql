CREATE KEYSPACE IF NOT EXISTS appearances
WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 2};

USE appearances;

CREATE TABLE IF NOT EXISTS by_person_id (
    person_id uuid,
    camera_id uuid,
    location text,
    appearance_time timestamp,
    PRIMARY KEY ((person_id), appearance_time)
) WITH compaction = {'class': 'DateTieredCompactionStrategy', 'max_sstable_age_days': 90};

CREATE TABLE IF NOT EXISTS by_location (
    person_id uuid,
    camera_id uuid,
    location text,
    appearance_time timestamp,
    PRIMARY KEY ((location), appearance_time, person_id)
) WITH CLUSTERING ORDER BY (appearance_time DESC)
  AND compaction = {'class': 'DateTieredCompactionStrategy', 'max_sstable_age_days': 90};

CREATE TABLE IF NOT EXISTS by_camera_id (
    location text,
    appearance_time timestamp,
    person_id uuid,
    camera_id uuid,
    PRIMARY KEY ((camera_id), appearance_time, person_id)
) WITH CLUSTERING ORDER BY (appearance_time DESC)
  AND compaction = {'class': 'DateTieredCompactionStrategy', 'max_sstable_age_days': 90};
