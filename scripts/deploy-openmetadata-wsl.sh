#!/bin/bash
################################################################################
# OpenMetadata Deployment Script for WSL
# Version: 1.10.1 (Latest)
# Author: Talentys Data Team
# Date: 2025-10-19
################################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
OPENMETADATA_VERSION="1.10.1"
PROJECT_ROOT="/mnt/c/projets/dremiodbt"
COMPOSE_FILE="$PROJECT_ROOT/docker-compose-openmetadata-official.yml"
LOG_DIR="$PROJECT_ROOT/logs"
LOG_FILE="$LOG_DIR/openmetadata-deployment-$(date +%Y%m%d-%H%M%S).log"

# Create log directory
mkdir -p "$LOG_DIR"

# Logging function
log() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case $level in
        INFO)
            echo -e "${CYAN}[$timestamp] [INFO]${NC} $message" | tee -a "$LOG_FILE"
            ;;
        SUCCESS)
            echo -e "${GREEN}[$timestamp] [SUCCESS]${NC} $message" | tee -a "$LOG_FILE"
            ;;
        WARNING)
            echo -e "${YELLOW}[$timestamp] [WARNING]${NC} $message" | tee -a "$LOG_FILE"
            ;;
        ERROR)
            echo -e "${RED}[$timestamp] [ERROR]${NC} $message" | tee -a "$LOG_FILE"
            ;;
        *)
            echo "[$timestamp] $message" | tee -a "$LOG_FILE"
            ;;
    esac
}

# Banner
echo -e "${GREEN}"
echo "========================================"
echo "  OpenMetadata Deployment Script v1.10.1"
echo "  Platform: WSL Ubuntu"
echo "========================================"
echo -e "${NC}"

log INFO "Starting OpenMetadata deployment..."
log INFO "Version: $OPENMETADATA_VERSION"
log INFO "Compose file: $COMPOSE_FILE"

# Check Docker
log INFO "Checking Docker..."
if ! command -v docker &> /dev/null; then
    log ERROR "Docker is not installed or not in PATH"
    exit 1
fi

DOCKER_VERSION=$(docker --version)
log SUCCESS "Docker found: $DOCKER_VERSION"

# Check Docker Compose
log INFO "Checking Docker Compose..."
if ! docker compose version &> /dev/null; then
    log ERROR "Docker Compose is not available"
    exit 1
fi

COMPOSE_VERSION=$(docker compose version)
log SUCCESS "Docker Compose found: $COMPOSE_VERSION"

# Check if compose file exists
if [ ! -f "$COMPOSE_FILE" ]; then
    log ERROR "Compose file not found: $COMPOSE_FILE"
    exit 1
fi
log SUCCESS "Compose file found"

# Stop existing OpenMetadata containers
log INFO "Stopping existing OpenMetadata containers..."
docker stop openmetadata_server openmetadata_ingestion openmetadata_mysql openmetadata_elasticsearch 2>/dev/null || true
docker rm openmetadata_server openmetadata_ingestion openmetadata_mysql openmetadata_elasticsearch execute_migrate_all 2>/dev/null || true
log SUCCESS "Old containers removed"

# Pull latest images
log INFO "Pulling OpenMetadata images (version $OPENMETADATA_VERSION)..."
cd "$PROJECT_ROOT"
docker compose -f "$COMPOSE_FILE" pull

if [ $? -ne 0 ]; then
    log ERROR "Failed to pull Docker images"
    exit 1
fi
log SUCCESS "Images pulled successfully"

# Start services
log INFO "Starting OpenMetadata services..."
docker compose -f "$COMPOSE_FILE" up -d

if [ $? -ne 0 ]; then
    log ERROR "Failed to start services"
    exit 1
fi
log SUCCESS "Services started"

# Wait for services to initialize
log INFO "Waiting for services to initialize (180 seconds)..."
sleep 180

# Check container status
log INFO "Checking container status..."
echo ""
docker compose -f "$COMPOSE_FILE" ps
echo ""

# Wait for OpenMetadata server to be ready
log INFO "Waiting for OpenMetadata server to be ready..."
MAX_ATTEMPTS=30
ATTEMPT=0

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    if curl -sf http://localhost:8585/api/v1/health > /dev/null 2>&1; then
        log SUCCESS "OpenMetadata server is ready!"
        break
    fi
    
    ATTEMPT=$((ATTEMPT + 1))
    echo -n "."
    sleep 10
done

echo ""

if [ $ATTEMPT -eq $MAX_ATTEMPTS ]; then
    log WARNING "Server did not respond within expected time, but may still be initializing"
    log INFO "You can check status later at: http://localhost:8585"
else
    # Test API
    log INFO "Testing OpenMetadata API..."
    HEALTH_RESPONSE=$(curl -s http://localhost:8585/api/v1/health)
    log SUCCESS "API Health Check: OK"
    echo "$HEALTH_RESPONSE" | jq . 2>/dev/null || echo "$HEALTH_RESPONSE"
fi

# Display summary
echo ""
echo -e "${GREEN}========================================"
echo "  DEPLOYMENT COMPLETED!"
echo "========================================${NC}"
echo ""
echo -e "${CYAN}Services Running:${NC}"
echo "  ✓ MySQL:          localhost:3308"
echo "  ✓ Elasticsearch:  localhost:9200"
echo "  ✓ OpenMetadata:   localhost:8585"
echo "  ✓ Ingestion:      localhost:8080"
echo ""
echo -e "${YELLOW}Access Information:${NC}"
echo "  UI:       http://localhost:8585"
echo "  Login:    admin / admin"
echo "  API:      http://localhost:8585/api"
echo "  Swagger:  http://localhost:8585/swagger-ui"
echo ""
echo -e "${CYAN}Next Steps:${NC}"
echo "  1. Open http://localhost:8585 in your browser"
echo "  2. Login with admin / admin"
echo "  3. Change the default password"
echo "  4. Configure Dremio connector"
echo "  5. Start metadata ingestion"
echo ""
echo -e "${BLUE}Log file: $LOG_FILE${NC}"
echo ""

log SUCCESS "Deployment script completed"

# Open browser (if running in WSL with Windows)
if command -v wslview &> /dev/null; then
    log INFO "Opening browser..."
    wslview http://localhost:8585 &
elif command -v explorer.exe &> /dev/null; then
    log INFO "Opening browser..."
    explorer.exe "http://localhost:8585" &
fi

exit 0
