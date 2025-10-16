#!/bin/bash

echo "=========================================="
echo "Initializing Dremio + dbt + OpenMetadata"
echo "=========================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is running
echo -e "${YELLOW}Checking Docker...${NC}"
if ! docker info > /dev/null 2>&1; then
    echo "Docker is not running. Please start Docker and try again."
    exit 1
fi
echo -e "${GREEN}Docker is running${NC}"

# Start Docker services
echo -e "${YELLOW}Starting Docker services...${NC}"
cd docker
docker-compose up -d
cd ..
echo -e "${GREEN}Docker services started${NC}"

# Wait for services to be ready
echo -e "${YELLOW}Waiting for services to be ready...${NC}"
sleep 30

# Check Dremio
echo -e "${YELLOW}Checking Dremio...${NC}"
until curl -s http://localhost:9047 > /dev/null; do
    echo "Waiting for Dremio to be ready..."
    sleep 5
done
echo -e "${GREEN}Dremio is ready at http://localhost:9047${NC}"

# Check OpenMetadata
echo -e "${YELLOW}Checking OpenMetadata...${NC}"
until curl -s http://localhost:8585/api > /dev/null; do
    echo "Waiting for OpenMetadata to be ready..."
    sleep 5
done
echo -e "${GREEN}OpenMetadata is ready at http://localhost:8585${NC}"

# Install Python dependencies
echo -e "${YELLOW}Installing Python dependencies from requirements.txt...${NC}"
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo -e "${GREEN}Python dependencies installed${NC}"
else
    echo -e "${YELLOW}requirements.txt not found, installing manually...${NC}"
    pip install dbt-core dbt-dremio
    pip install "openmetadata-ingestion[postgres,dbt]"
    echo -e "${GREEN}Python dependencies installed${NC}"
fi

echo -e "${GREEN}=========================================="
echo "Initialization complete!"
echo "==========================================${NC}"
echo ""
echo "Next steps:"
echo "1. Access Dremio at http://localhost:9047"
echo "2. Access OpenMetadata at http://localhost:8585"
echo "3. Run 'dbt debug' to test dbt connection"
echo "4. Run './scripts/run-ingestion.sh' to start ingestion"
