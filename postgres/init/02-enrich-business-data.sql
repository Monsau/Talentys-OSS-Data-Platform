-- ================================
-- ENRICHISSEMENT BASE DE DONNÉES BUSINESS
-- PostgreSQL - Données Complètes
-- ================================

-- Connexion: business_data database

-- ================================
-- 1. AJOUT DE NOUVELLES TABLES
-- ================================

-- Table suppliers (fournisseurs)
CREATE TABLE IF NOT EXISTS suppliers (
    supplier_id SERIAL PRIMARY KEY,
    supplier_name VARCHAR(100) NOT NULL,
    contact_name VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(20),
    address TEXT,
    city VARCHAR(50),
    country VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table categories 
CREATE TABLE IF NOT EXISTS categories (
    category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(50) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table inventory (stock)
CREATE TABLE IF NOT EXISTS inventory (
    inventory_id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(product_id),
    warehouse_location VARCHAR(50),
    quantity_available INTEGER DEFAULT 0,
    quantity_reserved INTEGER DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table promotions
CREATE TABLE IF NOT EXISTS promotions (
    promotion_id SERIAL PRIMARY KEY,
    promotion_name VARCHAR(100) NOT NULL,
    discount_percentage DECIMAL(5,2),
    start_date DATE,
    end_date DATE,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ================================
-- 2. MODIFICATION TABLES EXISTANTES
-- ================================

-- Ajouter colonnes à products
ALTER TABLE products ADD COLUMN IF NOT EXISTS supplier_id INTEGER REFERENCES suppliers(supplier_id);
ALTER TABLE products ADD COLUMN IF NOT EXISTS category_id INTEGER REFERENCES categories(category_id);
ALTER TABLE products ADD COLUMN IF NOT EXISTS weight_kg DECIMAL(8,3);
ALTER TABLE products ADD COLUMN IF NOT EXISTS dimensions VARCHAR(50);

-- Ajouter colonnes à orders
ALTER TABLE orders ADD COLUMN IF NOT EXISTS promotion_id INTEGER REFERENCES promotions(promotion_id);
ALTER TABLE orders ADD COLUMN IF NOT EXISTS discount_amount DECIMAL(10,2) DEFAULT 0;
ALTER TABLE orders ADD COLUMN IF NOT EXISTS tax_amount DECIMAL(10,2) DEFAULT 0;
ALTER TABLE orders ADD COLUMN IF NOT EXISTS shipping_cost DECIMAL(10,2) DEFAULT 0;

-- ================================
-- 3. INSERTION DONNÉES FOURNISSEURS
-- ================================

INSERT INTO suppliers (supplier_name, contact_name, email, phone, city, country) VALUES
('TechSupply Global', 'John Anderson', 'john@techsupply.com', '+1-555-0101', 'San Francisco', 'USA'),
('EuroElectronics', 'Marie Dubois', 'marie@euroelec.fr', '+33-1-23456789', 'Lyon', 'France'),
('AsiaComponents Ltd', 'Li Wei', 'li.wei@asiacomp.com', '+86-10-12345678', 'Shanghai', 'China'),
('NordicFurniture AB', 'Erik Larsson', 'erik@nordicfurn.se', '+46-8-87654321', 'Stockholm', 'Sweden'),
('MediterraneanGoods', 'Giuseppe Rossi', 'giuseppe@medgoods.it', '+39-06-11223344', 'Rome', 'Italy')
ON CONFLICT DO NOTHING;

-- ================================
-- 4. INSERTION CATÉGORIES
-- ================================

INSERT INTO categories (category_name, description) VALUES
('Electronics', 'Electronic devices and components'),
('Furniture', 'Home and office furniture'),
('Appliances', 'Home appliances and kitchen equipment'),
('Sports & Fitness', 'Sports equipment and fitness gear'),
('Books & Media', 'Books, magazines, and digital media'),
('Clothing', 'Apparel and accessories'),
('Automotive', 'Car parts and accessories'),
('Garden & Outdoor', 'Garden tools and outdoor equipment')
ON CONFLICT DO NOTHING;

-- ================================
-- 5. INSERTION PROMOTIONS
-- ================================

INSERT INTO promotions (promotion_name, discount_percentage, start_date, end_date, active) VALUES
('Winter Sale 2025', 25.00, '2025-01-01', '2025-02-28', true),
('Spring Collection', 15.00, '2025-03-01', '2025-04-30', true),
('Summer Clearance', 30.00, '2025-06-01', '2025-07-31', false),
('Back to School', 20.00, '2025-08-15', '2025-09-15', false),
('Black Friday Special', 40.00, '2025-11-25', '2025-11-30', false)
ON CONFLICT DO NOTHING;

-- ================================
-- 6. MISE À JOUR PRODUITS EXISTANTS
-- ================================

-- Assigner fournisseurs et catégories aux produits
UPDATE products SET 
    supplier_id = 1, 
    category_id = 1,
    weight_kg = 2.5,
    dimensions = '35x25x3 cm'
WHERE product_name = 'Laptop Pro';

UPDATE products SET 
    supplier_id = 1, 
    category_id = 1,
    weight_kg = 0.2,
    dimensions = '15x7x1 cm'
WHERE product_name = 'Smartphone X';

UPDATE products SET 
    supplier_id = 4, 
    category_id = 2,
    weight_kg = 15.0,
    dimensions = '60x60x120 cm'
WHERE product_name = 'Office Chair';

UPDATE products SET 
    supplier_id = 5, 
    category_id = 3,
    weight_kg = 3.2,
    dimensions = '30x20x35 cm'
WHERE product_name = 'Coffee Maker';

UPDATE products SET 
    supplier_id = 2, 
    category_id = 4,
    weight_kg = 0.8,
    dimensions = '30x20x15 cm'
WHERE product_name = 'Running Shoes';

-- ================================
-- 7. AJOUT DE NOUVEAUX PRODUITS
-- ================================

INSERT INTO products (product_name, category_id, supplier_id, price, stock_quantity, description, weight_kg, dimensions) VALUES
('Gaming Monitor 4K', 1, 1, 599.99, 20, '32-inch 4K gaming monitor', 8.5, '75x45x25 cm'),
('Wireless Keyboard', 1, 1, 79.99, 50, 'Mechanical wireless keyboard', 1.2, '45x15x3 cm'),
('Standing Desk', 2, 4, 399.99, 15, 'Height-adjustable standing desk', 25.0, '120x60x75 cm'),
('Yoga Mat', 4, 2, 29.99, 100, 'Non-slip yoga mat', 1.5, '180x60x0.5 cm'),
('Smart Watch', 1, 3, 249.99, 30, 'Fitness tracking smartwatch', 0.1, '4x4x1 cm'),
('Bookshelf', 2, 4, 149.99, 25, '5-tier wooden bookshelf', 18.0, '80x30x180 cm'),
('Blender Pro', 3, 5, 89.99, 40, 'High-speed professional blender', 4.2, '20x20x40 cm'),
('Mountain Bike', 4, 2, 799.99, 10, '21-speed mountain bicycle', 15.0, '180x65x110 cm');

-- ================================
-- 8. AJOUT COMMANDES SUPPLÉMENTAIRES
-- ================================

-- Nouvelles commandes avec promotions
INSERT INTO orders (customer_id, order_date, total_amount, status, promotion_id, discount_amount, tax_amount, shipping_cost) VALUES
(1, '2025-01-20', 524.99, 'completed', 1, 174.99, 52.50, 15.00),
(2, '2025-01-21', 319.98, 'shipped', 1, 79.98, 32.00, 12.00),
(3, '2025-01-22', 149.99, 'processing', 2, 22.50, 15.00, 10.00),
(4, '2025-01-23', 679.99, 'completed', NULL, 0.00, 68.00, 25.00),
(5, '2025-01-24', 459.98, 'pending', 2, 68.99, 46.00, 18.00),
(1, '2025-01-25', 89.99, 'completed', NULL, 0.00, 9.00, 8.00),
(2, '2025-01-26', 249.99, 'shipped', 2, 37.50, 25.00, 12.00);

-- ================================
-- 9. AJOUT INVENTORY RECORDS
-- ================================

INSERT INTO inventory (product_id, warehouse_location, quantity_available, quantity_reserved) VALUES
(1, 'Warehouse-A', 45, 5),
(2, 'Warehouse-A', 90, 10),
(3, 'Warehouse-B', 20, 5),
(4, 'Warehouse-C', 25, 5),
(5, 'Warehouse-A', 70, 5),
(6, 'Warehouse-B', 18, 2),
(7, 'Warehouse-C', 45, 5),
(8, 'Warehouse-B', 12, 3),
(9, 'Warehouse-A', 95, 5),
(10, 'Warehouse-A', 28, 2),
(11, 'Warehouse-B', 20, 5),
(12, 'Warehouse-C', 35, 5),
(13, 'Warehouse-B', 8, 2);

-- ================================
-- 10. VUES MÉTIER (BUSINESS VIEWS)
-- ================================

-- Vue des ventes par catégorie
CREATE OR REPLACE VIEW sales_by_category AS
SELECT 
    c.category_name,
    COUNT(DISTINCT o.order_id) as total_orders,
    SUM(oi.quantity) as total_items_sold,
    SUM(oi.total_price) as total_revenue,
    AVG(oi.unit_price) as avg_unit_price
FROM categories c
JOIN products p ON c.category_id = p.category_id
JOIN order_items oi ON p.product_id = oi.product_id
JOIN orders o ON oi.order_id = o.order_id
WHERE o.status = 'completed'
GROUP BY c.category_id, c.category_name
ORDER BY total_revenue DESC;

-- Vue du stock critique
CREATE OR REPLACE VIEW low_stock_alert AS
SELECT 
    p.product_name,
    c.category_name,
    s.supplier_name,
    i.quantity_available,
    i.quantity_reserved,
    (i.quantity_available - i.quantity_reserved) as available_stock,
    p.price * (i.quantity_available - i.quantity_reserved) as stock_value
FROM products p
JOIN categories c ON p.category_id = c.category_id
JOIN suppliers s ON p.supplier_id = s.supplier_id
JOIN inventory i ON p.product_id = i.product_id
WHERE (i.quantity_available - i.quantity_reserved) < 20
ORDER BY available_stock ASC;

-- Vue des top customers
CREATE OR REPLACE VIEW top_customers AS
SELECT 
    cust.customer_id,
    cust.first_name || ' ' || cust.last_name as customer_name,
    cust.email,
    cust.city,
    cust.country,
    COUNT(o.order_id) as total_orders,
    SUM(o.total_amount) as total_spent,
    AVG(o.total_amount) as avg_order_value,
    MAX(o.order_date) as last_order_date
FROM customers cust
LEFT JOIN orders o ON cust.customer_id = o.customer_id
GROUP BY cust.customer_id, cust.first_name, cust.last_name, cust.email, cust.city, cust.country
HAVING COUNT(o.order_id) > 0
ORDER BY total_spent DESC;

-- ================================
-- 11. FONCTIONS UTILES
-- ================================

-- Fonction pour calculer le profit
CREATE OR REPLACE FUNCTION calculate_profit(
    product_cost DECIMAL,
    selling_price DECIMAL,
    quantity INTEGER
) RETURNS DECIMAL AS $$
BEGIN
    RETURN (selling_price - product_cost) * quantity;
END;
$$ LANGUAGE plpgsql;

-- ================================
-- 12. INDEXES POUR PERFORMANCE
-- ================================

CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_order_date ON orders(order_date);
CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_products_category_id ON products(category_id);
CREATE INDEX IF NOT EXISTS idx_products_supplier_id ON products(supplier_id);
CREATE INDEX IF NOT EXISTS idx_inventory_product_id ON inventory(product_id);

-- ================================
-- 13. PERMISSIONS
-- ================================

-- Accorder permissions à dbt_user
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO dbt_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO dbt_user;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO dbt_user;

-- ================================
-- RÉSUMÉ DES DONNÉES CRÉÉES
-- ================================

-- Afficher statistiques
DO $$
BEGIN
    RAISE NOTICE '================================';
    RAISE NOTICE 'BASE DE DONNÉES ENRICHIE - STATISTIQUES';
    RAISE NOTICE '================================';
    RAISE NOTICE 'Tables créées: suppliers, categories, inventory, promotions';
    RAISE NOTICE 'Vues métier: sales_by_category, low_stock_alert, top_customers';
    RAISE NOTICE 'Fonctions: calculate_profit';
    RAISE NOTICE 'Indexes: 6 index de performance';
    RAISE NOTICE '================================';
END $$;