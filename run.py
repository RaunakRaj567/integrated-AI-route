"""
===============================================================================
AGRI-LOGISTICS PORTAL — SINGLE COMMAND LAUNCHER
===============================================================================
File Path: run.py

Why this file exists:
---------------------
Launches both the FastAPI backend (http://127.0.0.1:8000) and Vite React 
frontend (http://localhost:5173) simultaneously in parallel subprocesses.
Handles clean shutdown on Ctrl+C.
===============================================================================
"""

import subprocess
import sys
import os
import time
import io

# Ensure UTF-8 output encoding for Windows PowerShell / CMD console
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(ROOT_DIR, "frontend")


def main():
    print("=" * 70)
    print("      AGRI-LOGISTICS AI PROFIT & CVRP PORTAL LAUNCHER")
    print("=" * 70)
    print(f"  • Root Directory    : {ROOT_DIR}")
    print(f"  • Frontend Directory: {FRONTEND_DIR}")
    print("-" * 70)

    # 1. Start FastAPI Backend (Uvicorn)
    backend_cmd = [
        sys.executable, "-m", "uvicorn", "backend.main:app",
        "--host", "127.0.0.1",
        "--port", "8000",
        "--reload"
    ]
    print("[1/2] Launching FastAPI Backend on http://127.0.0.1:8000 ...")
    backend_process = subprocess.Popen(
        backend_cmd,
        cwd=ROOT_DIR
    )

    # Allow backend 1.5 seconds to initialize
    time.sleep(1.5)

    # 2. Start Vite React Frontend
    npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
    frontend_cmd = [npm_cmd, "run", "dev"]
    print("[2/2] Launching React Frontend on http://localhost:5173 ...")
    frontend_process = subprocess.Popen(
        frontend_cmd,
        cwd=FRONTEND_DIR
    )

    print("=" * 70)
    print("   🚀 ALL SERVICES RUNNING SUCCESSFULLY!")
    print("   • React Dashboard : http://localhost:5173")
    print("   • FastAPI Backend : http://127.0.0.1:8000")
    print("   • API Swagger Docs: http://127.0.0.1:8000/docs")
    print("=" * 70)
    print("Press Ctrl+C in this window to stop both servers cleanly.\n")

    # Auto-launch the browser
    import webbrowser
    time.sleep(2)
    print("[INFO] Auto-launching browser...")
    webbrowser.open("http://localhost:5173")

    try:
        while True:
            time.sleep(1)
            if backend_process.poll() is not None or frontend_process.poll() is not None:
                break
    except KeyboardInterrupt:
        print("\n[STOPPING] Shutting down servers...")
    finally:
        print("• Stopping FastAPI backend...")
        backend_process.terminate()
        print("• Stopping React frontend...")
        frontend_process.terminate()
        print("✓ Done. Servers stopped cleanly.")


if __name__ == "__main__":
    main()
