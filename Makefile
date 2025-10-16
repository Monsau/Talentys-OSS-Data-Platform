# ============================================================================
# 🚀 Dremio + dbt Platform - Makefile
# ============================================================================
# Simplified commands for platform management

.PHONY: help deploy start stop restart clean data dbt-run dbt-test dbt-docs status logs

# Default target
.DEFAULT_GOAL := help

# ============================================================================
# COLORS
# ============================================================================
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m

# ============================================================================
# CONFIGURATION
# ============================================================================
PYTHON := python3
VENV := venv
VENV_BIN := $(VENV)/bin
DBT_DIR := dbt

# ============================================================================
# HELP
# ============================================================================

help: ## Show this help message
	@echo "$(BLUE)╔════════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(BLUE)║        🚀 Dremio + dbt Platform - Available Commands          ║$(NC)"
	@echo "$(BLUE)╚════════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(YELLOW)Quick Start:$(NC)"
	@echo "  1. make deploy    - Deploy entire platform"
	@echo "  2. make status    - Check service status"
	@echo "  3. make dbt-run   - Run dbt models"
	@echo ""

# ============================================================================
# FULL DEPLOYMENT
# ============================================================================

deploy: ## 🚀 Deploy complete platform (one command)
	@echo "$(BLUE)Starting full platform deployment...$(NC)"
	$(PYTHON) deploy_platform.py

deploy-quick: ## ⚡ Quick deploy (skip if already running)
	@echo "$(BLUE)Quick deployment (skipping existing steps)...$(NC)"
	@export SKIP_DOCKER_START=true SKIP_VENV_CREATION=true && $(PYTHON) deploy_platform.py

# ============================================================================
# DOCKER SERVICES
# ============================================================================

start: ## ▶️  Start all Docker services
	@echo "$(BLUE)Starting Docker services...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)✅ Services started!$(NC)"
	@echo "$(YELLOW)Waiting for services to be ready (30s)...$(NC)"
	@sleep 30
	@make status

stop: ## ⏹️  Stop all Docker services
	@echo "$(YELLOW)Stopping Docker services...$(NC)"
	docker-compose stop
	@echo "$(GREEN)✅ Services stopped$(NC)"

restart: ## 🔄 Restart all Docker services
	@echo "$(YELLOW)Restarting Docker services...$(NC)"
	docker-compose restart
	@echo "$(GREEN)✅ Services restarted$(NC)"
	@sleep 10
	@make status

down: ## ⏬ Stop and remove containers (keep data)
	@echo "$(YELLOW)Stopping and removing containers...$(NC)"
	docker-compose down
	@echo "$(GREEN)✅ Containers removed$(NC)"

clean: ## 🧹 Remove everything (⚠️  including data)
	@echo "$(RED)⚠️  WARNING: This will delete ALL data!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose down -v; \
		rm -rf generated_data/; \
		rm -rf $(DBT_DIR)/target/ $(DBT_DIR)/logs/ $(DBT_DIR)/dbt_packages/; \
		echo "$(GREEN)✅ Cleanup complete$(NC)"; \
	else \
		echo "$(YELLOW)Cancelled$(NC)"; \
	fi

# ============================================================================
# PYTHON ENVIRONMENT
# ============================================================================

venv: ## 🐍 Create Python virtual environment
	@echo "$(BLUE)Creating virtual environment...$(NC)"
	$(PYTHON) -m venv $(VENV)
	$(VENV_BIN)/pip install --upgrade pip
	$(VENV_BIN)/pip install -r requirements.txt
	@echo "$(GREEN)✅ Virtual environment ready!$(NC)"
	@echo "$(YELLOW)Activate with: source $(VENV_BIN)/activate$(NC)"

venv-clean: ## 🗑️  Remove virtual environment
	@echo "$(YELLOW)Removing virtual environment...$(NC)"
	rm -rf $(VENV)
	@echo "$(GREEN)✅ Virtual environment removed$(NC)"

# ============================================================================
# DATA GENERATION
# ============================================================================

data: ## 🎲 Generate all test data
	@echo "$(BLUE)Generating test data...$(NC)"
	$(VENV_BIN)/python scripts/generate_all_data.py
	@echo "$(GREEN)✅ Data generated!$(NC)"

