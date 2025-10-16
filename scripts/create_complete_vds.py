#!/usr/bin/env python3
"""
Script pour créer des VDS (Virtual Dataset) dans Dremio avec données PostgreSQL réelles
"""
import requests
import json
import sys
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DREMIO_URL = "http://localhost:9047"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

def login():
    """Connexion à Dremio"""
    payload = {
        "userName": ADMIN_USERNAME,
        "password": ADMIN_PASSWORD
    }
    
    response = requests.post(
        f"{DREMIO_URL}/apiv2/login",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        return response.json()["token"]
    else:
        raise Exception(f"Échec de connexion: {response.status_code}")

def create_space(token, space_name, description=""):
    """Créer un espace Dremio"""
    payload = {
        "entityType": "space",
        "name": space_name,
        "description": description
    }
    
    response = requests.post(
        f"{DREMIO_URL}/api/v3/catalog",
        json=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"_dremio{token}"
        }
    )
    
    if response.status_code in [200, 201]:
        logger.info(f"✓ Espace créé: {space_name}")
        return True
    elif response.status_code == 409:
        logger.info(f"✓ Espace existe déjà: {space_name}")
        return True
    else:
        logger.error(f"Erreur création espace {space_name}: {response.status_code} - {response.text[:200]}")
        return False

def create_vds(token, space, dataset_name, sql, description=""):
    """Créer un Virtual Dataset"""
    payload = {
        "entityType": "dataset",
        "type": "VIRTUAL_DATASET", 
        "path": [space, dataset_name],
        "sql": sql,
        "sqlContext": [space],
        "description": description
    }
    
    response = requests.post(
        f"{DREMIO_URL}/api/v3/catalog",
        json=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"_dremio{token}"
        }
    )
    
    if response.status_code in [200, 201]:
        logger.info(f"✓ VDS créé: {space}.{dataset_name}")
        return True
    elif response.status_code == 409:
        logger.info(f"✓ VDS existe déjà: {space}.{dataset_name}")
        return True
    else:
        logger.error(f"Erreur création VDS {space}.{dataset_name}: {response.status_code}")
        logger.error(f"Message: {response.text[:300]}")
        return False

