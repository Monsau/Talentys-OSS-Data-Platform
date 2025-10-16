#!/bin/bash
# ============================================================================
# 🚀 Dremio + dbt Platform - Quick Deploy Script (Linux/Mac)
# ============================================================================
# One-command deployment for Unix-like systems

set -e  # Exit on error

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# ============================================================================
# FUNCTIONS
# ============================================================================

print_header() {
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║        🚀 Dremio + dbt Platform - Quick Deploy               ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_step() {
    local step=$1
    local total=$2
    local message=$3
    echo ""
    echo -e "${BLUE}[$step/$total] $message${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

check_command() {
    local cmd=$1
    local name=$2
    if command -v "$cmd" &> /dev/null; then
        print_success "$name found: $(command -v $cmd)"
        return 0
    else
        print_error "$name not found"
        return 1
    fi
}

# ============================================================================
# MAIN DEPLOYMENT
# ============================================================================

main() {
    print_header
    
    print_info "This script will deploy:"
    echo "  • Dremio 26 OSS"
    echo "  • PostgreSQL 15"
    echo "  • Elasticsearch 7.17"
    echo "  • MinIO"
    echo "  • dbt with 12 models"
    echo "  • 80K+ test records"
    echo ""
    
    read -p "Press ENTER to continue or Ctrl+C to cancel..."
    
    # ========================================================================
    # Step 1: Check Prerequisites
    # ========================================================================
    print_step 1 8 "Checking Prerequisites"
    
    all_ok=true
    check_command docker "Docker" || all_ok=false
    check_command docker-compose "Docker Compose" || all_ok=false
    check_command python3 "Python 3" || all_ok=false
    
    if [ "$all_ok" = false ]; then
        print_error "Missing prerequisites! Please install required tools."
        exit 1
    fi
    
    # ========================================================================
    # Step 2: Start Docker Services
    # ========================================================================
    print_step 2 8 "Starting Docker Services"
    
    print_info "Starting containers..."
    docker-compose up -d
    
    print_success "Docker services started!"
    print_info "Waiting for services to be ready (30s)..."
    sleep 30
    
    # ========================================================================
    # Step 3: Create Python Virtual Environment
    # ========================================================================
    print_step 3 8 "Setting Up Python Environment"
    
    if [ -d "venv" ]; then
        print_info "Virtual environment already exists"
    else
        print_info "Creating virtual environment..."
        python3 -m venv venv
        print_success "Virtual environment created!"
    fi
    
    print_info "Installing Python packages..."
    source venv/bin/activate
    pip install --upgrade pip -q
    pip install -r requirements.txt -q
    print_success "Python packages installed!"
    
    # ========================================================================
    # Step 4: Generate Test Data
    # ========================================================================
    print_step 4 8 "Generating Test Data"
    
    print_info "Generating 80K+ records..."
    python3 scripts/generate_all_data.py
    print_success "Data generated!"
    
    # ========================================================================
    # Step 5: Wait for Services
    # ========================================================================
    print_step 5 8 "Waiting for Services to be Ready"
    
    print_info "Waiting for Dremio (may take 2-3 minutes on first start)..."
    timeout=120
    elapsed=0
    while [ $elapsed -lt $timeout ]; do
        if curl -s http://localhost:9047 > /dev/null 2>&1; then
            print_success "Dremio is ready!"
            break
        fi
        sleep 5
        elapsed=$((elapsed + 5))
        echo -n "."
    done
    
    if [ $elapsed -ge $timeout ]; then
        print_error "Dremio not ready after ${timeout}s"
        exit 1
    fi
    
    # ========================================================================
    # Step 6: Setup dbt
    # ========================================================================
    print_step 6 8 "Setting Up dbt"
    
    cd dbt
    print_info "Testing dbt connection..."
    dbt debug || print_warning "dbt debug had issues (may be OK if sources not yet configured)"
    cd ..
    
    # ========================================================================
    # Step 7: Manual Configuration Reminder
    # ========================================================================
    print_step 7 8 "Configure Dremio Sources"
    
    print_warning "MANUAL STEP REQUIRED:"
    echo ""
    echo "1. Open Dremio UI: http://localhost:9047"
    echo "2. Login: dremio / dremio123"
    echo "3. Add sources:"
    echo "   • PostgreSQL: Host=postgres, Port=5432, DB=business_db, User=postgres, Password=postgres123"
    echo "   • Elasticsearch: Host=elasticsearch, Port=9200"
    echo "   • MinIO: Endpoint=minio:9000, Access=minioadmin, Secret=minioadmin123, Bucket=sales_data"
    echo ""
    
    read -p "Press ENTER when sources are configured..."
    
    # ========================================================================
    # Step 8: Run dbt
    # ========================================================================
    print_step 8 8 "Running dbt Models"
    
    cd dbt
    print_info "Running dbt models..."
    dbt run
    
    print_info "Running dbt tests..."
    dbt test || print_warning "Some tests may have failed (check output above)"
    
    cd ..
    
    # ========================================================================
    # Success!
    # ========================================================================
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║               🎉 DEPLOYMENT SUCCESSFUL! 🎉                    ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${YELLOW}📊 Access your platform:${NC}"
    echo "  • Dremio UI:        http://localhost:9047"
    echo "  • MinIO Console:    http://localhost:9001"
    echo "  • Elasticsearch:    http://localhost:9200"
    echo "  • PostgreSQL:       localhost:5432"
    echo ""
    echo -e "${YELLOW}🔐 Credentials:${NC}"
    echo "  • Dremio:     dremio / dremio123"
    echo "  • MinIO:      minioadmin / minioadmin123"
    echo "  • PostgreSQL: postgres / postgres123"
    echo ""
    echo -e "${YELLOW}📁 Next steps:${NC}"
    echo "  1. Check service status:    make status"
    echo "  2. View dbt documentation:  make dbt-docs"
    echo "  3. Run example queries in Dremio UI"
    echo "  4. Explore data in \$scratch.marts"
    echo ""
    echo -e "${YELLOW}📚 Documentation:${NC}"
    echo "  • Quick Start: QUICKSTART.md"
    echo "  • Full Report: DBT_COMPLETION_REPORT.md"
    echo "  • All commands: make help"
    echo ""
}

# Run main
main

