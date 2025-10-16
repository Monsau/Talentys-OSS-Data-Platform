#!/bin/bash
set -e

# Créer des bases de données multiples
echo "Creating additional databases..."

# Base de données business
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE business_data;
    CREATE DATABASE analytics_warehouse;
    
    -- Créer utilisateur business
    CREATE USER business_user WITH PASSWORD 'business_password';
    GRANT ALL PRIVILEGES ON DATABASE business_data TO business_user;
    GRANT ALL PRIVILEGES ON DATABASE analytics_warehouse TO business_user;
    
    -- Connecter à business_data pour créer des tables d'exemple
    \c business_data;
    
    -- Schema et tables d'exemple
    CREATE SCHEMA IF NOT EXISTS public;
    
    -- Table customers
    CREATE TABLE IF NOT EXISTS customers (
        customer_id SERIAL PRIMARY KEY,
        first_name VARCHAR(50) NOT NULL,
        last_name VARCHAR(50) NOT NULL,
        email VARCHAR(100) UNIQUE,
        phone VARCHAR(20),
        address TEXT,
        city VARCHAR(50),
        country VARCHAR(50),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Table orders
    CREATE TABLE IF NOT EXISTS orders (
        order_id SERIAL PRIMARY KEY,
        customer_id INTEGER REFERENCES customers(customer_id),
        order_date DATE NOT NULL,
        total_amount DECIMAL(10,2) NOT NULL,
        status VARCHAR(20) DEFAULT 'pending',
        shipping_address TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Table order_items
    CREATE TABLE IF NOT EXISTS order_items (
        item_id SERIAL PRIMARY KEY,
        order_id INTEGER REFERENCES orders(order_id),
        product_name VARCHAR(100) NOT NULL,
        quantity INTEGER NOT NULL,
        unit_price DECIMAL(8,2) NOT NULL,
        total_price DECIMAL(10,2) NOT NULL
    );
    
    -- Table products
    CREATE TABLE IF NOT EXISTS products (
        product_id SERIAL PRIMARY KEY,
        product_name VARCHAR(100) NOT NULL,
        category VARCHAR(50),
        price DECIMAL(8,2) NOT NULL,
        stock_quantity INTEGER DEFAULT 0,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Insérer des données d'exemple
    INSERT INTO customers (first_name, last_name, email, phone, city, country) VALUES
    ('John', 'Doe', 'john.doe@email.com', '+1234567890', 'New York', 'USA'),
    ('Jane', 'Smith', 'jane.smith@email.com', '+1234567891', 'London', 'UK'),
    ('Pierre', 'Dupont', 'pierre.dupont@email.com', '+33123456789', 'Paris', 'France'),
    ('Maria', 'Garcia', 'maria.garcia@email.com', '+34123456789', 'Madrid', 'Spain'),
    ('Ahmed', 'Hassan', 'ahmed.hassan@email.com', '+201234567890', 'Cairo', 'Egypt');
    
    INSERT INTO products (product_name, category, price, stock_quantity, description) VALUES
    ('Laptop Pro', 'Electronics', 1299.99, 50, 'High-performance laptop'),
    ('Smartphone X', 'Electronics', 699.99, 100, 'Latest smartphone model'),
    ('Office Chair', 'Furniture', 249.99, 25, 'Ergonomic office chair'),
    ('Coffee Maker', 'Appliances', 89.99, 30, 'Automatic coffee maker'),
    ('Running Shoes', 'Sports', 129.99, 75, 'Professional running shoes');
    
    INSERT INTO orders (customer_id, order_date, total_amount, status) VALUES
    (1, '2025-01-15', 1299.99, 'completed'),
    (2, '2025-01-16', 699.99, 'shipped'),
    (3, '2025-01-17', 339.98, 'processing'),
    (4, '2025-01-18', 89.99, 'completed'),
    (5, '2025-01-19', 129.99, 'pending');
    
    INSERT INTO order_items (order_id, product_name, quantity, unit_price, total_price) VALUES
    (1, 'Laptop Pro', 1, 1299.99, 1299.99),
    (2, 'Smartphone X', 1, 699.99, 699.99),
    (3, 'Office Chair', 1, 249.99, 249.99),
    (3, 'Coffee Maker', 1, 89.99, 89.99),
    (4, 'Coffee Maker', 1, 89.99, 89.99),
    (5, 'Running Shoes', 1, 129.99, 129.99);
    
    -- Permissions pour business_user
    GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO business_user;
    GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO business_user;
    
    echo "✅ Base de données business_data initialisée avec succès"
EOSQL

echo "✅ Toutes les bases de données ont été créées avec succès"