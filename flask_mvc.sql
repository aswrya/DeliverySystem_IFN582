-- Create the database
CREATE DATABASE IF NOT EXISTS flask_mvc;
USE flask_mvc;

-- Users table
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    password VARCHAR(255),
    role ENUM('user', 'admin') DEFAULT 'user'
);

-- Shops table
CREATE TABLE shops (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    location VARCHAR(255),
    image_url VARCHAR(255)
);

-- Food items table
CREATE TABLE food_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(5,2) NOT NULL,
    image_url VARCHAR(255) NOT NULL,
    shop_id INT,
    CONSTRAINT fk_shop FOREIGN KEY (shop_id) REFERENCES shops(id)
);

-- Orders table
CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    total DECIMAL(10,2),
    name VARCHAR(100),
    address TEXT,
    contact VARCHAR(20),
    delivery_method VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Order items table
CREATE TABLE order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT,
    product_id INT,
    name VARCHAR(255),
    price DECIMAL(10,2),
    quantity INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (product_id) REFERENCES food_items(id)
);

-- Cart table
CREATE TABLE cart (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    name VARCHAR(255),
    price DECIMAL(10,2),
    image_url VARCHAR(255),
    quantity INT DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (product_id) REFERENCES food_items(id)
);

-- sample data for shop table

INSERT INTO shops (id, name, description, location, image_url) VALUES
(1, 'dominos', 'We deliver good and testy foods', 'zillmere', 'images/dominos_logo.jpg'),
(2, 'Mac donald', 'Foods from MCdoald', 'Margate St. Brisbane', 'images/mcd.jpg'),
(3, 'Pizza Hut', 'Food and drink from pizza hut', 'Queen St QLD', 'images/pizza_hut.avif'),
(4, 'Bites', 'food delivery', 'Percy ST QLD', 'images/bites.jpeg');


-- sample data for food_items table

INSERT INTO food_items (id, name, price, image_url, shop_id) VALUES
(1,'Chi. Burger',13.00,'images/burger.svg',1),
(2,'Pizza',18.00,'images/pizza_full.png',1),
(3,'Pizza Slice',6.00,'images/pizza.png',1),
(4,'Burger',12.00,'images/burger.svg',2),
(5,'Chips',23.00,'images/ice-cream.png',2),
(6,'Coke',4.39,'images/coco-cola.png',2),
(7,'Chicken leg',24.00,'images/meat-icon.svg',3),
(8,'Fanta',4.99,'images/fanta.jpg',3),
(9,'BBQ-Ribs',35.00,'images/bbq-ribs.png',4),
(10,'Hotdogs',5.00,'images/hotdog.jpg',4),
(11,'Tacos',14.00,'images/dish-3.png',4),
(12,'Sushi',5.00,'images/Sushi.webp',1),
(13,'Donuts',4.00,'images/donuts.png',4),
(14,'Sandwich',3.00,'images/toastbread.png',4),
(15,'Rolls',12.00,'images/wrap.png',4);