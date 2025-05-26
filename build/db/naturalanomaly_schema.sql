CREATE SCHEMA `naturalanomaly`;

CREATE USER 'anomaly_user' IDENTIFIED BY 'anom@l321';

GRANT ALL PRIVILEGES ON `naturalanomaly`.* TO 'anomaly_user';

FLUSH PRIVILEGES;