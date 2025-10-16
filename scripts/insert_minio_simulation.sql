-- Données simulées pour MinIO (avec écarts volontaires pour tester la comparaison)
-- On va créer une table temporaire dans PostgreSQL pour simuler MinIO

-- Création d'une table minio_customers_simulation
DROP TABLE IF EXISTS minio_customers_simulation;

CREATE TABLE minio_customers_simulation (
    customer_id INTEGER,
    name VARCHAR(200),
    email VARCHAR(100),
    country VARCHAR(50),
    signup_date DATE
);

-- Insertion de données avec écarts volontaires:
-- - 8 clients en commun avec PostgreSQL (mêmes IDs)
-- - 2 clients avec emails différents (quality issues)
-- - 1 client avec country différent
-- - 2 clients uniquement dans MinIO (IDs 11-12)
-- - 2 clients manquants de PostgreSQL (IDs 9-10 absents)

INSERT INTO minio_customers_simulation (customer_id, name, email, country, signup_date) VALUES
-- Clients parfaitement matchés (IDs 1-6)
(1, 'Jean Dupont', 'jean.dupont@email.fr', 'France', '2024-01-15'),
(2, 'Marie Martin', 'marie.martin@email.fr', 'France', '2024-02-20'),
(3, 'Pierre Durand', 'pierre.durand@email.fr', 'France', '2024-03-10'),
(4, 'Sophie Bernard', 'sophie.bernard@email.fr', 'France', '2024-04-05'),
(5, 'Luc Petit', 'luc.petit@email.fr', 'France', '2024-05-12'),
(6, 'Julie Robert', 'julie.robert@email.fr', 'France', '2024-06-18'),

-- Client avec email différent (ID 7)
(7, 'Thomas Richard', 'thomas.richard@gmail.com', 'France', '2024-07-22'),  -- Email différent!

-- Client avec country différent (ID 8)
(8, 'Emma Moreau', 'emma.moreau@email.fr', 'Belgium', '2024-08-30'),  -- Country différent!

-- Clients 9-10 ABSENTS de MinIO (quality issue: missing data)

-- Clients uniquement dans MinIO (IDs 11-12)
(11, 'Antoine Dubois', 'antoine.dubois@email.fr', 'France', '2024-10-10'),
(12, 'Claire Leroy', 'claire.leroy@email.fr', 'France', '2024-10-12');

-- Vérification
SELECT 
    COUNT(*) as total_minio_customers,
    MIN(signup_date) as first_date,
    MAX(signup_date) as last_date,
    COUNT(DISTINCT country) as countries
FROM minio_customers_simulation;

-- Comparaison rapide
SELECT 
    'PostgreSQL' as source,
    COUNT(*) as customer_count
FROM customers
UNION ALL
SELECT 
    'MinIO (simulated)' as source,
    COUNT(*) as customer_count
FROM minio_customers_simulation;
