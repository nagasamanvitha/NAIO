#!/bin/bash

echo "========================================"
echo "Naio n8n Setup Script"
echo "========================================"
echo ""

echo "[1/5] Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker is not installed!"
    echo "Please install Docker from https://www.docker.com/products/docker-desktop"
    exit 1
fi
echo "✓ Docker is installed!"
echo ""

echo "[2/5] Checking if n8n is already running..."
if docker ps | grep -q n8n; then
    echo "✓ n8n is already running!"
    echo ""
    echo "n8n URL: http://localhost:5678"
    echo ""
    read -p "Press Enter to continue to next step..."
else
    echo "[3/5] Starting n8n container..."
    echo "This will start n8n in the background."
    echo "n8n will be available at: http://localhost:5678"
    echo ""
    
    docker run -d --name n8n -p 5678:5678 -v n8n_data:/home/node/.n8n n8nio/n8n
    
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to start n8n!"
        echo "Make sure Docker Desktop is running."
        exit 1
    fi
    
    echo "✓ n8n started successfully!"
    echo "Waiting 5 seconds for n8n to initialize..."
    sleep 5
fi

echo ""
echo "[4/5] n8n Setup Instructions:"
echo ""
echo "1. Open your browser and go to: http://localhost:5678"
echo "2. Create an account (first time only)"
echo "3. Click 'Workflows' in the sidebar"
echo "4. Click 'Import from File' button"
echo "5. Import these files:"
echo "   - n8n/workflows/zendesk_workflow.json"
echo "   - n8n/workflows/intercom_workflow.json"
echo "   - n8n/workflows/unified_workflow.json"
echo ""
echo "[5/5] Upload Mock Data:"
echo ""
echo "1. In n8n, click 'Files' in the sidebar"
echo "2. Upload all CSV files from: n8n/mock_data/"
echo "   - zendesk_mock.csv"
echo "   - salesforce_mock.csv"
echo "   - nps_mock.csv"
echo "   - app_store_mock.csv"
echo ""
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "Next Steps:"
echo "1. Open n8n: http://localhost:5678"
echo "2. Import workflows (see instructions above)"
echo "3. Upload mock data files"
echo "4. Configure workflows with your backend URL"
echo "5. Execute workflows to test!"
echo ""
echo "For detailed instructions, see: n8n/SETUP_GUIDE.md"
echo ""







