#!/bin/bash
# Quick test runner script for Docker-based integration tests

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting Cribl Ansible Docker Integration Tests${NC}"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker and try again.${NC}"
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ docker-compose is not installed. Please install it and try again.${NC}"
    exit 1
fi

# Check if env/test.env exists
if [ ! -f "../../env/test.env" ]; then
    echo -e "${RED}❌ env/test.env not found. Please create it with Cribl credentials.${NC}"
    exit 1
fi

echo -e "${YELLOW}📋 Test Configuration:${NC}"
source ../../env/test.env
echo "  Cribl URL: ${cribl_url}"
echo "  Username: ${cribl_username}"
echo ""

# Change to script directory
cd "$(dirname "$0")"

# Run tests
echo -e "${GREEN}🐳 Building Docker container...${NC}"
docker-compose build

echo ""
echo -e "${GREEN}🧪 Running integration tests...${NC}"
echo ""

# Run pytest with docker marker
pytest test_docker_integration.py -v -m docker

# Capture exit code
EXIT_CODE=$?

# Cleanup
echo ""
echo -e "${YELLOW}🧹 Cleaning up...${NC}"
docker-compose down -v

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ All tests passed!${NC}"
else
    echo ""
    echo -e "${RED}❌ Some tests failed. Check the output above for details.${NC}"
fi

exit $EXIT_CODE

