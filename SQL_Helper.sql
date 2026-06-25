docker run --name mysql --network library-network -e MYSQL_ROOT_PASSWORD=password -p 3306:3306 -d mysql:8.4.0

docker exec -it mysql mysql -u root -ppassword

CREATE DATABASE IF NOT EXISTS `library` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'libraryAPI'@'%' IDENTIFIED BY 'PASSWORD';
GRANT ALL PRIVILEGES ON `library`.* TO 'libraryAPI'@'%';
FLUSH PRIVILEGES;

USE library;

CREATE TABLE IF NOT EXISTS books (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    category ENUM('Manga', 'Novel', 'Technical') NOT NULL,
    title VARCHAR(255) NOT NULL,
    series TINYINT(1) NOT NULL DEFAULT 0,
    volume INT UNSIGNED NOT NULL,
    author VARCHAR(150) NOT NULL,
    publisher VARCHAR(150) NOT NULL,
    price DOUBLE NOT NULL,
    isbn VARCHAR(13) NOT NULL UNIQUE,
    wishlist TINYINT(1) NOT NULL DEFAULT 1,
    gift TINYINT(1) NOT NULL DEFAULT 0,
    borrow TINYINT(1) NOT NULL DEFAULT 0,
    releaseDate DATE DEFAULT NULL,
    payDate DATE DEFAULT NULL,
    startDate DATE DEFAULT NULL,
    endDate DATE DEFAULT NULL,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
