-- Script d'insertion de données de démonstration pour Phase 3
-- PostgreSQL customers

-- Nettoyage
TRUNCATE TABLE customers CASCADE;

-- Insertion de 10 clients de test
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

-- Vérification
SELECT 
    COUNT(*) as total_inserted,
    MIN(created_at) as first_date,
    MAX(created_at) as last_date,
    COUNT(DISTINCT country) as countries
FROM customers;
