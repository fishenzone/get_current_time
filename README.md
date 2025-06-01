# LangGraph Time Bot

## How to Run (Linux)

```bash
# System-level setup (Python & Ollama)
sudo apt update
sudo apt install python3.11 python3.11-venv
curl -fsSL https://ollama.com/install.sh | sh

# Project setup (navigate to your project directory)
git clone https://github.com/fishenzone/get_current_time.git

# Pull Ollama model (ensure `ollama serve` is running or starts automatically)
ollama pull qwen3:30b-a3b

# Python environment setup
python3.11 -m venv .venv
source .venv/bin/activate

# Install Python dependencies
python -m pip install -r requirements.txt
python -m pip install -U "langgraph-cli[inmem]"
python -m pip install -e .

# Run services (each command in a separate terminal)
# Terminal 1: Start Ollama server
ollama serve

# Terminal 2: Start LangGraph frontend
python frontend.py
# Access the UI at: http://localhost:8011/
# You can also access http://172.208.114.221:8011/

# Terminal 3 (Optional): Start LangGraph Studio UI (for visualization)
langgraph dev
# Access UI at: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024