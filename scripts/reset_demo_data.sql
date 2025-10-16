-- Nettoyage et réinitialisation complète avec IDs cohérents

-- 1. Nettoyage
TRUNCATE TABLE customers CASCADE;
DROP TABLE IF EXISTS minio_customers_simulation;

-- 2. Réinitialiser la séquence pour repartir à 1
ALTER SEQUENCE customers_id_seq RESTART WITH 1;

-- 3. Insérer les 10 clients PostgreSQL
INSERT INTO customers (first_name, last_name, email, phone, address, city, country, created_at) VALUES
('Jean', 'Dupont', 'jean.dupont@email.fr', '+33612345678', '10 rue de Paris', 'Paris', 'France', '2024-01-15'),
('Marie', 'Martin', 'marie.martin@email.fr', '+33623456789', '25 avenue des Champs', 'Lyon', 'France', '2024-02-20'),
('Pierre', 'Durand', 'pierre.durand@email.fr', '+33634567890', '5 boulevard Victor Hugo', 'Marseille', 'France', '2024-03-10'),
('Sophie', 'Bernard', 'sophie.bernard@email.fr', '+33645678901', '15 rue de la République', 'Toulouse', 'France', '2024-04-05'),
('Luc', 'Petit', 'luc.petit@email.fr', '+33656789012', '30 place du Marché', 'Nice', 'France', '2024-05-12'),
('Julie', 'Robert', 'julie.robert@email.fr', '+33667890123', '8 rue Nationale', 'Nantes', 'France', '2024-06-18'),
('Thomas', 'Richard', 'thomas.richard@email.fr', '+33678901234', '20 avenue Jean Jaurès', 'Strasbourg', 'France', '2024-07-22'),
('Emma', 'Moreau', 'emma.moreau@email.fr', '+33689012345', '12 rue du Commerce', 'Bordeaux', 'France', '2024-08-30'),
('Lucas', 'Simon', 'lucas.simon@email.fr', '+33690123456', '45 boulevard Gambetta', 'Lille', 'France', '2024-09-14'),
('Camille', 'Laurent', 'camille.laurent@email.fr', '+33601234567', '3 place de la Liberté', 'Rennes', 'France', '2024-10-01');

-- 4. Créer la table MinIO avec IDs cohérents
CREATE TABLE minio_customers_simulation (
    customer_id INTEGER PRIMARY KEY,
    name VARCHAR(200),
    email VARCHAR(100),
    country VARCHAR(50),
    signup_date DATE
);

-- 5. Insérer données MinIO avec écarts volontaires
INSERT INTO minio_customers_simulation (customer_id, name, email, country, signup_date) VALUES
-- 6 clients parfaitement matchés (IDs 1-6)
(1, 'Jean Dupont', 'jean.dupont@email.fr', 'France', '2024-01-15'),
(2, 'Marie Martin', 'marie.martin@email.fr', 'France', '2024-02-20'),
(3, 'Pierre Durand', 'pierre.durand@email.fr', 'France', '2024-03-10'),
(4, 'Sophie Bernard', 'sophie.bernard@email.fr', 'France', '2024-04-05'),
(5, 'Luc Petit', 'luc.petit@email.fr', 'France', '2024-05-12'),
(6, 'Julie Robert', 'julie.robert@email.fr', 'France', '2024-06-18'),

-- Email différent (ID 7)
(7, 'Thomas Richard', 'thomas.richard@gmail.com', 'France', '2024-07-22'),

-- Country différent (ID 8)
(8, 'Emma Moreau', 'emma.moreau@email.fr', 'Belgium', '2024-08-30'),

-- IDs 9-10 absents (dans PG mais pas MinIO)

-- Clients uniquement dans MinIO (IDs 11-12)
(11, 'Antoine Dubois', 'antoine.dubois@email.fr', 'France', '2024-10-10'),
(12, 'Claire Leroy', 'claire.leroy@email.fr', 'France', '2024-10-12');

-- 6. Vérifications
SELECT 'PostgreSQL' as source, COUNT(*) as count, MIN(id) as min_id, MAX(id) as max_id FROM customers
UNION ALL
SELECT 'MinIO', COUNT(*), MIN(customer_id), MAX(customer_id) FROM minio_customers_simulation;

-- Vérification des IDs
SELECT 
    'Customers IDs' as description,
    string_agg(id::text, ', ' ORDER BY id) as ids
FROM customers
UNION ALL
SELECT 
    'MinIO IDs',
    string_agg(customer_id::text, ', ' ORDER BY customer_id)
FROM minio_customers_simulation;