data-load: ## 📥 Load data to all sources
	@echo "$(BLUE)Loading data to sources...$(NC)"
	@echo "$(YELLOW)TODO: Implement data loading scripts$(NC)"
	# $(VENV_BIN)/python scripts/load_postgres_data.py
	# $(VENV_BIN)/python scripts/load_elasticsearch_data.py
	# $(VENV_BIN)/python scripts/load_minio_data.py

# ============================================================================
# DBT
# ============================================================================

dbt-debug: ## 🔍 Test dbt connection
	@echo "$(BLUE)Testing dbt connection...$(NC)"
	cd $(DBT_DIR) && $(VENV_BIN)/dbt debug

dbt-deps: ## 📦 Install dbt dependencies
	@echo "$(BLUE)Installing dbt packages...$(NC)"
	cd $(DBT_DIR) && $(VENV_BIN)/dbt deps

dbt-run: ## ▶️  Run all dbt models
	@echo "$(BLUE)Running dbt models...$(NC)"
	cd $(DBT_DIR) && $(VENV_BIN)/dbt run
	@echo "$(GREEN)✅ dbt models built!$(NC)"

dbt-run-full: ## 🔄 Full refresh all dbt models
	@echo "$(BLUE)Running dbt models (full refresh)...$(NC)"
	cd $(DBT_DIR) && $(VENV_BIN)/dbt run --full-refresh
	@echo "$(GREEN)✅ dbt models rebuilt!$(NC)"

dbt-test: ## ✅ Run all dbt tests
	@echo "$(BLUE)Running dbt tests...$(NC)"
	cd $(DBT_DIR) && $(VENV_BIN)/dbt test

dbt-docs: ## 📚 Generate and serve dbt docs
	@echo "$(BLUE)Generating dbt documentation...$(NC)"
	cd $(DBT_DIR) && $(VENV_BIN)/dbt docs generate
	@echo "$(GREEN)✅ Documentation generated!$(NC)"
	@echo "$(YELLOW)Serving on http://localhost:8080$(NC)"
	cd $(DBT_DIR) && $(VENV_BIN)/dbt docs serve --port 8080

dbt-clean: ## 🧹 Clean dbt artifacts
	@echo "$(YELLOW)Cleaning dbt artifacts...$(NC)"
	cd $(DBT_DIR) && rm -rf target/ logs/ dbt_packages/
	@echo "$(GREEN)✅ dbt artifacts cleaned$(NC)"

# ============================================================================
# DREMIO MANAGEMENT
# ============================================================================

dremio-drop-tables: ## 🗑️  Drop all dbt tables in Dremio
	@echo "$(YELLOW)Dropping dbt tables in Dremio...$(NC)"
	$(VENV_BIN)/python scripts/drop_tables_sql.py
	@echo "$(GREEN)✅ Tables dropped$(NC)"

# ============================================================================
# STATUS & MONITORING
# ============================================================================

status: ## 📊 Check platform status
	@echo "$(BLUE)╔════════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(BLUE)║                    Platform Status                            ║$(NC)"
	@echo "$(BLUE)╚════════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(YELLOW)Docker Services:$(NC)"
	@docker-compose ps
	@echo ""
	@echo "$(YELLOW)Service URLs:$(NC)"
	@echo "  • Dremio:        http://localhost:9047"
	@echo "  • MinIO Console: http://localhost:9001"
	@echo "  • Elasticsearch: http://localhost:9200"
	@echo "  • PostgreSQL:    localhost:5432"
	@echo ""

logs: ## 📋 Show Docker logs (all services)
	docker-compose logs -f --tail=100

logs-dremio: ## 📋 Show Dremio logs
	docker-compose logs -f --tail=100 dremio

logs-postgres: ## 📋 Show PostgreSQL logs
	docker-compose logs -f --tail=100 postgres

logs-elasticsearch: ## 📋 Show Elasticsearch logs
	docker-compose logs -f --tail=100 elasticsearch

logs-minio: ## 📋 Show MinIO logs
	docker-compose logs -f --tail=100 minio

# ============================================================================
# TESTING
# ============================================================================

test: ## 🧪 Run all tests
	@echo "$(BLUE)Running platform tests...$(NC)"
	@make dbt-test

