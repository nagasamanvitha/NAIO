#!/bin/bash

echo "Starting n8n..."
echo ""
echo "n8n will be available at: http://localhost:5678"
echo ""
echo "Press Ctrl+C to stop n8n"
echo ""

docker run -it --rm --name n8n -p 5678:5678 -v n8n_data:/home/node/.n8n n8nio/n8n