def main():
    logger.info("🚀 CREATION DES VDS AVEC DONNEES POSTGRESQL REELLES")
    
    try:
        # Connexion
        logger.info("🔐 Authentification...")
        token = login()
        logger.info("✓ Authentification réussie")
        
        # Créer les espaces nécessaires
        logger.info("\n=== CREATION DES ESPACES ===")
        spaces_to_create = [
            ("raw", "Données brutes sources"),
            ("staging", "Données intermédiaires transformées"),
            ("analytics", "Analyses et métriques métier"),
            ("marts", "Data marts pour tableaux de bord")
        ]
        
        for space_name, description in spaces_to_create:
            create_space(token, space_name, description)
        
        # Créer les VDS raw (données sources PostgreSQL)
        logger.info("\n=== CREATION DES VDS RAW (SOURCES) ===")
        
        # VDS Raw Customers
        sql_raw_customers = """
        SELECT 
            id as customer_id,
            first_name,
            last_name,
            first_name || ' ' || last_name as full_name,
            email,
            phone,
            address,
            city,
            country,
            created_at
        FROM PostgreSQL_BusinessDB.public.customers
        """
        create_vds(token, "raw", "customers", sql_raw_customers, "Clients depuis PostgreSQL")
        
        # VDS Raw Orders
        sql_raw_orders = """
        SELECT 
            id as order_id,
            customer_id,
            order_date,
            status,
            total_amount
        FROM PostgreSQL_BusinessDB.public.orders
        """
        create_vds(token, "raw", "orders", sql_raw_orders, "Commandes depuis PostgreSQL")
        
        # VDS Raw Products
        sql_raw_products = """
        SELECT 
            id as product_id,
            name as product_name,
            description,
            price,
            category,
            sku,
            created_at
        FROM PostgreSQL_BusinessDB.public.products
        """
        create_vds(token, "raw", "products", sql_raw_products, "Produits depuis PostgreSQL")
        
        # VDS Raw Order Items
        sql_raw_order_items = """
        SELECT 
            id as item_id,
            order_id,
            product_id,
            quantity,
            unit_price,
            quantity * unit_price as line_total
        FROM PostgreSQL_BusinessDB.public.order_items
        """
        create_vds(token, "raw", "order_items", sql_raw_order_items, "Articles commandés depuis PostgreSQL")
        
        # Créer les VDS staging (données enrichies)
        logger.info("\n=== CREATION DES VDS STAGING (ENRICHIES) ===")
        
        # VDS Staging Orders Enriched
        sql_staging_orders_enriched = """
        SELECT 
            o.order_id,
            o.customer_id,
            c.full_name as customer_name,
            c.email as customer_email,
            c.city as customer_city,
            c.country as customer_country,
            o.order_date,
            o.status,
            o.total_amount,
            EXTRACT(YEAR FROM o.order_date) as order_year,
            EXTRACT(MONTH FROM o.order_date) as order_month,
            EXTRACT(DAY FROM o.order_date) as order_day,
            CASE 
                WHEN o.total_amount < 100 THEN 'Small'
                WHEN o.total_amount < 500 THEN 'Medium'
                ELSE 'Large'
            END as order_size_category
        FROM raw.orders o
        LEFT JOIN raw.customers c ON o.customer_id = c.customer_id
        """
        create_vds(token, "staging", "orders_enriched", sql_staging_orders_enriched, "Commandes enrichies avec infos client")
        
        # VDS Staging Sales Details
        sql_staging_sales_details = """
        SELECT 
            oi.item_id,
            oi.order_id,
            oi.product_id,
            p.product_name,
            p.category,
            p.sku,
            oi.quantity,
            oi.unit_price,
            oi.line_total,
            o.customer_id,
            c.full_name as customer_name,
            o.order_date,
            o.status as order_status
        FROM raw.order_items oi
        LEFT JOIN raw.products p ON oi.product_id = p.product_id
        LEFT JOIN raw.orders o ON oi.order_id = o.order_id
        LEFT JOIN raw.customers c ON o.customer_id = c.customer_id
        """
        create_vds(token, "staging", "sales_details", sql_staging_sales_details, "Détails des ventes avec toutes les dimensions")
        
        # Créer les VDS analytics (métriques métier)
        logger.info("\n=== CREATION DES VDS ANALYTICS (METRIQUES) ===")
        
        # VDS Analytics Sales by Category
        sql_analytics_sales_by_category = """
        SELECT 
            p.category,
            COUNT(DISTINCT oi.order_id) as total_orders,
            COUNT(DISTINCT o.customer_id) as unique_customers,
            SUM(oi.quantity) as total_quantity_sold,
            SUM(oi.line_total) as total_revenue,
            AVG(oi.line_total) as avg_line_value,
            AVG(oi.unit_price) as avg_unit_price
        FROM raw.order_items oi
        LEFT JOIN raw.products p ON oi.product_id = p.product_id
        LEFT JOIN raw.orders o ON oi.order_id = o.order_id
        WHERE o.status = 'completed'
        GROUP BY p.category
        ORDER BY total_revenue DESC
        """
        create_vds(token, "analytics", "sales_by_category", sql_analytics_sales_by_category, "Ventes par catégorie de produit")
        
        # VDS Analytics Customer Metrics
        sql_analytics_customer_metrics = """
        SELECT 
            c.customer_id,
            c.full_name,
            c.email,
            c.city,
            c.country,
            COUNT(DISTINCT o.order_id) as total_orders,
            SUM(CASE WHEN o.status = 'completed' THEN o.total_amount ELSE 0 END) as total_spent,
            AVG(CASE WHEN o.status = 'completed' THEN o.total_amount ELSE NULL END) as avg_order_value,
            MIN(o.order_date) as first_order_date,
            MAX(o.order_date) as last_order_date,
            CASE 
                WHEN SUM(CASE WHEN o.status = 'completed' THEN o.total_amount ELSE 0 END) > 1000 THEN 'VIP'
                WHEN SUM(CASE WHEN o.status = 'completed' THEN o.total_amount ELSE 0 END) > 500 THEN 'Premium'
                ELSE 'Standard'
            END as customer_segment
        FROM raw.customers c
        LEFT JOIN raw.orders o ON c.customer_id = o.customer_id
        GROUP BY c.customer_id, c.full_name, c.email, c.city, c.country
        ORDER BY total_spent DESC
        """
        create_vds(token, "analytics", "customer_metrics", sql_analytics_customer_metrics, "Métriques et segmentation clients")
        
        # VDS Analytics Product Performance
        sql_analytics_product_performance = """
        SELECT 
            p.product_id,
            p.product_name,
            p.category,
            p.sku,
            p.price as list_price,
            COUNT(DISTINCT oi.order_id) as orders_count,
            SUM(oi.quantity) as total_sold,
            SUM(oi.line_total) as revenue,
            AVG(oi.unit_price) as avg_selling_price,
            (SUM(oi.line_total) / NULLIF(SUM(oi.quantity), 0)) as revenue_per_unit,
            COUNT(DISTINCT o.customer_id) as unique_customers
        FROM raw.products p
        LEFT JOIN raw.order_items oi ON p.product_id = oi.product_id
        LEFT JOIN raw.orders o ON oi.order_id = o.order_id AND o.status = 'completed'
        GROUP BY p.product_id, p.product_name, p.category, p.sku, p.price
        ORDER BY revenue DESC NULLS LAST
        """
        create_vds(token, "analytics", "product_performance", sql_analytics_product_performance, "Performance et métriques produits")
        
        # Créer les VDS marts (tableaux de bord)
        logger.info("\n=== CREATION DES VDS MARTS (DASHBOARDS) ===")
        
        # VDS Marts Executive Summary
        sql_marts_executive_summary = """
        SELECT 
            'Executive Summary' as metric_group,
            COUNT(DISTINCT c.customer_id) as total_customers,
            COUNT(DISTINCT CASE WHEN o.status = 'completed' THEN o.order_id END) as completed_orders,
            SUM(CASE WHEN o.status = 'completed' THEN o.total_amount ELSE 0 END) as total_revenue,
            AVG(CASE WHEN o.status = 'completed' THEN o.total_amount END) as avg_order_value,
            COUNT(DISTINCT p.product_id) as total_products,
            COUNT(DISTINCT p.category) as total_categories
        FROM raw.customers c
        CROSS JOIN raw.orders o
        CROSS JOIN raw.products p
        """
        create_vds(token, "marts", "executive_summary", sql_marts_executive_summary, "Résumé exécutif pour tableaux de bord")
        
        logger.info("\n" + "="*60)
        logger.info("✅ CREATION DES VDS TERMINEE AVEC SUCCES!")
        logger.info("="*60)
        logger.info("\n📊 VDS créés par espace:")
        logger.info("   🔸 raw: customers, orders, products, order_items")
        logger.info("   🔸 staging: orders_enriched, sales_details") 
        logger.info("   🔸 analytics: sales_by_category, customer_metrics, product_performance")
        logger.info("   🔸 marts: executive_summary")
        logger.info("\n🌐 Interface Dremio: http://localhost:9047")
        logger.info("👤 Connexion: admin / admin123")
        logger.info("\n🎯 VDS prêts pour analyses et tableaux de bord!")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ ERREUR LORS DE LA CREATION DES VDS: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)