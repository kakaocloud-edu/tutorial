CREATE DATABASE IF NOT EXISTS history;
    
USE history;

CREATE TABLE IF NOT EXISTS access (
	    id INT AUTO_INCREMENT PRIMARY KEY,
	    date VARCHAR(255) NOT NULL
	);

	INSERT INTO access (date) VALUES ('hello:)');

CALL mysql.mnms_grant_right_user('admin', '%', 'all', '*', '*');

ALTER USER 'admin'@'%' IDENTIFIED WITH mysql_native_password BY 'admin1234';
