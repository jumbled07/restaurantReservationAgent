import subprocess
import sys
import os
from threading import Thread

def run_backend():
    print("Starting FastAPI backend...")
    subprocess.run([
        sys.executable, "-m", "uvicorn",
        "app.backend.main:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--reload"
    ])

def run_frontend():
    print("Starting Streamlit frontend...")
    subprocess.run([
        sys.executable, "-m", "streamlit",
        "run", "app/frontend/main.py",
        "--server.port", "8501"
    ])

def main():
    # Create necessary directories if they don't exist
    os.makedirs("app/frontend", exist_ok=True)
    os.makedirs("app/backend", exist_ok=True)
    os.makedirs("app/agent", exist_ok=True)
    os.makedirs("app/models", exist_ok=True)
    os.makedirs("app/scripts", exist_ok=True)
    
    # Start backend and frontend in separate threads
    backend_thread = Thread(target=run_backend)
    frontend_thread = Thread(target=run_frontend)
    
    backend_thread.start()
    frontend_thread.start()
    
    try:
        backend_thread.join()
        frontend_thread.join()
    except KeyboardInterrupt:
        print("\nShutting down the application...")
        sys.exit(0)

if __name__ == "__main__":
    main() 