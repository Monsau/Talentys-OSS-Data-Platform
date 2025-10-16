#!/bin/bash

echo "=========================================="
echo "Running Dremio to OpenMetadata Ingestion"
echo "=========================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Change to project root
cd "$(dirname "$0")/.."

# Run dbt
echo -e "${YELLOW}Running dbt models...${NC}"
cd dbt
dbt deps
dbt debug
dbt run
dbt test
dbt docs generate
cd ..
echo -e "${GREEN}dbt models executed successfully${NC}"

# Run Dremio ingestion
echo -e "${YELLOW}Running Dremio ingestion to OpenMetadata...${NC}"
metadata ingest -c openmetadata/ingestion/dremio-ingestion.yaml

if [ $? -eq 0 ]; then
    echo -e "${GREEN}Dremio ingestion completed successfully${NC}"
else
    echo -e "${RED}Dremio ingestion failed${NC}"
    exit 1
fi

# Run dbt ingestion
echo -e "${YELLOW}Running dbt ingestion to OpenMetadata...${NC}"
metadata ingest -c openmetadata/ingestion/dbt-ingestion.yaml

if [ $? -eq 0 ]; then
    echo -e "${GREEN}dbt ingestion completed successfully${NC}"
else
    echo -e "${RED}dbt ingestion failed${NC}"
    exit 1
fi

echo -e "${GREEN}=========================================="
echo "Ingestion complete!"
echo "==========================================${NC}"
echo ""
echo "Check OpenMetadata at http://localhost:8585"
echo "to view your ingested data and lineage"
