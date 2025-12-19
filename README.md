# Data Communication Project - Error Detection & Correction Simulation

This project demonstrates **Data Transmission with Error Detection Methods** using Python Socket Programming. It simulates a complete communication channel involving a Sender, an Intermediate Node (Error Injector), and a Receiver.

It features a **Web Interface (Flask)** for easy interaction and visualization.

## 🚀 Features

### 1. Error Detection Methods
The Sender can generate control information using:
-   **Parity Bit** (Odd/Even)
-   **2D Parity** (Matrix Parity)
-   **CRC** (Cyclic Redundancy Check)
-   **Hamming Code** (Single Bit Error Correction)
-   **Internet Checksum**

### 2. Error Injection (The Man-in-the-Middle)
The Server acts as an intermediate node that randomly corrupts data before forwarding it to the receiver:
-   **Bit Flip**
-   **Character Substitution**
-   **Character Deletion**
-   **Random Insertion**
-   **Burst Error**

### 3. Real-time Verification
The Receiver validates the incoming data against the control information and displays:
-   **DATA CORRECT** ✅
-   **DATA CORRUPTED** ❌

---

## 🛠️ Components

1.  **Client 1 (Sender):** Generates packets in `DATA|METHOD|CONTROL` format.
2.  **Server (Corruptor):** Intercepts packets on Port 8000, optionally corrupts them, and forwards to Port 9000.
3.  **Client 2 (Receiver):** Listens on Port 9000, recalculates checksums, and verifies integrity.
4.  **Web Dashboard:** A unified Flask-based UI to control all components.

---

## 📦 Requirements

-   Python 3.x
-   Flask

```bash
pip install flask
```

## ▶️ How to Run

1.  Clone the repository:
    ```bash
    git clone https://github.com/BarisCeyhun26/data-communication-project.git
    cd data-communication-project
    ```

2.  Run the launcher script:
    ```bash
    python3 run.py
    ```
    *This will automatically launch the Web Interface in your default browser.*

3.  **Use the Dashboard:**
    -   **Start Receiver:** Click "Start Listening".
    -   **Start Server:** Click "Start Server".
    -   **Send Data:** Enter text, select a method, and click "SEND PACKET".
    -   **Observe:** Watch the logs to see how data travels and if it gets corrupted!

---

## 📂 Project Structure

-   `run.py`: Launcher script.
-   `web_app.py`: Main Flask application (Web GUI).
-   `client1_sender.py`: Logic for encoding and calculation methods.
-   `server_corruptor.py`: Logic for error injection.
-   `client2_receiver.py`: Logic for decoding and verification.

---

## 👨‍💻 License

This project is open-source and available for educational purposes.
