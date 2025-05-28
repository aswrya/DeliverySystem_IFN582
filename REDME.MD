First make venv file in the project

script1:- python3 -m venv venv

script2:- source venv/bin/activate

script3:- pip3 install flask mysql-connector-python

script4:- pip3 install -r requirements.txt

script5:- pip3 install flask_mysqldb


Now create database

create database flask_mvc;

first excute only create table then after alter table script

create database flask_mvc;

CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100),
    email VARCHAR(100),
    password VARCHAR(255),
    role ENUM('user', 'admin') DEFAULT 'user'
);



food_item
CREATE TABLE food_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(5,2) NOT NULL,
    image_url VARCHAR(255) NOT NULL
);

ALTER TABLE food_items ADD COLUMN shop_id INT;

This can be excuted after shop table created

ALTER TABLE food_items ADD CONSTRAINT fk_shop FOREIGN KEY (shop_id) REFERENCES shops(id);



CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    total DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE orders 
ADD COLUMN name VARCHAR(100),
ADD COLUMN address TEXT,
ADD COLUMN contact VARCHAR(20),
ADD COLUMN delivery_method VARCHAR(50);

CREATE TABLE order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT,
    product_id INT,
    name VARCHAR(255),
    price DECIMAL(10,2),
    quantity INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE shops (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    location VARCHAR(255)
);

ALTER TABLE shops ADD COLUMN image_url VARCHAR(255);


store cart item in database

CREATE TABLE cart (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    name VARCHAR(255),
    price DECIMAL(10, 2),
    image_url VARCHAR(255),
    quantity INT DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (product_id) REFERENCES food_items(id)
);

