CREATE DATABASE IF NOT EXISTS permissions_db;

USE permissions_db;

CREATE TABLE IF NOT EXISTS permissions (
  id INT AUTO_INCREMENT PRIMARY KEY,
  uuid VARCHAR(36),
  name VARCHAR(255),
  camera_id VARCHAR(36),
  permission INT
);
