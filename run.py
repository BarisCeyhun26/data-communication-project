import subprocess
import sys
import time
import webbrowser

def main():
    print("Launching Socket Programming Web Interface...")
    
    python_exe = sys.executable
    script = "web_app.py"
    url = "http://localhost:8080"
    
    print(f"Starting {script}...")
    try:
        # Start Flask App
        p = subprocess.Popen([python_exe, script])
        
        # Wait for Flask to start
        print("Waiting for server to start...")
        time.sleep(2)
        
        # Open Browser
        print(f"Opening {url} in your browser...")
        webbrowser.open(url)
        
        print("\nWeb Interface is running!")
        print("Press Ctrl+C in this terminal to stop the server.")
        
        p.wait()
        
    except KeyboardInterrupt:
        print("\nStopping server...")
        p.terminate()
        print("Done.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
