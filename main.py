import os
from src.ui import run_app
from src.client import client

def main():
    # Ensure client is initialized (auth test runs on import)
    print("Starting application...")
    run_app()

if __name__ == "__main__":
    main()