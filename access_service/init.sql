CREATE DATABASE IF NOT EXISTS permissions_db;

USE permissions_db;

CREATE TABLE IF NOT EXISTS cameras (
    camera_id VARCHAR(36),
    url TINYTEXT,
    location TINYTEXT,
    is_active BOOLEAN
);
