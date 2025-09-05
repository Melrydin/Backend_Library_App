docker run --name some-mysql -e MYSQL_ROOT_PASSWORD=password -p 3306:3306 -d mysql:latest

Go to the Server Terminal and run

CREATE DATABASE library;

CREATE USER 'libraryAPI'@'%' IDENTIFIED BY 'hallowelt';

GRANT ALL PRIVILEGES ON library.* TO 'libraryAPI'@'%';

FLUSH PRIVILEGES;

use library;

CREATE TABLE books (
    id INTEGER unsigned NOT NULL AUTO_INCREMENT,
    category ENUM('Manga', 'Novel', 'Technical'),
    title TINYTEXT NOT NULL,
    series TINYINT(1) NOT NULL,
    volume TINYINT unsigned,
    author TINYTEXT NOT NULL,
    publisher TINYTEXT NOT NULL,
    price DOUBLE NOT NULL,
    isbn BIGINT(13) unsigned NOT NULL,
    wishlist TINYINT(1) NOT NULL,
    gift TINYINT(1) NOT NULL,
    borrow TINYINT(1) NOT NULL,
    releaseDate DATE,
    payDate DATE,
    startDate DATE,
    endDate DATE,
    CONSTRAINT pk_books PRIMARY KEY (id));
