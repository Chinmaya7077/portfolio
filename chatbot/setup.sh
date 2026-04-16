#!/bin/bash
# ============================================
# Portfolio AI Chatbot - Setup Script
# ============================================

set -e

echo "=================================="
echo " Portfolio AI Chatbot Setup"
echo "=================================="

# Step 1: Python virtual environment
echo ""
echo "[1/5] Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Step 2: Install dependencies
echo "[2/5] Installing Python dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo "      Dependencies installed."

# Step 3: Check Ollama
echo "[3/5] Checking Ollama..."
if command -v ollama &> /dev/null; then
    echo "      Ollama found."
    if ollama list 2>/dev/null | grep -q "mistral"; then
        echo "      Model 'mistral' is available."
    else
        echo "      Pulling 'mistral' model (this may take a few minutes)..."
        ollama pull mistral
    fi
else
    echo "      WARNING: Ollama not found!"
    echo "      Install it: curl -fsSL https://ollama.ai/install.sh | sh"
    echo "      Then run: ollama pull mistral"
fi

# Step 4: Run data ingestion
echo "[4/5] Running data ingestion..."
python ingest.py

# Step 5: Done
echo ""
echo "[5/5] Setup complete!"
echo ""
echo "=================================="
echo " To start the server:"
echo "   source venv/bin/activate"
echo "   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo " API docs: http://localhost:8000/docs"
echo " Health:   http://localhost:8000/health"
echo "=================================="
