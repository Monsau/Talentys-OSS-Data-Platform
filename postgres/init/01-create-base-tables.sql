-- ========================================
-- 01-create-base-tables.sql
-- Script de création des tables de base pour business_db
-- ========================================

-- Table customers (clients)
CREATE TABLE IF NOT EXISTS customers (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    address VARCHAR(255),
    city VARCHAR(100),
    country VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table products (produits)
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    category VARCHAR(100),
    sku VARCHAR(100) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table orders (commandes)
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id),
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'pending',
    total_amount DECIMAL(10,2) NOT NULL
);

-- Table order_items (articles commandés)
CREATE TABLE IF NOT EXISTS order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id),
    product_id INTEGER REFERENCES products(id),
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL
);

-- Insertion de données de base pour customers
INSERT INTO customers (first_name, last_name, email, phone, address, city, country) VALUES
    ('Jean', 'Dupont', 'jean.dupont@email.com', '+33123456789', '123 Rue de la Paix', 'Paris', 'France'),
    ('Marie', 'Martin', 'marie.martin@email.com', '+33987654321', '456 Avenue Victor Hugo', 'Lyon', 'France'),
    ('Pierre', 'Durand', 'pierre.durand@email.com', '+33555666777', '789 Boulevard Saint-Germain', 'Marseille', 'France'),
    ('Sophie', 'Leroy', 'sophie.leroy@email.com', '+33444555666', '321 Rue de Rivoli', 'Toulouse', 'France'),
    ('David', 'Bernard', 'david.bernard@email.com', '+33333444555', '654 Place Vendôme', 'Nice', 'France');

-- Insertion de données de base pour products
INSERT INTO products (name, description, price, category, sku) VALUES
    ('Ordinateur Portable', 'Laptop haute performance 15 pouces', 1299.99, 'Electronics', 'SKU-LAPTOP-001'),
    ('Smartphone', 'Téléphone intelligent dernière génération', 699.99, 'Electronics', 'SKU-PHONE-002'),
    ('Bureau Ergonomique', 'Bureau ajustable en hauteur', 899.99, 'Furniture', 'SKU-DESK-003'),
    ('Chaise de Bureau', 'Chaise ergonomique professionnelle', 399.99, 'Furniture', 'SKU-CHAIR-004'),
    ('Livre Technique', 'Manuel de programmation Python', 49.99, 'Books', 'SKU-BOOK-005'),
    ('Écran 4K', 'Moniteur 27 pouces Ultra HD', 599.99, 'Electronics', 'SKU-MONITOR-006'),
    ('Casque Audio', 'Casque sans fil haute qualité', 199.99, 'Electronics', 'SKU-HEADSET-007'),
    ('Bureau Compact', 'Petit bureau pour appartement', 299.99, 'Furniture', 'SKU-DESK-008'),
    ('Tapis de Yoga', 'Tapis antidérapant premium', 69.99, 'Sports', 'SKU-YOGA-009'),
    ('Montre Connectée', 'Smartwatch avec GPS', 399.99, 'Electronics', 'SKU-WATCH-010');

-- Insertion de données de base pour orders
INSERT INTO orders (customer_id, order_date, status, total_amount) VALUES
    (1, '2024-12-15 10:30:00', 'completed', 1349.98),
    (2, '2024-12-16 14:15:00', 'completed', 699.99),
    (3, '2024-12-17 09:45:00', 'pending', 1299.98),
    (1, '2024-12-18 16:20:00', 'completed', 649.98),
    (4, '2024-12-19 11:10:00', 'shipped', 399.99),
    (5, '2024-12-20 13:30:00', 'completed', 799.98),
    (2, '2024-12-21 08:50:00', 'processing', 199.99),
    (3, '2024-12-22 15:40:00', 'completed', 469.98);

-- Insertion de données de base pour order_items
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
    -- Commande 1
    (1, 1, 1, 1299.99),
    (1, 5, 1, 49.99),
    -- Commande 2
    (2, 2, 1, 699.99),
    -- Commande 3
    (3, 3, 1, 899.99),
    (3, 4, 1, 399.99),
    -- Commande 4
    (4, 6, 1, 599.99),
    (4, 5, 1, 49.99),
    -- Commande 5
    (5, 4, 1, 399.99),
    -- Commande 6
    (6, 7, 1, 199.99),
    (6, 6, 1, 599.99),
    -- Commande 7
    (7, 7, 1, 199.99),
    -- Commande 8
    (8, 9, 1, 69.99),
    (8, 4, 1, 399.99);

-- Création des index de base pour les performances
CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email);
CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_order_items_product_id ON order_items(product_id);
CREATE INDEX IF NOT EXISTS idx_products_sku ON products(sku);

RAISE NOTICE 'TABLES DE BASE CREEES AVEC SUCCES';
RAISE NOTICE 'Données insérées: 5 clients, 10 produits, 8 commandes';