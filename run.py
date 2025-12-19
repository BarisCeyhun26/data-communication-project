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
        p = subprocess.Popen([python_exe, script])
        
        print("Waiting for server to start...")
        time.sleep(2)
        
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
