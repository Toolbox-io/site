#!/bin/bash

# Multi-branch deployment script for Toolbox.io with isolated environments
# Usage: ./deploy-multi.sh [main|dev|both] [--build] [--restart]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
DEPLOY_TARGET="both"
BUILD=false
RESTART=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        main|dev|both)
            DEPLOY_TARGET="$1"
            shift
            ;;
        --build)
            BUILD=true
            shift
            ;;
        --restart)
            RESTART=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [main|dev|both] [--build] [--restart]"
            echo ""
            echo "Options:"
            echo "  main|dev|both    Deploy target (default: both)"
            echo "  --build          Force rebuild of containers"
            echo "  --restart        Restart containers after deployment"
            echo "  -h, --help       Show this help message"
            echo ""
            echo "This script manages isolated environments:"
            echo "  Main: toolbox-io.ru (port 8000), download.toolbox-io.ru (port 8001)"
            echo "  Dev:  beta.toolbox-io.ru (port 8002), download-beta.toolbox-io.ru (port 8003)"
            exit 0
            ;;
        *)
            echo -e "${RED}Error: Unknown option $1${NC}"
            exit 1
            ;;
    esac
done

echo -e "${BLUE}=== Toolbox.io Multi-Branch Deployment (Isolated) ===${NC}"
echo -e "${YELLOW}Target: $DEPLOY_TARGET${NC}"
echo -e "${YELLOW}Build: $BUILD${NC}"
echo -e "${YELLOW}Restart: $RESTART${NC}"
echo ""

# Function to deploy main branch
deploy_main() {
    echo -e "${GREEN}Deploying main branch (isolated)...${NC}"
    
    if [ "$BUILD" = true ]; then
        echo -e "${YELLOW}Building main containers...${NC}"
        docker compose -f docker-compose.main.yml build
    fi
    
    if [ "$RESTART" = true ]; then
        echo -e "${YELLOW}Restarting main services...${NC}"
        docker compose -f docker-compose.main.yml restart
    else
        echo -e "${YELLOW}Starting main services...${NC}"
        docker compose -f docker-compose.main.yml up -d
    fi
    
    echo -e "${GREEN}Main branch deployed successfully!${NC}"
    echo -e "${BLUE}Main site: https://toolbox-io.ru${NC}"
    echo -e "${BLUE}Main download: https://download.toolbox-io.ru${NC}"
}

# Function to deploy dev branch
deploy_dev() {
    echo -e "${GREEN}Deploying dev branch (isolated)...${NC}"
    
    if [ "$BUILD" = true ]; then
        echo -e "${YELLOW}Building dev containers...${NC}"
        docker compose -f docker-compose.dev.yml build
    fi
    
    if [ "$RESTART" = true ]; then
        echo -e "${YELLOW}Restarting dev services...${NC}"
        docker compose -f docker-compose.dev.yml restart
    else
        echo -e "${YELLOW}Starting dev services...${NC}"
        docker compose -f docker-compose.dev.yml up -d
    fi
    
    echo -e "${GREEN}Dev branch deployed successfully!${NC}"
    echo -e "${BLUE}Dev site: https://beta.toolbox-io.ru${NC}"
    echo -e "${BLUE}Dev download: https://download-beta.toolbox-io.ru${NC}"
}

# Function to check if services are running
check_services() {
    echo -e "${BLUE}Checking service status...${NC}"
    
    # Check main services
    if docker compose -f docker-compose.main.yml ps | grep -q "Up"; then
        echo -e "${GREEN}✓ Main services are running${NC}"
    else
        echo -e "${RED}✗ Main services are not running${NC}"
    fi
    
    # Check dev services
    if docker compose -f docker-compose.dev.yml ps | grep -q "Up"; then
        echo -e "${GREEN}✓ Dev services are running${NC}"
    else
        echo -e "${RED}✗ Dev services are not running${NC}"
    fi
}

# Function to show logs
show_logs() {
    echo -e "${BLUE}Recent logs:${NC}"
    echo -e "${YELLOW}Main services logs:${NC}"
    docker compose -f docker-compose.main.yml logs --tail=10
    echo ""
    echo -e "${YELLOW}Dev services logs:${NC}"
    docker compose -f docker-compose.dev.yml logs --tail=10
}

# Function to stop services
stop_services() {
    echo -e "${YELLOW}Stopping services...${NC}"
    docker compose -f docker-compose.main.yml down
    docker compose -f docker-compose.dev.yml down
    echo -e "${GREEN}All services stopped${NC}"
}

# Function to show status
show_status() {
    echo -e "${BLUE}=== Service Status ===${NC}"
    echo -e "${YELLOW}Main services:${NC}"
    docker compose -f docker-compose.main.yml ps
    echo ""
    echo -e "${YELLOW}Dev services:${NC}"
    docker compose -f docker-compose.dev.yml ps
}

# Main deployment logic
case $DEPLOY_TARGET in
    main)
        deploy_main
        ;;
    dev)
        deploy_dev
        ;;
    both)
        deploy_main
        echo ""
        deploy_dev
        ;;
    stop)
        stop_services
        exit 0
        ;;
    status)
        show_status
        exit 0
        ;;
    *)
        echo -e "${RED}Error: Invalid deployment target '$DEPLOY_TARGET'${NC}"
        echo -e "${YELLOW}Valid options: main, dev, both, stop, status${NC}"
        exit 1
        ;;
esac

echo ""
check_services

if [ "$RESTART" = true ]; then
    echo ""
    show_logs
fi

echo ""
echo -e "${GREEN}Deployment completed!${NC}"
echo -e "${BLUE}Main: https://toolbox-io.ru${NC}"
echo -e "${BLUE}Main download: https://download.toolbox-io.ru${NC}"
echo -e "${BLUE}Dev:  https://beta.toolbox-io.ru${NC}"
echo -e "${BLUE}Dev download:  https://download-beta.toolbox-io.ru${NC}" 