test-integration: ## 🔗 Run integration tests
	@echo "$(BLUE)Running integration tests...$(NC)"
	$(VENV_BIN)/python tests/test_integration_e2e.py

# ============================================================================
# DATABASE ACCESS
# ============================================================================

psql: ## 🐘 Connect to PostgreSQL
	@echo "$(BLUE)Connecting to PostgreSQL...$(NC)"
	@echo "$(YELLOW)Password: postgres123$(NC)"
	psql -h localhost -p 5432 -U postgres -d business_db

psql-count: ## 📊 Show PostgreSQL record counts
	@echo "$(BLUE)PostgreSQL record counts:$(NC)"
	@psql -h localhost -p 5432 -U postgres -d business_db -c "SELECT 'customers' as table, COUNT(*) FROM customers UNION ALL SELECT 'orders', COUNT(*) FROM orders;"

# ============================================================================
# UTILITIES
# ============================================================================

check: ## ✅ Check prerequisites
	@echo "$(BLUE)Checking prerequisites...$(NC)"
	@echo -n "Docker:        "; docker --version || echo "$(RED)❌ Not found$(NC)"
	@echo -n "Docker Compose:"; docker-compose --version || echo "$(RED)❌ Not found$(NC)"
	@echo -n "Python:        "; $(PYTHON) --version || echo "$(RED)❌ Not found$(NC)"
	@echo -n "psql:          "; psql --version || echo "$(RED)❌ Not found$(NC)"

urls: ## 🌐 Show all service URLs
	@echo "$(BLUE)Service URLs:$(NC)"
	@echo "  $(GREEN)Dremio UI:$(NC)        http://localhost:9047"
	@echo "  $(GREEN)MinIO Console:$(NC)    http://localhost:9001"
	@echo "  $(GREEN)Elasticsearch:$(NC)    http://localhost:9200"
	@echo "  $(GREEN)PostgreSQL:$(NC)       localhost:5432"
	@echo ""
	@echo "$(BLUE)Credentials:$(NC)"
	@echo "  $(YELLOW)Dremio:$(NC)      dremio / dremio123"
	@echo "  $(YELLOW)MinIO:$(NC)       minioadmin / minioadmin123"
	@echo "  $(YELLOW)PostgreSQL:$(NC)  postgres / postgres123"

open: ## 🌐 Open Dremio UI in browser
	@echo "$(BLUE)Opening Dremio UI...$(NC)"
	@python -m webbrowser http://localhost:9047 || xdg-open http://localhost:9047 || open http://localhost:9047

# ============================================================================
# DEVELOPMENT
# ============================================================================

shell: ## 🐚 Enter Python virtual environment shell
	@echo "$(BLUE)Activating virtual environment...$(NC)"
	@echo "$(YELLOW)Run: source $(VENV_BIN)/activate$(NC)"
	@$(SHELL)

format: ## 🎨 Format Python code
	@echo "$(BLUE)Formatting Python code...$(NC)"
	$(VENV_BIN)/black .
	$(VENV_BIN)/isort .

lint: ## 🔍 Lint Python code
	@echo "$(BLUE)Linting Python code...$(NC)"
	$(VENV_BIN)/flake8 .
	$(VENV_BIN)/pylint dremio_connector/

# ============================================================================
# EXAMPLES
# ============================================================================

example-queries: ## 📊 Show example SQL queries
	@echo "$(BLUE)Example Queries:$(NC)"
	@echo ""
	@echo "$(YELLOW)1. Business Overview (last 7 days):$(NC)"
	@echo 'SELECT business_date, combined_revenue, platform_errors FROM "$$scratch".marts.fct_business_overview WHERE business_date >= CURRENT_DATE - 7 ORDER BY business_date DESC;'
	@echo ""
	@echo "$(YELLOW)2. Top 10 Customers by Revenue:$(NC)"
	@echo 'SELECT c.customer_name, SUM(o.amount) as total FROM "$$scratch".marts.dim_customers c JOIN "$$scratch".marts.fct_orders o ON c.customer_id = o.customer_id GROUP BY c.customer_name ORDER BY total DESC LIMIT 10;'
	@echo ""
	@echo "$(BLUE)Run these in Dremio UI: http://localhost:9047$(NC)"
