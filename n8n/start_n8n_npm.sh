#!/bin/bash

echo "========================================"
echo "Starting n8n (No Docker Required)"
echo "========================================"
echo ""
echo "n8n will start at: http://localhost:5678"
echo ""
echo "Keep this terminal open while using n8n."
echo "Press Ctrl+C to stop."
echo ""
echo "========================================"
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js is not installed!"
    echo "Please install Node.js from https://nodejs.org/"
    exit 1
fi

# Start n8n using npx (downloads automatically if needed)
npx -y n8n







